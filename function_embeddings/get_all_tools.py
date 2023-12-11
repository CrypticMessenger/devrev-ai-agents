from .connectdb import connectdb, disconnectdb

def get_all_tools(model:str)->list:
    try:
        # connect to db
        collection = connectdb(model)
        # get all tools
        res = collection.query(
            expr = 'function_name>" "', #get all entries to true, to get all functions
            output_fields = ['function_name', 'description', 'embedding', 'examples','arguments'],
            limit=10000
        )
        # disconnect from db
        disconnectdb()
        # return all tools
        return res
    except Exception as e:
        print(f"Something went wrong: {e}")
        return None