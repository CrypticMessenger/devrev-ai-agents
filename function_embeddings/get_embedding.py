# Get DB uri and api-key from config.ini file
# REQUIRED -> pymilvus=2.3.4

import time
import json
from .schema import *
from pymilvus import connections
from .connectdb import connectdb

def load_db(collection)->None:
    try:
        # load collection
        t0 = time.time()
        print("Loading collection...")
        collection.load()
        t1 = time.time()
        print(f"Succeed in {round(t1-t0, 4)} seconds!")
    except Exception as e:
        print("Something went wrong in function function_embeddings/get_embedding.py -> load_db function: {e}")

    return

def search_similar(embedding_data:json,model:str, metric_type="COSINE", topk=5, level=2)->list:
    try:
        search_params = {"metric_type": metric_type,  "params": {"level": level}}
        topk = topk

        collection = connectdb(model)

        # load db
        load_db(collection)

        # define search vector
        search_vec = [embedding_data]

        if model=='openai':
            # search_vec = [[random.random() for _ in range(dim_openai)]]
            anns_field = openai_embedding_field.name
        elif model=='bert':
            # search_vec = [[random.random() for _ in range(dim_bert)]]
            anns_field = bert_embedding_field.name
        elif model=='palm':
            # search_vec = [[random.random() for _ in range(dim_palm)]]
            anns_field = palm_embedding_field.name

        print(f"Searching vector: {search_vec}")
        t0 = time.time()

        results = collection.search(search_vec,
                                anns_field=anns_field,
                                param=search_params,
                                limit=topk,
                                guarantee_timestamp=1,
                                output_fields=['function_name', 'description', 'embedding', 'examples','arguments']
                                )
        t1 = time.time()
        print(f"Result:{results}")
        print(f"Search latency: {round(t1-t0, 4)} seconds!")
        
        collection.release()
        connections.disconnect("default")

        return results
    except Exception as e:
        print("Something went wrong in function function_embeddings/get_embedding.py -> search_similar function: {e}")