
"""# Define the evaluation method"""
from utils.OutputChecker import compare_lists_of_tools
from Langchain.customLangchain import Inference
from Langchain.tools import *
from constants import template,all_tools
import pandas as pd
import json
from ExperimentPipeline import ExperimentPipeline
from function_embeddings.get_all_tools import get_all_tools

def objective_similarity(list1,list2):
  return compare_lists_of_tools(list1,list2)

obj = Inference(template,create_tools(all_tools))
# Define Inference Function
def inference_function(query):
    response = obj.invoke_agent(query)
    return response

def process_output(input_string) :
  try :
    input_string = input_string.strip()
    output_map = json.loads(input_string)
    return output_map
  except :
    return {}



# Get inference

original_df = pd.read_csv("Data/Testing dataset.csv")
original_df['expected_output'] = original_df['Output'].apply(process_output)
original_df.drop('Output',axis=1,inplace=True)

df = original_df.sample(n=5, random_state=35)
df = df.reset_index(drop=True)



result_map = df.set_index('Query')['expected_output'].to_dict()

queries_with_empty_map = [query for query, value in result_map.items() if value == {}]

if queries_with_empty_map:
    print("Queries with an empty map as value:")
    for query in queries_with_empty_map:
        print(query)
else:
    print("No queries with an empty map as value found.")

EXP_DIR = "Results/Langchain"


experiment = ExperimentPipeline(inference_function,result_map, objective_similarity, EXP_DIR, df)
experiment.run_experiment(save_results=True)