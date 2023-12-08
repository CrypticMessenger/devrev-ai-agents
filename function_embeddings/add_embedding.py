# Get DB uri and api-key from config.ini file
# REQUIRED -> pymilvus=2.3.4

import time
import json
from .schema import *
from .connectdb import connectdb
from pymilvus import connections

def add_embedding(embedding_data:json)->None:

    try:
        model = embedding_data['model']
        collection = connectdb(model)

        func_id = embedding_data['name']
        func_desc = embedding_data['description']
        func_embeds = embedding_data['embedding']

        # begin
        t0 = time.time()
        entity = [[func_id],[model], [func_desc], [func_embeds]]
        ins_resp = collection.insert(entity)
        ins_rt = time.time() - t0
        print(f"Succeed in insert {round(ins_rt,4)} seconds!")

        print("Flushing...")
        start_flush = time.time()
        collection.flush()
        end_flush = time.time()
        print(f"Succeed in flush in {round(end_flush - start_flush, 4)} seconds!")
        connections.disconnect("default")
    except Exception as e:
        print(f"Something went wrong: {e}")
    return
