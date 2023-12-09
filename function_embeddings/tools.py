def create_description(tool_json):
        desc=f"Function Name is {tool_json['name']}. Description:{tool_json['description']} "
        try:
            for args in tool_json['arguments']:
                desc+= f"[argument name - {args['name']}, description = {args['description']}]"
        except:
            pass
        return desc

def create_description_with_example(function_description,examples=""):
  function_description+=f"Examples - {examples}"
  return function_description