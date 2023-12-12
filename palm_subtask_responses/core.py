import json
from json import tool
import logging
import os.path
from pathlib import Path
from collections import deque
from time import sleep
import google.generativeai as palm
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from function_embeddings.OpenAIHelpers import OpenAIWrapper
# from ..function_embeddings.OpenAIHelpers import OpenAIWrapper
logging.basicConfig(level=logging.DEBUG)
from openai import OpenAI

cwd = Path.cwd().joinpath("palm_subtask_responses", "etc")
logging.info(cwd)

SCOPES = ["https://www.googleapis.com/auth/generative-language.tuning"]


def load_creds(token_path="token.json", client_secret_path="client_secret.json"):
    """Converts `oauth-client-id.json` to a credential object.

    This function caches the generated tokens to minimize the use of the
    consent screen.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


creds = load_creds(
    token_path=cwd.joinpath("token.json"),
    client_secret_path=cwd.joinpath("ft_model_secret.json"),
)

# Configure PALM and fetch models
palm.configure(credentials=creds)

text_model = [
    m for m in palm.list_models() if "generateText" in m.supported_generation_methods
][0].name

argument_mapping_model = [
    m for m in palm.list_tuned_models() if "argumentmappingmodel" in m.name
][0].name

embeddings_model = [
    m for m in palm.list_models() if "embedText" in m.supported_generation_methods
][0].name

logging.info(f"Using text model: {text_model}")
logging.info(f"Using argument mapping model: {argument_mapping_model}")
logging.info(f"Using embeddings model: {embeddings_model}")

constants = json.load(open(cwd.joinpath("constants.json")))
tools = constants["tools"]
example_prompts = constants["examples"]


def generate_argument_descriptions(tools, look_in=None):
    """
    Invokes the LLM (One-time call) to generate argument descriptions for each tool
    and saves them in a json file.
    """
    arg_prompt = constants["argument_processing_prompt"]
    if look_in is not None and os.path.exists(look_in):
        arguments_description = json.load(open(look_in, "r"))
    else:
        for tool in tools:
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
        if look_in is not None:
            json.dump(arguments_description, open(look_in, "w"))
    return arguments_description


def get_tools_description(tools, argument_descriptions):
    """
    Generates a description of all tools and their arguments.
    """
    tools_description = ""
    for tool in tools:
        tools_description += (
            "\n" + f"{tool['function_name']}:{tool['description'].split('.')[0]}"
        )
        for argument in argument_descriptions[tool["function_name"]]:
            tools_description += " with args:"
            for arg, props in argument.items():
                tools_description += f"\n\t{arg}:{props['desc'].split('.')[0]}"
    return tools_description


def segement_task(task_statement: str):
    """
    Given a task statement, segments it into subtasks and performs coreference resolution
    """
    segmentation_prompt = constants["segmentation_prompt"]

    response = palm.generate_text(
        model=text_model,
        prompt=segmentation_prompt % task_statement,
        temperature=0,
        max_output_tokens=800,
    )

    return eval(response.result)


def get_tools_for_tasks(tasks, tools_description):
    """
    It takes a list of tasks and a description of all tools and their arguments
    and returns a list of tuples of the form (task, tool) where tool is the most
    relevant tool for the given task.

    (Invokes LLM)
    """
    output = []
    tool_getter_prompt = constants["tool_getter_prompt"]
    for task,tool_desc in zip(tasks,tools_description):
        response = palm.generate_text(
            model=text_model,
            prompt=tool_getter_prompt % (tool_desc, task),
            temperature=0,
            max_output_tokens=800,
        )
        result = response.result
        if result == "None":
            return []
        output.append((task, response.result))
    return output


def get_relevant_tools(tasks, tools, argument_descriptions):
    client = OpenAI(api_key = "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")
    model = OpenAIWrapper(client)
    tool_desc = []
    relevant_tools = {}
    for task in tasks:
        relevant_tools[task] = model.get_related_tools(task)
    
    for task in relevant_tools.keys():
        tool_desc.append(get_tools_description(relevant_tools[task], argument_descriptions))

    # tools_description = get_tools_description(tools, argument_descriptions)
    return get_tools_for_tasks(tasks, tool_desc)


class KnowledgeItem:
    description: str
    tool: str

    def __init__(self, description: str, tool: str, arg_mapping: tuple = None) -> None:
        self.description = description
        self.tool = tool
        if arg_mapping:
            self.arg_mapping = arg_mapping
        else:
            self.arg_mapping = ()

    def summarize(self) -> str:
        return self.description + ": " + self.tool

    def __str__(self) -> str:
        return f"Know <{self.description} from [{self.tool}]>"

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return str(self)


def get_base_knowledge(tools, arguments_description):
    """
    Returns a list of knowledge items for all tools that don't have any arguments.
    This is called the base knowledge as it is the starting point for the inference.
    """
    knowledge = []

    l = list(arguments_description.keys())

    for tool in arguments_description:
        if len(arguments_description[tool]) == 0:
            tool_names = [t["name"] for t in tools]
            index = tool_names.index(tool)
            tool_description = tools[index]["description"]
            knowledge.append(KnowledgeItem(tool_description, tool))

    return knowledge


def elaborate_args(args: list[dict]):
    response = ""
    primary_count = 0
    for arg in args:
        for name, props in arg.items():
            response += "\n- "
            response += f"{name} ({props['type']}): {props['desc']}"
            primary_count += 1
            if "allowed" in props.keys():
                response += f" allowing: {props['allowed']}"

    return response


def get_instruction_prompt(instruction, arguments_description, knowledge):
    directive = instruction[0]
    tool_to_be_used = instruction[1]

    tool_arguments = arguments_description[tool_to_be_used]

    prompt = "Solve the 'Directive' with the given 'Tool'. Use values in 'Past Actions' or the provided directive and map values to arguments in the Tool. In case of missing info return a directive to get the missing info required to get missing info."
    prompt += f"\nDirective:{directive}\nTool: {tool_to_be_used} with args:{elaborate_args(tool_arguments)}"

    prompt += "\nPast Actions:"
    for knowledge_item in knowledge[::-1]:
        prompt += f"\n- {knowledge_item.summarize()}"

    return prompt


def complete_task(instructions: deque, tools, arguments_description, max_iter=10):
    knowledge = get_base_knowledge(tools, arguments_description)

    total_input_len = 0
    total_output_len = 0
    steps = 0

    while len(instructions) > 0:
        sleep(0.25)
        if steps > max_iter:
            break

        steps += 1
        instruction = instructions[0]
        response = palm.generate_text(
            model=argument_mapping_model,
            prompt=get_instruction_prompt(
                instruction, arguments_description, knowledge
            ),
            temperature=0,
            max_output_tokens=800,
        )

        total_input_len += len(
            get_instruction_prompt(instruction, arguments_description, knowledge)
        )

        logging.debug(f"Input: {instruction}\nOutput: {response.result}")

        total_output_len += len(response.result)

        response = eval(response.result)

        if len(response.get("missing_action", "")) > 0:
            logging.debug(f"Missing action: {response['missing_action']}")

            tool_for_missing_action = get_relevant_tools(
                [response["missing_action"]], tools, arguments_description
            )

            logging.debug(f"Tool for missing action: {tool_for_missing_action}")

            if len(tool_for_missing_action) > 0:
                instructions.appendleft(
                    (response["missing_action"], tool_for_missing_action[0][1])
                )
        else:
            logging.debug(f"Result: {response.get('result', [])}")
            instructions.popleft()
            knowledge.append(
                KnowledgeItem(instruction[0], instruction[1], response["result"])
            )

    logging.debug(f"Total tokens: {total_input_len}")
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
                        value = f"$$PREV[{tool_ordering.index(v)}]"
            elif arg[1] in tool_ordering:
                value = f"$$PREV[{tool_ordering.index(arg[1])}]"

            solution_item["arguments"].append(
                {"argument_name": arg[0], "argument_value": value}
            )
        solution.append(solution_item)

    return solution


class InferenceV1:
    def __init__(self, tools, arg_cache=None):
        self.tools = tools
        self.argument_descriptions = generate_argument_descriptions(
            self.tools, look_in=arg_cache
        )

    def invoke_agent(self, query):
        task_segments = segement_task(query)

        logging.debug(f"Task segments: {task_segments}")
        task_and_tool = get_relevant_tools(
            task_segments, self.tools, self.argument_descriptions
        )

        logging.debug(f"Task and tool: {task_and_tool}")

        solution_knowledge = complete_task(
            deque(task_and_tool), self.tools, self.argument_descriptions
        )

        print("??????????????????????")
        for k_item in solution_knowledge:
            logging.debug(k_item)

        final_solution = topo_sort(solution_knowledge)

        return final_solution


if __name__ == "__main__":
    arg_cache = cwd.joinpath("refined_arguments_description.json")
    obj = InferenceV1(tools, arg_cache)
    examples = [
        "Summarize work items similar to don:core:dvrv-us-1:devo/0:issue/1",
        "What is the meaning of life?",
        "Prioritize my P0 issues and add them to the current sprint",
        "Summarize high severity tickets from the customer UltimateCustomer",
        "What are my all issues in the triage stage under part FEAT-123? Summarize them.",
        "List all high severity tickets coming in from slack from customer Cust123 and generate a summary of them.",
        "Given a customer meeting transcript T, create action items and add them to my current sprint",
        "Get all work items similar to TKT-123, summarize them, create issues from that summary, and prioritize them",
    ]

    # for example in examples:
    #     print(example)
    #     print(json.dumps(obj.invoke_agent(example), indent=2))
    #     print()
    
    response = obj.invoke_agent("Prioritize my P0 issues and add them to the current sprint")
    print(json.dumps(response, indent=2))
