import configparser
from pymilvus import connections, utility
from pymilvus import Collection
import json
from .schema import *
import sys

def connectdb(MODEL:str):
    try:
        # connect to milvus
        
        cfp = configparser.RawConfigParser()
        cfp.read('config.ini')
        milvus_uri = cfp.get('example', 'uri')
        token = cfp.get('example', 'token')

        connections.connect("default",
                            uri=milvus_uri,
                            token=token)
        print(f"Connecting to DB: {milvus_uri}")

        # Check if the collection exists, else create collection
        collection_name = "devrev"+'_'+MODEL
        print(f"Connecting to collection if exists, else create collection: {collection_name}")
        check_collection = utility.has_collection(collection_name)

        if check_collection:
            collection = Collection(collection_name)
        else:
            if MODEL=='openai':
                collection = Collection(name=collection_name, schema=schema_openai)
                print(f"Schema: {schema_openai}")
            elif MODEL=='bert':
                collection = Collection(name=collection_name, schema=schema_bert)
                print(f"Schema: {schema_bert}")
            elif MODEL=='palm':
                collection = Collection(name=collection_name, schema=schema_palm)
                print(f"Schema: {schema_palm}")

        print("Success!")
        return collection
    except Exception as e:
        print(f"Something went wrong: {e}")
        return None

