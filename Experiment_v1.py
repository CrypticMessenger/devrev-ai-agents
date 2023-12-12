
"""# Define the evaluation method"""
from palm_subtask_responses.core import InferenceV1
from utils.OutputChecker import compare_lists_of_tools
from constants import all_tools_regular
import pandas as pd
import json
from ExperimentPipeline import ExperimentPipeline

inference = InferenceV1(all_tools_regular["tools"], "hello.json")

def objective_similarity(list1,list2):
  return compare_lists_of_tools(list1,list2)

# Define Inference Function
def inference_function(query):
    print(query)
    obj = inference
    response = obj.invoke_agent(query)
    print(response)
    return response

def process_output(input_string) :
  try :
    input_string = input_string.strip()
    output_map = json.loads(input_string)
    return output_map
  except :
    return {}



# Get inference

original_df = pd.read_csv("Data/test_v0.csv")
original_df['expected_output'] = original_df['Output'].apply(process_output)
original_df.drop('Output',axis=1,inplace=True)

df = original_df.sample(n=10, random_state=35)
df = df.reset_index(drop=True)



result_map = df.set_index('Query')['expected_output'].to_dict()

queries_with_empty_map = [query for query, value in result_map.items() if value == {}]

if queries_with_empty_map:
    print("Queries with an empty map as value:")
    for query in queries_with_empty_map:
        print(query)
else:
    print("No queries with an empty map as value found.")

EXP_DIR = "Results/PalmSeg"


experiment = ExperimentPipeline(inference_function,result_map, objective_similarity, EXP_DIR, df)
experiment.run_experiment(save_results=True)