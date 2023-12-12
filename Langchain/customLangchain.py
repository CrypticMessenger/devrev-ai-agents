from typing import List, Union
import re

from langchain.agents import (
    AgentType,
    initialize_agent,
    AgentExecutor,
    Tool,
    AgentOutputParser,
    LLMSingleActionAgent,
)
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.llms import OpenAI
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain.tools import tool
from langchain import hub
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain.llms import GooglePalm


# import tools.py functions from directory
from .tools import *

def estimate_tokens(text):
    # Split text into tokens (considering words as tokens here)
    return len(text)/8


llm = GooglePalm(temperature=0, google_api_key='AIzaSyAq9RCFh9Jx5t9oR20xWRAZdXsn-b01pT8')
# llm = OpenAI(temperature=0, openai_api_key='')

input_tokens = 0
output_tokens = 0

class CustomOutputParser(AgentOutputParser):
    def create_map(self,ans):
        final_ans = []
        lines = ans.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('"tool_name"'):
                tool_name = line.split(":")[1].strip().strip('"')
                i=i+1
                tool_info = {}
                tool_info['tool_name'] = tool_name
                arguments = []
                while i<len(lines):
                    if lines[i].startswith('"tool_name"'):
                        break
                    else:
                        argument_name = lines[i].split(":")[1].strip().strip('"')
                        # split next line by '":' and then strip the spaces and " from the argument value
                        argument_value = lines[i+1].split('":')[1].strip().strip('"')
                        arguments.append({"argument_name": argument_name, "argument_value":argument_value})
                        i=i+2
                tool_info['arguments']=arguments
                final_ans.append(tool_info)
            else:
                i=i+1
        return final_ans




    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # print("llm_output: ",llm_output)
        # Check if agent should finish
        global output_tokens
        output_tokens+= estimate_tokens(llm_output)
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": self.create_map(llm_output.split("Final Answer:")[-1].strip())},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

def extract_function_names(text):
    # Define the pattern to find function names
    text = f'{text}'
    pattern = r"function_name is ([\w\s-]+)\."
    # Find all matches using regex
    matches = re.findall(pattern, text) 
    return matches
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        total_steps = len(intermediate_steps)
        idx = 0
        for action, observation in intermediate_steps:
            thoughts += action.log
            if idx < total_steps-3:
                if len(extract_function_names(observation))!=0:
                    thoughts+= f"\nObservation: {extract_function_names(observation)}\nThought: "
                    continue
            thoughts += f"\nObservation: {observation}\nThought: "
            idx+=1

        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided

        final_template = self.template.format(**kwargs)
        global input_tokens
        input_tokens+= estimate_tokens(final_template)
        return final_template


class Inference:
    def __init__(self,prompt_template,all_tools):
        
        self.tools = all_tools

        self.prompt = CustomPromptTemplate(
            template=prompt_template,
            tools=self.tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because that is needed
            input_variables=["input", "intermediate_steps"]
        )

        self.output_parser = CustomOutputParser()
        self.llm_chain = LLMChain(llm=llm, prompt=self.prompt)

        self.tool_names = [tool.name for tool in self.tools]
        agent = LLMSingleActionAgent(
            llm_chain=self.llm_chain,
            output_parser=self.output_parser,
            stop=["\nObservation:"],
            allowed_tools=self.tool_names
        )

        self.agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=self.tools, verbose=True,max_iterations=5000)

    def invoke_agent(self, input_question):
        global input_tokens
        global output_tokens
        input_tokens = 0
        output_tokens = 0
        print("Agent Invoked")
        print(f"Input Question: {input_question}")
        output = self.agent_executor.invoke({"input": input_question})
        return output['output'],input_tokens,output_tokens