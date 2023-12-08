def compare_objects(obj_a, obj_b):
    if isinstance(obj_a, dict) and isinstance(obj_b, dict):
        print("dict",obj_a,obj_b)
        if len(obj_a) != len(obj_b):
            return False

        for key, value_a in obj_a.items():
            if key not in obj_b or not compare_objects(value_a, obj_b[key]):
                return False
        return True

    elif isinstance(obj_a, list) and isinstance(obj_b, list):
        print("list",obj_a,obj_b)
        if len(obj_a) != len(obj_b):
            return False
        if len(obj_a) == 0:
            return True
        if isinstance(obj_a[0], dict):
            obj_a = sorted(obj_a, key=lambda x: x['argument_name'])
            obj_b = sorted(obj_b, key=lambda x: x['argument_name'])
        else:
            obj_a = sorted(obj_a)
            obj_b = sorted(obj_b)
        for a, b in zip(obj_a, obj_b):
            if not compare_objects(a, b):
                return False
        return True

    else:
        return obj_a == obj_b

def processing_list(list):
  prev_outputs = [None] * len(list)
  for i, tool in enumerate(list):
    if(tool['arguments']):
      for arg in tool['arguments']:
          if (arg['argument_value']) and '$$PREV[' in arg['argument_value']:
              prev_idx = int(arg['argument_value'].split('$$PREV[')[1][0])
              arg['argument_value'] = prev_outputs[prev_idx]
    prev_outputs[i] = tool['tool_name']
  return list

list1 = [{'tool_name': 'works_list', 'arguments': [{'argument_name': 'issue.priority', 'argument_value': ['p2']}]}, {'tool_name': 'add_work_items_to_sprint', 'arguments': [{'argument_name': 'work_ids', 'argument_value': '$$PREV[0]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[1]'}]}, {'tool_name': 'get_sprint_id', 'arguments': []}]
list2 = [{'tool_name': 'get_sprint_id', 'arguments': []},{'tool_name': 'create_actionable_tasks_from_text', 'arguments': [{'argument_name': 'text', 'argument_value': 'MeetingTranscript'}]},{'tool_name': 'add_work_items_to_sprint', 'arguments': [{'argument_name': 'work_ids', 'argument_value': '$$PREV[1]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[0]'}]}]

def compare_lists_of_tools(list1, list2):
    list1 = processing_list(list1)
    list2 = processing_list(list2)
    map1 = {}
    map2 = {}
    for item in list1:
      map1[item['tool_name']] = item['arguments']
    for item in list2:
      map2[item['tool_name']] = item['arguments']
    print(map1)
    print(map2)
    return compare_objects(map1,map2)


if __name__=='__main__':
    list1 = [{'tool_name': 'works_list', 'arguments': [{'argument_name': 'issue.priority', 'argument_value': ['p2']}]}, {'tool_name': 'add_work_items_to_sprint', 'arguments': [{'argument_name': 'work_ids', 'argument_value': '$$PREV[0]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[1]'}]}, {'tool_name': 'get_sprint_id', 'arguments': []}]
    list2 = [{'tool_name': 'get_sprint_id', 'arguments': []},{'tool_name': 'create_actionable_tasks_from_text', 'arguments': [{'argument_name': 'text', 'argument_value': 'MeetingTranscript'}]},{'tool_name': 'add_work_items_to_sprint', 'arguments': [{'argument_name': 'work_ids', 'argument_value': '$$PREV[1]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[0]'}]}]
    lists_equal = compare_lists_of_tools(list1, list2)
    print("Are the lists equal?", lists_equal)