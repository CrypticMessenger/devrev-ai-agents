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


llm = GooglePalm(temperature=0, google_api_key='AIzaSyAq9RCFh9Jx5t9oR20xWRAZdXsn-b01pT8')
# llm = OpenAI(temperature=0, openai_api_key='')


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
        # Check if agent should finish
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
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


class Inference:
    def __init__(self,prompt_template,all_tools_json):
        
        self.tools = create_tools(all_tools_json)

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

        self.agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=self.tools, verbose=False)

    def invoke_agent(self, input_question):
        print("Agent Invoked")
        print(f"Input Question: {input_question}")
        output = self.agent_executor.invoke({"input": input_question})
        return output['output']