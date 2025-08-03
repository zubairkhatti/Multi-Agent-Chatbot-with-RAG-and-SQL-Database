import base64
import markdown2
import streamlit as st

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return ""  # fallback to blank avatar


def setup_css(user_avatar, bot_avatar):
    st.markdown(f"""
        <style>
        .main .block-container {{
            max-width: 100vw !important;
            padding-left: 0rem;
            padding-right: 0rem;
        }}
        .chat-container {{
            background: #252529;
            border-radius: 15px;
            padding: 2vw 1vw 10vw 1vw;
            margin-top: -4vw;
            height: 60vh;
            overflow-y: auto;
            scrollbar-width: thin;
            -webkit-overflow-scrolling: touch;
        }}
        .stTextInput > div > div > input {{
            width: 100% !important;
            font-size: 1.0em;
            padding: 1em;
            border-radius: 12px;
            height: auto;
        }}
        .stButton > button {{
            width: 100%;
            font-size: 1.0em;
            border-radius: 12px;
            margin-top: 0;
        }}
        .form-container {{
            width: 100%;
            max-width: 100%;
            margin: 0 auto;
            padding: 1em 0 0 0;
        }}
        .input-row {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .input-field {{
            flex: 1;
        }}
        .send-button {{
            margin-top: 28px !important;  /* Move it down */
            /* or margin-top: -10px !important; to move it up */
        }}
        .clear-button {{
            margin-top: 10px;
        }}
        .chat-row {{
            display: flex;
            margin-bottom: 15px;
        }}
        .user-row {{ justify-content: flex-end; }}
        .ai-row {{ justify-content: flex-start; }}
        .chat-bubble {{
            max-width: 80%;
            padding: 10px 20px;
            border-radius: 18px;
            font-size: 1em;
            line-height: 1.3;
            word-break: break-word;
        }}
        .user-bubble {{
            background-color: #d1f5d3;
            color: #222;
            border-bottom-right-radius: 4px;
            margin-right: 10px;
        }}
        .ai-bubble {{
            background-color: #333336;
            color: #fff;
            border-bottom-left-radius: 4px;
            margin-left: 10px;
        }}
        .avatar {{
            width: 25px;
            height: 25px;
            border-radius: 50%;
            object-fit: cover;
            background: #fff;
        }}
        </style>
    """, unsafe_allow_html=True)

def format_message(text):
    return text.replace('\n', '<br>')

def render_chat(chat_history, user_avatar, bot_avatar):
    user_avatar_src = f"data:image/png;base64,{user_avatar}"
    bot_avatar_src = f"data:image/png;base64,{bot_avatar}"

    chat_html = '<div class="chat-container" id="chatbox">'
    for user_msg, bot_msg in chat_history:
        chat_html += (
            f'<div class="chat-row user-row">'
            f'<div class="chat-bubble user-bubble">{markdown2.markdown(format_message(user_msg))}</div>'
            f'<img src="{user_avatar_src}" class="avatar" />'
            f'</div>'
            f'<div class="chat-row ai-row">'
            f'<img src="{bot_avatar_src}" class="avatar" />'
            f'<div class="chat-bubble ai-bubble">{markdown2.markdown(format_message(bot_msg))}</div>'
            f'</div>'
        )
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    st.markdown("""
        <script>
            var chatbox = document.getElementById('chatbox');
            if (chatbox) chatbox.scrollTop = chatbox.scrollHeight;
        </script>
    """, unsafe_allow_html=True)

def chat_input_form():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([14, 1])
        with col1:
            user_input = st.text_input("Type your message:", key="input")
        with col2:
            st.markdown('<div class="send-button">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Send")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return user_input.strip(), submitted
