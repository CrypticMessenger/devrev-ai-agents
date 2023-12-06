from openai import OpenAI
from collections import defaultdict
import json
import numpy as np
import tiktoken
import converter
import validate_training_jsonl
import constants

#####################
api_key = "your-api-key" 
input_csv = "dataset.csv"
output_jsonl = "output.jsonl"
starting_prompt = constants.template
#####################

# Convert the CSV file to JSONL
converter.csv_to_json(input_csv=input_csv, output_jsonl=output_jsonl, starting_prompt=starting_prompt)

# Validate the JSONL file
validate_training_jsonl.validate_training_jsonl(data_path=output_jsonl)

# fine-tune the model
# client = OpenAI(api_key=api_key)

# upload_response = client.files.create(
#     file=open(output_jsonl, "rb"),
#     purpose="fine-tune"
# )
# file_id = upload_response.id

# res = client.fine_tuning.jobs.create(
#   training_file=file_id, 
#   model="gpt-3.5-turbo", 
#   hyperparameters={
#     "n_epochs":epochs
#   }
# )

# print(res)
# job_id = res.id
# list_jobs = client.fine_tuning.jobs.list(limit=10)
# print(list_jobs)

# check_job = client.fine_tuning.jobs.retrieve(id=job_id)
# print(check_job)
# events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id, limit=10)
# print(events)
