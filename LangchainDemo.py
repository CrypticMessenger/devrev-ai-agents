from Langchain.customLangchain import Inference
from constants import template,all_tools
from Langchain.tools import *


query = "Retrieve work items in the ""In Progress"" stage owned by ""USER-456"" and ""USER-789"", summarize them, and prioritize by severity."
obj = Inference(template,create_tools(all_tools))
response,input_tokens,output_tokens = obj.invoke_agent(query)

print(f'Query: {query} \n Response: {response} \n input tokens: {input_tokens} \n output tokens: {output_tokens}')