import argparse
import json
from function_embeddings.toolOperations import get_all_tools,search_tool
from constants import PALM_EXAMPLES_TEMPLATES, PALM_CONTEXT
from openai import OpenAI
from function_embeddings.OpenAIHelpers import OpenAIWrapper
import google.generativeai as palm
from function_embeddings.PalmHelpers import PalmWrapper

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A simple command-line program.")

    # Add a subparser for the 'getAllTools' command
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Subparser for 'getAllTools'
    parser_get_all_tools = subparsers.add_parser('getAllTools', help='Fetch all tools')
    parser_get_all_tools.add_argument('--model', choices=['openai', 'palm'], help='give model Name', required=False, default='openai')
    parser_get_all_tools.add_argument('--showDescription', action='store_true', help='show tool names with description', required=False)

    # Subparser for 'searchTool'
    parser_search_tool = subparsers.add_parser('searchTool', help='Search tool')
    parser_search_tool.add_argument('--toolName', help='give tool name', required=True)
    parser_search_tool.add_argument('--model', choices=['openai', 'palm'], help='give model Name', required=False, default='openai')

    #Subparser for 'addTool'
    parser_add_tool = subparsers.add_parser('addTool', help='Add tool given in a file in JSON format')
    parser_add_tool.add_argument('--fileName', help='give json file name to import tool information from', required=True)
    parser_add_tool.add_argument('--model', choices=['openai', 'palm'], help='give model Name', required=False, default='openai')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Your logic based on the provided command
    if args.command == "getAllTools":
        # Call the function with the provided arguments
        r = get_all_tools(args.model)
       
        for i, tool in enumerate(r):
            if args.showDescription:
                print(f"{i + 1}. {tool['function_name']}: {tool['description']}")
            else:
                print(f"{i + 1}. {tool['function_name']}")
    elif args.command == "searchTool":
        r = search_tool(args.model, args.toolName)
        if(len(r)==0):
            print("No tool found with the given name")
        else:
            print(f"Tool found: {r[0]['function_name']}")
            print(f"Description: {r[0]['description']}")
            print(f"Arguments:")
            for i,argument in enumerate(r[0]['arguments']):
                print(f"\t{i+1}. {argument['name']}: {argument['description']}\n")
            print(f"Examples: ")
            print(r[0]['examples'])
    
    elif args.command == "addTool":
        json_file_path = args.fileName
        try:
            with open(json_file_path, 'r') as json_file:
                tool = json.load(json_file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("The file should contain only one valid JSON object.")
            return
        except FileNotFoundError:
            print(f"Error: File not found - {json_file_path}")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return
        print(f"Adding tool from file: {args.fileName} to model: {args.model}")
        if(args.model == 'openai'):
            client = OpenAI(api_key = "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")
            model = OpenAIWrapper(client)
            tool_name = tool['name']
        
            if(len(search_tool(args.model, tool_name))>0):
                print(f"Tool with name {tool_name} already exists")
            else:
                function_description_openai = model.generate_function_description(tool)
                function_examples = model.generate_examples(function_description_openai,10)
                function_arguments = ""
                if 'arguments' in tool:
                    function_arguments = tool['arguments']
                rich_desc  = f"Function name is {tool['name']}.{function_description_openai}. Arguments = {function_arguments} Examples = {function_examples}"
                function_info = {
                    'function_name': tool['name'],
                    'description': function_description_openai,
                    'examples': function_examples,
                    'arguments': function_arguments
                }
                model.add_functionDB(function_info['function_name'],function_info['description'],function_info['examples'],function_info['arguments'])
        elif args.model == 'palm':
            palm.configure(api_key="api-key-using-console-google")
            model = PalmWrapper(palm,example_template=PALM_EXAMPLES_TEMPLATES, palm_context = PALM_CONTEXT)
            tool_name = tool['name']
        
            if(len(search_tool(args.model, tool_name))>0):
                print(f"Tool with name {tool_name} already exists")
            else:
                function_description_palm = model.create_description(tool)
                function_examples = model.generate_examples(function_description=function_description_palm,number_of_examples=3)
                if 'arguments' in tool:
                    function_arguments = tool['arguments']
                rich_desc  = f"Function name is {tool['name']}.{function_description_palm}. Arguments = {function_arguments} Examples = {function_examples}"
                function_info = {
                    'function_name': tool['name'],
                    'description': function_description_palm,
                    'examples': function_examples,
                    'arguments': function_arguments
                }
                model.add_functionDB(function_info['function_name'],function_info['description'],function_info['examples'],function_info['arguments'])
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
