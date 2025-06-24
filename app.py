import streamlit as st
import random
import torch
from html import escape
from sentence_transformers import SentenceTransformer, util

# Load semantic model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Set page config
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# CSS Styling
st.markdown("""
<style>
.stApp { padding: 0 !important; margin: 0 !important; }
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

.chat-container {
    display: flex; flex-direction: column;
    max-width: 900px; margin: 0 auto;
    padding: 20px; box-sizing: border-box;
}
.title-container {
    text-align: center; padding-bottom: 10px; background: white;
    font-family: 'Poppins', sans-serif; font-weight: 600;
}
.title-container h1 { color: black; margin: 0; }

.input-area {
    display: flex; gap: 10px;
    padding: 10px 0 20px 0; background: white;
}
.input-area input {
    flex-grow: 1; padding: 14px 18px; font-size: 16px;
    border: 2px solid #ddd; border-radius: 30px;
    outline: none; transition: border-color 0.3s;
    font-family: 'Poppins', sans-serif;
}
.input-area input:focus { border-color: #3CA887; }
.input-area button {
    padding: 14px 24px; font-size: 16px;
    border: none; border-radius: 30px;
    background-color: #3CA887; color: white;
    cursor: pointer; transition: background-color 0.3s;
    font-family: 'Poppins', sans-serif; font-weight: 500;
}
.input-area button:hover { background-color: #2E7D6F; }

.chat-window {
    flex-grow: 1; overflow-y: auto; max-height: 60vh;
    padding: 15px; display: flex; flex-direction: column-reverse;
    gap: 15px;
}
.user, .bot {
    align-self: center; width: 100%;
}
.user {
    background-color: #D1F2EB; color: #0B3D2E;
    padding: 12px 16px; border-radius: 18px 18px 4px 18px;
    font-family: 'Poppins', sans-serif;
    word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.bot {
    background-color: #EFEFEF; color: #333;
    padding: 12px 16px; border-radius: 18px 18px 18px 4px;
    font-family: 'Poppins', sans-serif;
    word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.chat-window::-webkit-scrollbar { width: 8px; }
.chat-window::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }
</style>
""", unsafe_allow_html=True)

# Auto scroll
st.markdown("""
<script>
function scrollToBottom() {
    const w = document.querySelector('.chat-window');
    if (w) w.scrollTop = w.scrollHeight;
}
window.onload = scrollToBottom;
new MutationObserver(scrollToBottom).observe(
    document.querySelector('.chat-window'),
    { childList: true, subtree: true }
);
</script>
""", unsafe_allow_html=True)

# Rich responses
RESPONSES = {
    "olympiad_tips": {
        "keywords": ["olympiad", "subject olympiad", "contest", "competition", "how to prepare", "olympiad tips"],
        "reply": """🚀 **Preparing for subject Olympiads?** Here's a roadmap to victory:

1. **Master the fundamentals** 🧠 – Concepts first, formulas later.
2. **Solve past questions** 📘 – Spot patterns, gain intuition.
3. **Keep an error log** ✍️ – Learn deeply from mistakes.
4. **Simulate real tests** ⏱️ – Build stamina and time management.
5. **Stay curious & resilient** 💪 – Olympiads test mindset as much as skill.

Remember: It’s not about speed — it’s about strategy. You've got this! 🌟"""
    },
    "biology_tips": {
        "keywords": ["bio", "biology", "biology olympiad", "prepare biology"],
        "reply": """🧬 **Biology Olympiad Champions, unite!**

- Dive into **cell biology**, **genetics**, and **physiology**.
- Use **Campbell’s Biology** and **BOG/BBO materials**.
- Practice with diagrams, data-based questions, and analysis.
- Don’t just memorize — **understand how life works**. 🌱

Biology is not just about facts; it’s about life’s code. 🔬💚"""
    }
}

FALLBACK_REPLIES = [
    "Hmm 🤔 I’m still learning. Could you rephrase that a bit? You're doing awesome anyway! 🌈",
    "I'm not sure I got that — but I’m proud of your effort 💪 Keep going, one step at a time!",
    "That’s an interesting thought! I’ll understand it better next time. You rock 🚀"
]

# Precompute intent embeddings
intent_embeddings = []
intent_replies = []
for intent in RESPONSES.values():
    for kw in intent["keywords"]:
        intent_embeddings.append(model.encode(kw, convert_to_tensor=True))
        intent_replies.append(intent["reply"])

def generate_reply(user_msg, threshold=0.55):
    user_embedding = model.encode(user_msg, convert_to_tensor=True)
    scores = [util.pytorch_cos_sim(user_embedding, emb)[0].item() for emb in intent_embeddings]
    max_score = max(scores)
    if max_score > threshold:
        return intent_replies[scores.index(max_score)]
    return random.choice(FALLBACK_REPLIES)

# UI rendering
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "message_input",
        placeholder="Write your message…",
        key="input_field",
        label_visibility="collapsed"
    )
    submit = st.form_submit_button("Send")
    if submit and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "bot", "content": generate_reply(user_input)})

# Chat window rendering
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
for msg in reversed(st.session_state.messages):
    text = escape(msg["content"])
    cls = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
