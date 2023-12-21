import streamlit as st

from PalmSegDemo import inference

# Function to generate chatbot response
def get_response(user_input):
    user_input = user_input.lower()
    return inference.invoke_agent(user_input)

# Streamlit UI
def main():
    # Set app title and page icon
    st.set_page_config(page_title="devrev", page_icon=":robot:")

    # App title and header
    st.title("devrev")
    st.markdown("Welcome to devrev! Ask me anything.")

    user_input = st.text_input("You:", "")

    if st.button("Send"):
        if user_input:
            bot_response = get_response(user_input)
            st.text_area("Chatbot:", value=bot_response, height=100, max_chars=None)

if __name__ == "__main__":
    main()
