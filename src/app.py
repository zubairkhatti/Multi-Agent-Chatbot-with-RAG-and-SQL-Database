import streamlit as st
from chatbot.chatbot_backend import ChatBot
from ui.chat_ui import get_image_base64, setup_css, render_chat, chat_input_form

# Set basic Streamlit page configuration
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# Load avatar images for user and chatbot
user_avatar = get_image_base64("images/user.png")
bot_avatar = get_image_base64("images/system.webp")

# Initialize chat history in session state if not present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Apply custom CSS styling to chat UI
setup_css(user_avatar, bot_avatar)

# Render chat history on screen
render_chat(st.session_state.chat_history, user_avatar, bot_avatar)

# Input field for user query
user_input, submitted = chat_input_form()

# Handle chatbot response after user submits input
if submitted and user_input:
    _, updated_history = ChatBot.respond(st.session_state.chat_history, user_input)
    st.session_state.chat_history = updated_history
    st.rerun() # Re-render UI to show updated chat

# Button to clear chat history
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()
