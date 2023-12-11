
"""# Define the evaluation method"""
from utils.OutputChecker import compare_lists_of_tools
import pandas as pd
import json
from ExperimentPipeline import ExperimentPipeline
from constants import all_tools
from core import *

def objective_similarity(list1,list2):
  return compare_lists_of_tools(list1,list2)


# Define Inference Function
def inference_function(query):
    task_segments = segement_task(query)

    task_and_tool = get_relevant_tools(task_segments, all_tools)

    argument_descriptions = generate_argument_descriptions(all_tools, look_in = "refined_arguments_description.json")

    solution_knowledge = complete_task(task_and_tool, argument_descriptions)

    final_solution = topo_sort(solution_knowledge)

    return json.dumps(final_solution)

def process_output(input_string) :
  try :
    input_string = input_string.strip()
    output_map = json.loads(input_string)
    return output_map
  except :
    return {}



# Get inference

original_df = pd.read_csv("/Users/ambrose_/Desktop/Inter-IIT-agents/agent007/devrev-ai-agents/Data/test_v0.csv")
df = original_df.sample(n=1, random_state=36)
df = df.reset_index(drop=True)

df['Output_map'] = df['Output'].apply(process_output)
result_map = df.set_index('Query')['Output_map'].to_dict()
result_map

queries_with_empty_map = [query for query, value in result_map.items() if value == {}]

if queries_with_empty_map:
    print("Queries with an empty map as value:")
    for query in queries_with_empty_map:
        print(query)
else:
    print("No queries with an empty map as value found.")

EXP_DIR = '/Users/ambrose_/Desktop/Inter-IIT-agents/agent007/devrev-ai-agents/Results'

inference_args = {
    "alpha": [0.1],
    "beta": ["gpt-3.5"]
}

experiment = ExperimentPipeline(inference_function, inference_args, result_map, objective_similarity, EXP_DIR, df)
experiment.run_experiment(save_results=True)