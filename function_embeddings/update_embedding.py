# Get DB uri and api-key from config.ini file
# REQUIRED -> pymilvus=2.3.4

import time
import json
from .schema import *
from .connectdb import connectdb
from pymilvus import connections

def update_embedding(embedding_data:json)->None:
    try:
        model = embedding_data['model']
        collection = connectdb(model)

        func_id = embedding_data['name']
        func_desc = embedding_data['description']
        func_embeds = embedding_data['embedding']

        # begin
        t0 = time.time()
        entity = [[func_id],[model], [func_desc], [func_embeds]]
        ins_resp = collection.upsert(entity)
        ins_rt = time.time() - t0
        print(f"Succeed in update {round(ins_rt,4)} seconds!")

        print("Flushing...")
        start_flush = time.time()
        collection.flush()
        end_flush = time.time()
        print(f"Succeed in flush in {round(end_flush - start_flush, 4)} seconds!")

        
        if len(collection.indexes) == 0:
            # build index
            index_params = {"index_type": "AUTOINDEX", "metric_type": "COSINE", "params": {}}
            t0 = time.time()
            print("Building AutoIndex...")
            if model=='openai':
                collection.create_index(field_name=openai_embedding_field.name, index_params=index_params)
            elif model=='bert':
                collection.create_index(field_name=bert_embedding_field.name, index_params=index_params)
            elif model=='palm':
                collection.create_index(field_name=palm_embedding_field.name, index_params=index_params)

            t1 = time.time()
            print(f"Succeed in {round(t1-t0, 4)} seconds!")

        connections.disconnect("default")
    except Exception as e:
        print(f"Something went wrong: {e}")
    return
