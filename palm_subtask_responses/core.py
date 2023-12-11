from collections import deque
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import json
import google.generativeai as palm
import spacy

my_config = json.load(open("config.json"))

palm.configure(api_key=my_config["palm_api_key"])
text_model = [
    m for m in palm.list_models() if "generateText" in m.supported_generation_methods
][0].name
embeddings_model = [
    m for m in palm.list_models() if "embedText" in m.supported_generation_methods
][0].name

tools = json.load(open("tools.json"))
models = palm.list_models()
example_prompts = json.load(open("example_prompts.json"))["examples"]

SCOPES = ["https://www.googleapis.com/auth/generative-language.tuning"]


def load_creds():
    """Converts `oauth-client-id.json` to a credential object.

    This function caches the generated tokens to minimize the use of the
    consent screen.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret_56510766963.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def generate_argument_descriptions(tools, look_in="refined_arguments_description.json"):
    arg_prompt = json.load(open("prompts.json"))["argument_processing_prompt"]
    if os.path.exists("refined_arguments_description.json"):
        arguments_description = json.load(open(look_in, "r"))
    else:
        for tool in tools["tools"]:
            arguments_description[tool["name"]] = []
            for argument in tool.get("arguments", []):
                output = palm.generate_text(
                    model=text_model,
                    prompt=arg_prompt % argument,
                    temperature=0,
                    max_output_tokens=800,
                )
                arguments_description[tool["name"]].append(
                    {argument["name"]: eval(output.result)}
                )
        json.dump(arguments_description, open(look_in, "w"))
    return arguments_description


def get_tools_description(tools, argument_descriptions):
    tools_description = ""
    for tool in tools["tools"]:
        tools_description += (
            "\n" + f"{tool['name']}:{tool['description'].split('.')[0]}"
        )
        for argument in argument_descriptions[tool["name"]]:
            tools_description += " with args:"
            for arg, props in argument.items():
                tools_description += f"\n\t{arg}:{props['desc'].split('.')[0]}"
    return tools_description


def segement_task(task_statement: str):
    segmentation_prompt = json.load(open("prompts.json"))["segmentation_prompt"]

    response = palm.generate_text(
        model=text_model,
        prompt=segmentation_prompt % task_statement,
        temperature=0,
        max_output_tokens=800,
    )

    return eval(response.result)


def get_tools_for_tasks(tasks, tools_description):
    output = []
    tool_getter_prompt = json.load(open("prompts.json"))["tool_getter_prompt"]
    for task in tasks:
        response = palm.generate_text(
            model=text_model,
            prompt=tool_getter_prompt % (tools_description, task),
            temperature=0,
            max_output_tokens=800,
        )
        result = response.result
        if result == "None":
            return []
        output.append((task, response.result))
    return output


def get_relevant_tools(tasks, tools):
    tools_description = get_tools_description(
        tools,
        get_tools_description(
            tools,
            argument_descriptions=generate_argument_descriptions(
                tools, look_in="refined_arguments_description.json"
            ),
        ),
    )
    return get_tools_for_tasks(tasks, tools_description)


class KnowledgeItem:
    description: str
    tool: str

    def __init__(self, description: str, tool: str) -> None:
        self.description = description
        self.tool = tool

    def summarize(self) -> str:
        return self.description + ":" + self.tool

    def __str__(self) -> str:
        return f"Know <{self.description} from [{self.tool}]>"

    def __repr__(self) -> str:
        return str(self)


def get_base_knowledge(tools, arguments_description):
    knowledge = []

    for tool in arguments_description:
        if len(arguments_description[tool]) == 0:
            tool_names = [t["name"] for t in tools["tools"]]
            index = tool_names.index(tool)
            tool_description = tools["tools"][index]["description"].split("Returns ")[1]
            knowledge.append(KnowledgeItem(tool_description, tool))

    return knowledge


def elaborate_args(args: list[dict]):
    response = ""
    primary_count = 0
    for arg in args:
        for name, props in arg.items():
            response += "\n\t"
            if primary_count < 3:
                response += f"{name} ({props['type']}):{props['desc']}"
                primary_count += 1
            else:
                response += f"{name}:{props['desc']}"
            if "allowed" in props.keys():
                response += f" allowing: {props['allowed']}"

    return response


def get_instruction_prompt(instruction, arguments_description, knowledge):
    directive = instruction[0]
    tool_to_be_used = instruction[1]

    tool_arguments = arguments_description[tool_to_be_used]

    prompt = ""
    # prompt = f"give response for:\n"
    prompt += f"Directive:{directive}\nTool: {tool_to_be_used} with args:{elaborate_args(tool_arguments)}"

    prompt += "\nPast Actions/Knowledge:"
    for knowledge_item in knowledge[::-1]:
        prompt += f"\n\t{knowledge_item.summarize()}"

    prompt += "\nOutput:"

    return prompt


def complete_task(instructions: deque, tools, arguments_description):
    subtask_solution_prompt = json.load(open("prompts.json"))["subtask_solution_prompt"]

    knowledge = get_base_knowledge(tools, arguments_description)

    total_len = 0
    steps = 0

    while len(instructions) > 0:
        if steps > 6:
            break
        steps += 1
        instruction = instructions[0]
        response = palm.generate_text(
            model=text_model,
            prompt=subtask_solution_prompt
            + get_instruction_prompt(instruction, arguments_description, knowledge),
            temperature=0,
            # max_output_tokens=800,
        )
        print(f"Input: {instruction}\nOutput: {response.result}")
        response = eval(response.result)

        tokens = palm.count_text_tokens(
            model=text_model,
            prompt=subtask_solution_prompt
            + get_instruction_prompt(instruction, arguments_description, knowledge),
        )
        total_len += tokens["token_count"]

        if len(response["missing_action"]) > 0:
            print(f"Missing action: {response['missing_action']}")

            tool_for_missing_action = get_tools_for_tasks([response["missing_action"]])

            print(f"Tool for missing action: {tool_for_missing_action}")

            if len(tool_for_missing_action) > 0:
                instructions.appendleft(
                    (response["missing_action"], tool_for_missing_action[0][1])
                )
        else:
            print(f"Result: {response['result']}")
            instructions.popleft()
            knowledge.append(KnowledgeItem(instruction[0], instruction[1]))
        print()

    print(f"Total tokens: {total_len}")
    return knowledge


def topo_sort(knowledge: list[KnowledgeItem]) -> list:
    """Returns a topologically sorted list of knowledge items."""
    final_goal = knowledge[-1]
    for item in knowledge:
        neighbors = set()
        for arg in item.arg_mapping:
            # print(arg)
            if (
                isinstance(arg[1], list)
                or isinstance(arg[1], tuple)
                or isinstance(arg[1], set)
                or isinstance(arg[1], dict)
            ):
                nbs = [k_item for k_item in knowledge if k_item.tool in arg[1]]
                neighbors.update(nbs)
            else:
                nbs = [k_item for k_item in knowledge if k_item.tool == arg[1]]
                neighbors.update(nbs)
        item.neighbors = neighbors


    def topo_sort_util(k_item: KnowledgeItem, visited: set, stack: list):
        visited.add(k_item)
        for neighbor in k_item.neighbors:
            if neighbor not in visited:
                topo_sort_util(neighbor, visited, stack)
        stack.append(k_item)

    visited = set()
    stack = []

    topo_sort_util(final_goal, visited, stack)

    # stack = stack[::-1]
    solution = []
    for item in stack:
        tool_ordering = [k_item.tool for k_item in stack]
        solution_item = {}
        solution_item["tool_name"] = item.tool
        solution_item["arguments"] = []
        for arg in item.arg_mapping:
            value = arg[1]
            if (
                isinstance(arg[1], list)
                or isinstance(arg[1], tuple)
                or isinstance(arg[1], set)
                or isinstance(arg[1], dict)
            ):
                for v in arg[1]:
                    if v in tool_ordering:
                        value  = f"$$PREV[{tool_ordering.index(v)}]"
            elif arg[1] in tool_ordering:
                value = f"$$PREV[{tool_ordering.index(arg[1])}]"

            solution_item["arguments"].append({"argument_name": arg[0], "argument_value": value})
        solution.append(solution_item)
    
    return solution
