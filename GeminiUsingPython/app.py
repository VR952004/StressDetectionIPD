import streamlit as st
from chatbot import start_chat, get_bot_response

# Maintain chat session and history in session state
if 'chat' not in st.session_state:
    st.session_state['chat'] = start_chat()  # Automatically start chatbot on page load
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'message_submitted' not in st.session_state:
    st.session_state['message_submitted'] = False  # Track form submission status

# Function to send the user message and get the bot's response
def send_message(user_message):
    if st.session_state['chat']:
        if user_message:
            # Append user message to chat history with bold "You"
            st.session_state['chat_history'].append({"role": "user", "text": f"**You**: {user_message}"})

            # Get bot response and append to chat history with bold "Bot"
            bot_response = get_bot_response(st.session_state['chat'], user_message)
            st.session_state['chat_history'].append({"role": "bot", "text": f"**Alora**: {bot_response}"})

# Streamlit Layout
st.title("Alora")

# Automatically start the conversation if it hasn't already
if len(st.session_state['chat_history']) == 0:
    st.session_state['chat_history'].append({"role": "bot", "text": "**Alora**: How has your day been so far?"})

# Display chat history
st.write("### Personalized Stress Detection Chatbot")
for message in st.session_state['chat_history']:
    st.markdown(message['text'])  # Render as Markdown to apply bold formatting

# Use a form for the input and button
with st.form(key="user_input_form", clear_on_submit=True):
    user_message = st.text_input("You:", value="")
    submit_button = st.form_submit_button(label="Send Message")

# Handle form submission and send the message immediately
if submit_button and user_message:
    send_message(user_message)  # Pass the input to send_message function