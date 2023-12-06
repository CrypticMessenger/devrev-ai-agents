import csv
import json


def csv_to_json(input_csv, output_jsonl, starting_prompt):
    with open(input_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header row

        with open(output_jsonl, 'w') as jsonl_file:
            for row in csv_reader:
                user_content = row[0]
                assistant_content = row[1]

                message = {
                    "role": "system",
                    "content": starting_prompt
                }

                messages_list = [message]

                message = {
                    "role": "user",
                    "content": user_content
                }
                messages_list.append(message)

                message = {
                    "role": "assistant",
                    "content": assistant_content
                }
                messages_list.append(message)

                final_json = {"messages": messages_list}

                # Write the JSON object without indentation and on a single line
                jsonl_file.write(json.dumps(final_json, separators=(',', ':')) + '\n')

