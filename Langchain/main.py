from customLangchain import Inference
from constants import template,all_tools

obj = Inference(template,all_tools)
response = obj.invoke_agent("Priortize my work items")

print(response)