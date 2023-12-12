from .connectdb import connectdb, disconnectdb

def get_all_tools(model:str,output_fields=['function_name', 'description', 'embedding', 'examples','arguments'])->list:
    try:
        # connect to db
        collection = connectdb(model)
        collection.load()
        # get all tools
        res = collection.query(
            expr = 'function_name>""', #get all entries to true, to get all functions
            output_fields = output_fields,
            limit=10000
        )
        collection.release()
        # disconnect from db
        disconnectdb()
        # return all tools
        return res
    except Exception as e:
        print(f"Something went wrong in function_embeddings/toolOperations.py -> get_all_tools function: {e}")
        return None
    
def search_tool(model:str, tool_name:str, output_fields=['function_name', 'description', 'embedding', 'examples','arguments'])->list:
    try:
        # connect to db
        collection = connectdb(model)
        collection.load()
        # get all tools
        res = collection.query(
            expr = f'function_name=="{tool_name}"',
            output_fields = output_fields,
            limit=10
        )
        collection.release()
        # disconnect from db
        disconnectdb()
        # return all tools
        return res
    except Exception as e:
        print(f"Something went wrong in function_embeddings/toolOperations.py -> search_tool function: {e}")
        return None