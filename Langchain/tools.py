
from langchain.agents import AgentType, initialize_agent, AgentExecutor,Tool, AgentOutputParser, LLMSingleActionAgent

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

        print(function_template)
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

    def query_user(llm_input):
        user_input = input(llm_input)
        return user_input


    # user_query_tool = Tool(
    #     name = "query_user",
    #     func = query_user,
    #     description = "Use this function to ask user for more some clarification"
    # )

    # tools = tools + [user_query_tool]

    print("Tools created")
    return tools