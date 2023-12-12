"""# Define the evaluation method"""
from palm_subtask_responses.core import InferenceV1
from constants import all_tools_regular
import json


query = (
    "Retrieve work items in the 'In Progress' stage owned by " +
    "USER-456  and USER-789 summarize them, and prioritize by severity."
)

# Please delete arg_dec_cache if you change the tools
inference = InferenceV1(all_tools_regular["tools"], "arg_desc_cache.json")
response, input_tokens, output_tokens = inference.invoke_agent(query)

print(f"Query: {query}")
print(
    f"Response: \n{json.dumps(response, indent=2)} \n input tokens: {input_tokens} \n output tokens: {output_tokens}"
)
