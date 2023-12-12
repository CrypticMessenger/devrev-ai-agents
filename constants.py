EXAMPLE_TEMPLATE = """You will be given a function description, for this function create chat examples queries of user for which the function can be used. Example:
Function description: Function Name is create_actionable_tasks_from_text. Description:Given a text, extracts actionable insights, and creates tasks for them, which are kind of a work item. [argument name - text, description = The text from which the actionable insights need to be created.]
Output: query1:Given a customer meeting transcript T, create action items. query2: Given summary S of sprint, create action items.
Create {number_of_examples} examples for the function. Create example queries to cover important aspects of the function.
"""

PALM_EXAMPLES_TEMPLATES = [
    ('Function description: Function Name is create_actionable_tasks_from_text. Description:Given a text, extracts actionable insights, and creates tasks for them, which are kind of a work item. [argument name - text, description = The text from which the actionable insights need to be created.',
     '''query1:Given a customer meeting transcript T, create action items. query2: Given summary S of sprint, create action items. Create {number_of_examples} examples for the function. Create example queries to cover important aspects of the function.'''
     )
]

PALM_CONTEXT = "You will be given a function description, for this function create chat examples queries of user for which the function can be used."

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
        },
        {
          "name": "ticket_needs_response",
          "description": "Filters for tickets that need a response",
          "type": "boolean"
        },
        {
          "name": "ticket_rev_org",
          "description": "Filters for tickets associated with any of the provided Rev Organizations",
          "type": "array of strings",
          "example": ["REV-123"]
        },
        {
          "name": "ticket_severity",
          "description": "Filters for tickets with any of the provided severities. Allowed values: blocker, high, low, medium",
          "type": "array of strings"
        },
        {
          "name": "ticket_source_channel",
          "description": "Filters for tickets with any of the provided source channels",
          "type": "array of strings"
        },
        {
          "name": "type",
          "description": "Filters for work of the provided types. Allowed values: issue, ticket, task",
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
      "description": "Returns the ID of the current user."
    }
  ]
}

all_tools_regular = {"tools": [
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
          "name": "owned_by",
          "description": "Filters for work owned by any of these users",
          "type": "array of strings",
          "example": ["DEVU-123"]
        },
        {
          "name": "issue.rev_orgs",
          "description": "Filters for issues with any of the provided Rev organizations",
          "type": "array of strings",
          "example": ["REV-123"]
        },
        {
          "name": "issue.priority",
          "description": "Filters for issues with any of the provided priorities. Allowed values: p0, p1, p2, p3",
          "type": "array of strings"
        },
        {
          "name": "limit",
          "description": "The maximum number of works to return. The default is '50'",
          "type": "integer (int32)"
        },
        {
          "name": "stage.name",
          "description": "Filters for records in the provided stage(s) by name",
          "type": "array of strings"
        },
        {
          "name": "ticket.needs_response",
          "description": "Filters for tickets that need a response",
          "type": "boolean"
        },
        {
          "name": "ticket.severity",
          "description": "Filters for tickets with any of the provided severities. Allowed values: blocker, high, low, medium",
          "type": "array of strings"
        },
        {
          "name": "ticket.source_channel",
          "description": "Filters for tickets with any of the provided source ch ",
          "type": "array of strings"
        },
        {
          "name": "types",
          "description": "Filters for work of the provided types. Allowed values: issue, ticket, task",
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
template = """You are the helping the chatbot of the company dev-rev. Input question is the query of the user. Answer the following questions as best you can. You have to get related tools using "get_related_tools" 
You can choose to use no tool.
Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do for answering user query
Action: the action to take, should be one of related tool only
Action Input: the input'(argument name, argument value)' to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: for each action return "tool_name","argument_name","argument_value"'' '
Example:
Question:  Summarize work items similar to don
Thought: Let's first find relevant tools for getting work items similar to don
Action: get_related_tools
Action Input: ("query": "getting work items similar to don")
Observation: ["function_name is get_similar_work_items. ....","function_name is work_items......","function_name is who_am_i....."]
Thought: Now we have relevant tools: ["get_similar_work_items"]. Let's call it.
Action: get_similar_work_items
Action Input: ("work_id": "don")
Observation: No error. Proceed to next step.
Thought: We have the work items. Now we need to find related tools to summarize them
Action: get_related_tools
Action Input: ("query": "to summarize work_items")
Observation: ["function_name is summarize_objects","function_name is work_items","function_name is get_similar_work_items"]
Thought: Now we have related tools to summarize objects: ["summarize_objects"].
Action: summarize_objects
Action Input:
(objects: "$$PREV[0]"(Referring to the out of get_similar_work_items, in the indexing do not include "get_related_tools")
Observation: No error. Proceed to next step.
Thought: I now know the final answer
Final Answer:
"tool_name": "get_similar_work_items"
"argument_name": "word_id"
"argument_value": "don"
"tool_name": "summarize_objects"
"argument_name": "objects"
"argument_value": "$$PREV[0]"
for the Question:  Summarize work items similar to don,
Final Answer should contain all the actions(tool name) you took and list of all pairs of argument value and argument name.
Begin!This Thought/Action/Action Input/Observation can repeat N times.Take actions and find the answer.
Solve the query in steps inteligently.If a tools requires a particular input do not assume it, find another tool to get it.
DO NOT ASSUME ARGUMENT VALUES TO THE FUNCTIONS.
Question: {input}
{agent_scratchpad}"""