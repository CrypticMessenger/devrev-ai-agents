import google.generativeai as palm
PALM_API_KEY='YOUR_API_KEY_HERE'
palm.configure(api_key=PALM_API_KEY)

history = ""
curr_conversation = '''
Ben: "Hello, how can I help you today?"'''

while(True):
    user_input = input("Enter a string: ")
    if(user_input == "exit"):
        break
    curr_conversation+="\n<USER>: \"" + user_input + "\""
    print(curr_conversation)

    answer_prompt = f'''
    A friend named Ben has a discussion with <USER>. <USER> decides the
    conversation topic and Ben and <USER> discuss this topic. Ben asks questions
    often.

    {history}

    {curr_conversation}
    Ben: '''

    response = palm.generate_text(prompt=answer_prompt)
    print(response.result)
    curr_conversation+="\nBen: " + response.result

    print("-->Conversation Length: " + str(len(curr_conversation)))

    summarize_prompt = f'''
    Summarize the following conversation between two friends named Ben and <USER>:

    {history}

    {curr_conversation}

    The summary should describe the context of the conversation in the past tense.

    '''
    
    if(len(curr_conversation) > 1000):
        response = palm.generate_text(prompt=summarize_prompt)
        print("Summary: "+response.result)
        history = response.result
        curr_conversation = ""
        print("Resetting conversation")