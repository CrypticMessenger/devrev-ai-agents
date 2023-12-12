"""# Define the evaluation method"""
from palm_subtask_responses.core import InferenceV1
from constants import all_tools_regular
import json
from function_embeddings.get_all_tools import get_all_tools

results = get_all_tools('openai')
all_tools = {}
tools = []

for item in results:
      function_info = {
        'name': item['function_name'],
        'description': item['description'],
        'arguments': item['arguments']
      }
      tools.append(function_info)

query = (
    "Retrieve work items in the 'In Progress' stage owned by " +
    "USER-456  and USER-789 summarize them, and prioritize by severity."
)

# Please delete arg_dec_cache if you change the tools
inference = InferenceV1(tools, "arg_desc_cache.json")
response, input_tokens, output_tokens = inference.invoke_agent(query)

print(f"Query: {query}")
print(
    f"Response: \n{json.dumps(response, indent=2)} \n input tokens: {input_tokens} \n output tokens: {output_tokens}"
)
