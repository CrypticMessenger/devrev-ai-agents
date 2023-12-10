
from langchain.agents import AgentType, initialize_agent, AgentExecutor,Tool, AgentOutputParser, LLMSingleActionAgent
from function_embeddings.OpenAIHelpers import OpenAIWrapper

from openai import OpenAI

def generate_functions(data):
    all_tool_functions = []
    for tool in data['tools']:
        # Generate function signature
#         @tool('{tool['name']}', handle_tool_error=True)
        function_template = f"def {tool['name']}("

        if 'arguments' in tool:
            arguments = tool['arguments']
            for arg in arguments:
                function_template += f"{arg['name']}=None, "
            function_template = function_template[:-2]  # Remove the trailing comma
        else:
            function_template+= "dummy=None"
        function_template += "):"

        # Generate function description
        function_template += f'\n    """{tool["description"]}"""\n    return "No error. Proceed to next step."'

        # Execute the code in a new namespace
        local_namespace = {}
        exec(function_template, globals(), local_namespace)
        # Create a function object and assign it to the global namespace
        generated_function = local_namespace[tool['name']]
        globals()[tool['name']] = generated_function
        all_tool_functions.append(generated_function)
    return all_tool_functions

def create_tools(tools_json):
    
    print("Creating Tools")
    tools_functions = generate_functions(tools_json)
    tools = []

    def create_description(tool_json):
        desc=tool_json['description']+" the function take the following arguments - "
        try:
            for args in tool_json['arguments']:
                desc+= f"[argument name - {args['name']}, description = {args['description']}, type = {args['type']}]"
        except:
            pass
        return desc


    for i in range(len(tools_json['tools'])):
        tool_instance = tools_json['tools'][i]

        tool = Tool(
            name=tool_instance['name'],
            func=tools_functions[i],
            description=create_description(tool_instance)
        )
        tools.append(tool)

    def get_related_tools_function(query):
        client = OpenAI(api_key = "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")
        model = OpenAIWrapper(client)
        return model.get_related_tools(query)[:3]

    def get_tool_arguments_function(tool_name):
        for i in range(len(tools_json['tools'])):
            if tools_json['tools'][i]['name'] in tool_name:
                return f"{tools_json['tools'][i]['arguments']}"
        return "what?"
        


    get_related_tools = Tool(
        name = "get_related_tools",
        func = get_related_tools_function,
        description = "Use this function to find related tool for the query"
    )

    get_tool_arguments = Tool(
        name = "get_tool_arguments",
        func = get_tool_arguments_function,
        description = "Use this function to find tool arguments"
    )

    tools = tools + [get_related_tools,get_tool_arguments]

    print("Tools created")
    return tools