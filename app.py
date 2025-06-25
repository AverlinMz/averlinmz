# app.py

import streamlit as st
import random
import string
from html import escape
from responses import RESPONSE_DATA, KEYWORDS  # <-- make sure 'responses.py' is here

def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
init_session()

st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Styling
st.markdown("""
<style>
.stApp { padding: 0 !important; margin: 0 !important; }
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

.chat-container { display: flex; flex-direction: column; max-width: 900px; margin: 0 auto; padding: 20px; }
.title-container { text-align: center; padding-bottom: 10px; background: white; font-family: 'Poppins', sans-serif; font-weight: 600; }
.title-container h1 { color: black; margin: 0; }

.chat-window { flex-grow: 1; overflow-y: auto; max-height: 60vh; padding: 15px; display: flex; flex-direction: column; gap: 15px; }
.user, .bot { align-self: center; width: 100%; word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: 'Poppins', sans-serif; }
.user { background-color: #D1F2EB; color: #0B3D2E; padding: 12px 16px; border-radius: 18px 18px 4px 18px; }
.bot  { background-color: #EFEFEF; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; animation: typing 1s ease-in-out; }

.chat-window::-webkit-scrollbar { width: 8px; }
.chat-window::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }

@keyframes typing { from { opacity: 0; } to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# Helpers
def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # 1) Check every top-level category except 'subjects'
    for cat in RESPONSE_DATA:
        if cat == "subjects":
            continue
        if any(kw in msg for kw in cleaned.get(cat, [])):
            return random.choice(RESPONSE_DATA[cat])

    # 2) Check 'subjects'
    for subj in cleaned.get("subjects", []):
        if subj in msg and subj in RESPONSE_DATA["subjects"]:
            return RESPONSE_DATA["subjects"][subj]

    # 3) Fallback
    return random.choice(RESPONSE_DATA["fallback"])

# Chat UI
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message…", key="input_field")
    if st.form_submit_button("Send") and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "bot", "content": get_bot_reply(user_input)})

# Render conversation
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
for i in range(len(st.session_state.messages) - 2, -1, -2):
    user_msg = st.session_state.messages[i]["content"]
    bot_msg  = st.session_state.messages[i+1]["content"] if i+1 < len(st.session_state.messages) else ""
    st.markdown(f'<div class="user">{escape(user_msg)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{escape(bot_msg)}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Sidebar tips
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.info(
        "- Say ‘hi’ or ‘hello’\n"
        "- Ask for ‘exam tips’\n"
        "- Try ‘I passed my exam’\n"
        "- Or simply ‘goodbye’ to see the farewell!"
    )
