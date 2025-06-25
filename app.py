import streamlit as st
import random
import string
from html import escape
import datetime

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "goals" not in st.session_state:
        st.session_state.goals = []
    if "context_topic" not in st.session_state:
        st.session_state.context_topic = None
init_session()

# Page config
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Theme Customizer
theme = st.sidebar.selectbox("🎨 Choose a theme", ["Default", "Night", "Blue"])
if theme == "Night":
    st.markdown("""
    <style>
    body, .stApp { background-color: #111111; color: white; }
    .user { background-color: #333333; color: white; }
    .bot { background-color: #444444; color: white; }
    </style>
    """, unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("""
    <style>
    body, .stApp { background-color: #e0f7fa; }
    .user { background-color: #81d4fa; color: #01579b; }
    .bot { background-color: #b2ebf2; color: #004d40; }
    </style>
    """, unsafe_allow_html=True)

# CSS Styling with animation for sliding text from bottom
st.markdown("""
<style>
/* Slide up animation */
@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translateY(40px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.title-container, .sidebar-title, .tips-header, .goals-header, .assistant-mode-header {
  animation: slideUp 1s ease forwards;
}

/* Delay for sidebar texts */
.sidebar-title {
  animation-delay: 0.3s;
}

.tips-header {
  animation-delay: 0.5s;
}

.goals-header {
  animation-delay: 0.7s;
}

.assistant-mode-header {
  animation-delay: 0.9s;
}

.chat-container { 
  display: flex; 
  flex-direction: column; 
  max-width: 900px; 
  margin: 0 auto; 
  padding: 20px; 
}
.title-container { 
  text-align: center; 
  padding-bottom: 10px; 
  font-family: 'Poppins', sans-serif; 
  font-weight: 600; 
  font-size: 2.5rem;
  color: #222;
}
.chat-window { 
  flex-grow: 1; 
  overflow-y: auto; 
  max-height: 60vh; 
  padding: 15px; 
  display: flex; 
  flex-direction: column; 
  gap: 15px; 
}
.user, .bot { 
  align-self: center; 
  width: 100%; 
  word-wrap: break-word; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
  font-family: 'Poppins', sans-serif; 
  font-size: 1.1rem;
}
.user { 
  background-color: #D1F2EB; 
  color: #0B3D2E; 
  padding: 12px 16px; 
  border-radius: 18px 18px 4px 18px; 
}
.bot  { 
  background-color: #EFEFEF; 
  color: #333; 
  padding: 12px 16px; 
  border-radius: 18px 18px 18px 4px; 
  animation: typing 1s ease-in-out; 
}
.chat-window::-webkit-scrollbar { 
  width: 8px; 
}
.chat-window::-webkit-scrollbar-track { 
  background: #f1f1f1; 
  border-radius: 10px; 
}
.chat-window::-webkit-scrollbar-thumb { 
  background: #c1c1c1; 
  border-radius: 10px; 
}
.chat-window::-webkit-scrollbar-thumb:hover { 
  background: #a1a1a1; 
}
@keyframes typing { 
  0% { opacity: 0; } 
  100% { opacity: 1; } 
}
</style>
""", unsafe_allow_html=True)

# Animated Title
st.markdown('<div class="title-container">AverlinMz – Study Chatbot</div>', unsafe_allow_html=True)

# Full Response Data (same as before, omitted here for brevity)
# Paste your RESPONSE_DATA dict here exactly from your previous code (to save space, omitted)

# Keywords for intent detection (same as before)
# Paste your KEYWORDS dict here exactly from your previous code (to save space, omitted)

# Your functions (clean_text, detect_intent, update_goals, detect_sentiment, get_bot_reply)
# Paste these functions from your previous code exactly here (omitted here for brevity)

# Chat form & display (same as before)
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        bot_reply = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': bot_reply})

# Render chat messages (same as before)
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
msgs = st.session_state.messages
for i in range(len(msgs) - 2, -1, -2):
    user_msg = msgs[i]['content']
    bot_msg = msgs[i+1]['content'] if i+1 < len(msgs) else ''
    st.markdown(f'<div class="user">{escape(user_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{escape(bot_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Sidebar: Show goals and tips with animated headers
with st.sidebar:
    st.markdown('<h3 class="sidebar-title">🎯 Your Goals</h3>', unsafe_allow_html=True)
    if st.session_state.goals:
        for g in st.session_state.goals:
            st.write("- " + g)
    else:
        st.write("You haven't set any goals yet. Tell me your goals!")

    st.markdown('<h3 class="tips-header">💡 Tips</h3>', unsafe_allow_html=True)
    st.info(
        "Try asking things like:\n"
        "- 'Give me study tips'\n"
        "- 'Tell me about physics'\n"
        "- 'How do I manage time?'\n"
        "- 'Motivate me please!'\n"
        "- 'Who created you?'\n"
        "- Or just say 'bye' to end the chat!"
    )

    st.markdown('<h3 class="goals-header">🧠 Mini AI Assistant Mode</h3>', unsafe_allow_html=True)
    st.write("This bot tries to detect your intent and give focused advice or answers.")

# Save chat history as direct download to browser (same as before)
def get_chat_history_text():
    lines = []
    for m in st.session_state.messages:
        role = m['role'].upper()
        content = m['content']
        lines.append(f"{role}: {content}\n")
    return "\n".join(lines)

filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
chat_history_text = get_chat_history_text()

st.download_button(
    label="💾 Download Chat History",
    data=chat_history_text,
    file_name=filename,
    mime="text/plain"
)
