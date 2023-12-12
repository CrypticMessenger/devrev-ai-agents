import json
import copy

def compare_objects(obj_a, obj_b):
    if isinstance(obj_a, dict) and isinstance(obj_b, dict):
        if len(obj_a) != len(obj_b):
            return False

        for key, value_a in obj_a.items():
            if key not in obj_b or not compare_objects(value_a, obj_b[key]):
                return False
        return True

    elif isinstance(obj_a, list) and isinstance(obj_b, list):
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
    elif isinstance(obj_a, str) and isinstance(obj_b, str):
        if obj_a in obj_b or obj_b in obj_a:
            return True
        return False
    else:
        return obj_a==obj_b
    
def score_calc(map1,map2):
    score=0
    for tool_name, arguments_list1 in map1.items():
        if tool_name in map2:
            arguments_list2 = map2[tool_name]
            for args1 in arguments_list1:
                for args2 in arguments_list2:
                    if compare_objects(args1, args2):
                        score += 1
    return score

def processing_list(list):
  prev_outputs = [None] * len(list)
  list_for_score = copy.deepcopy(list)
  for i, tool in enumerate(list):
    if(tool['arguments']):
      for arg in tool['arguments']:
          if (arg['argument_value']) and '$$PREV[' in arg['argument_value']:
              prev_idx = int(arg['argument_value'].split('$$PREV[')[1][0])
              tool_str=json.dumps(list[prev_idx])
              idx=tool['arguments'].index(arg)
              list_for_score[i]['arguments'][idx]['argument_value']=tool_str
              if prev_idx == i:
                 arg['argument_value'] = tool['tool_name']
              else:
                arg['argument_value'] = prev_outputs[prev_idx]
    prev_outputs[i] = tool['tool_name']
  return list,list_for_score

# list1 = [{'tool_name': 'works_list', 'arguments': [{'argument_name': 'issue.priority', 'argument_value': ['p2']}]}, {'tool_name': 'add_work_items_to_sprint', 'arguments': [{'argument_name': 'work_ids', 'argument_value': '$$PREV[0]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[1]'}]}, {'tool_name': 'get_sprint_id', 'arguments': []}]
# list2 = [{'tool_name': 'get_sprint_id', 'arguments': []},{'tool_name': 'create_actionable_tasks_from_text', 'arguments': [{'argument_name': 'text', 'argument_value': 'MeetingTranscript'}]},{'tool_name': 'add_work_items_to_sprint', 'arguments': [{'argument_name': 'work_ids', 'argument_value': '$$PREV[1]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[0]'}]}]

def compare_lists_of_tools(list1, list2):
    list1,list1_for_score = processing_list(list1)
    list2,list2_for_score = processing_list(list2)
    map1 = {}
    map2 = {}
    for item in list1_for_score:
      tool_name = item['tool_name']
      if tool_name not in map1:
         map1[tool_name] = [item['arguments']]
      else:
         map1[tool_name].append(item['arguments'])

    for item in list2_for_score:
      tool_name = item['tool_name']
      if tool_name not in map2:
         map2[tool_name] = [item['arguments']]
      else:
         map2[tool_name].append(item['arguments'])
    list_size = len(list1)
    return score_calc(map1,map2)==list_size


if __name__=='__main__':
    list1 = [{'tool_name': 'works_list', 'arguments': [{'argument_name': 'issue.priority', 'argument_value': ['p2']}]},{'tool_name': 'get_sprint_id', 'arguments': []},{'tool_name': 'add_work_items_to_sprint', 'arguments':[{'argument_name': 'work_ids', 'argument_value': '$$PREV[0]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[1]'}]}]
    list2 = [{'tool_name': 'works_list', 'arguments': [{'argument_name': 'issue.priority', 'argument_value': ['p1']}]},{'tool_name': 'get_sprint_id', 'arguments': []},{'tool_name': 'add_work_items_to_sprint', 'arguments':[{'argument_name': 'work_ids', 'argument_value': '$$PREV[0]'}, {'argument_name': 'sprint_id', 'argument_value': '$$PREV[1]'}]}]
    lists_equal = compare_lists_of_tools(list1, list2)
    print(lists_equal)
    tot_func=len(list1)
    func_matched=lists_equal
    score=func_matched/tot_func
    print("Final score", score)