
all_tools = {
  "tools": [
    {
      "name": "works_list",
      "description": "Returns a list of work items matching the request",
      "arguments": [
        {
          "name": "applies_to_part",
          "description": "Filters for work belonging to any of the provided parts",
          "type": "array of strings",
          "example": ["FEAT-123", "ENH-123", "PROD-123", "CAPL-123"]
        },
        {
          "name": "created_by",
          "description": "Filters for work created by any of these users",
          "type": "array of strings",
          "example": ["DEVU-123"]
        },
        {
          "name": "issue_priority",
          "description": "Filters for issues with any of the provided priorities. Allowed values: p0, p1, p2, p3",
          "type": "array of strings"
        },
        {
          "name": "issue_rev_orgs",
          "description": "Filters for issues with any of the provided Rev organizations",
          "type": "array of strings",
          "example": ["REV-123"]
        },
        {
          "name": "limit",
          "description": "The maximum number of works to return. The default is '50'",
          "type": "integer (int32)"
        },
        {
          "name": "owned_by",
          "description": "Filters for work owned by any of these users",
          "type": "array of strings",
          "example": ["DEVU-123"]
        },
        {
          "name": "stage_name",
          "description": "Filters for records in the provided stage(s) by name",
          "type": "array of strings"
        }
      ]
    },
    {
      "name": "summarize_objects",
      "description": "Summarizes a list of objects. The logic of how to summarize a particular object type is an internal implementation detail.",
      "arguments": [
        {
          "name": "objects",
          "description": "List of objects to summarize",
          "type": "array of objects"
        }
      ]
    },
    {
      "name": "prioritize_objects",
      "description": "Returns a list of objects sorted by priority. The logic of what constitutes priority for a given object is an internal implementation detail.",
      "arguments": [
        {
          "name": "objects",
          "description": "A list of objects to be prioritized",
          "type": "array of objects"
        }
      ]
    },
    {
      "name": "add_work_items_to_sprint",
      "description": "Adds the given work items to the sprint",
      "arguments": [
        {
          "name": "work_ids",
          "description": "A list of work item IDs to be added to the sprint.",
          "type": "array of strings"
        },
        {
          "name": "sprint_id",
          "description": "The ID of the sprint to which the work items should be added",
          "type": "string"
        }
      ]
    },
    {
      "name": "get_sprint_id",
      "description": "Returns the ID of the current sprint"
    },
    {
      "name": "get_similar_work_items",
      "description": "Returns a list of work items that are similar to the given work item",
      "arguments": [
        {
          "name": "work_id",
          "description": "The ID of the work item for which you want to find similar items",
          "type": "string"
        }
      ]
    },
    {
      "name": "search_object_by_name",
      "description": "Given a search string, returns the id of a matching object in the system of record. If multiple matches are found, it returns the one where the confidence is highest.",
      "arguments": [
        {
          "name": "query",
          "description": "The search string, could be for example customer’s name, part name, user name.",
          "type": "string"
        }
      ]
    },
    {
      "name": "create_actionable_tasks_from_text",
      "description": "Given a text, extracts actionable insights, and creates tasks for them, which are kind of a work item.",
      "arguments": [
        {
          "name": "text",
          "description": "The text from which the actionable insights need to be created.",
          "type": "string"
        }
      ]
    },
    {
      "name": "who_am_i",
      "description": "Returns the ID of the current user"
    }
  ]
}


# Set up the base template
template = f"""You are the helping the chatbot of the company dev-rev. Input question is the query of the user. Answer the following questions as best you can. You have access to the following tools:

{all_tools}

You can choose to use no tool.
If you feel not enough information is present, Ask the user by query_user tool.
Use the following format:

Question: the input question you must answer
now think step by step, and break the Question into multiple actions.
Final Answer: for each action return "tool_name","argument_name","argument_value"
For each action, you must search the most relevant sentence in the context, and return the tool name, argument name, argument value.


Example:

Question: Prioritize my P0 issues and add them to the current sprint
Final Answer:
"tool_name": "whoami"
"tool_name": "works_list"
"argument_name": "issue.priority"
"argument_value": ["p0"]
"argument_name": "owned_by"
"argument_value": ["$$PREV[0]"]
"argument_name": "type"
"argument_value": ["issue"]
"tool_name": "prioritize_objects"
"argument_name": "objects"
"argument_value": "$$PREV[1]"
"tool_name": "get_sprint_id"
"tool_name": "add_work_items_to_sprint"
"argument_name": "work_ids"
"argument_value": "$$PREV[2]"
"argument_name": "sprint_id"
"argument_value": "$$PREV[3]"

Question: Summarize work items similar to don:core:dvrv-us-1:devo/0:issue/1
Final Answer:
"tool_name": "get_similar_work_items"
"argument_name": "work_id"
"argument_value": "don:core:dvrv-us-1:devo/0:issue/123"
"tool_name": "summarize_objects"
"argument_name": "objects"
"argument_value": "$$PREV[0]"

Final Answer should contain all the actions(tool name) you took and list of all pairs of argument value and argument name in above format as shown above.
Begin! Remember to just output the final result. No blabbering

Question: """