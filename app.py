import streamlit as st
import difflib
import random
import time
from html import escape

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "typing" not in st.session_state:
    st.session_state.typing = False

if "last_bot_reply" not in st.session_state:
    st.session_state.last_bot_reply = ""

# Page config
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS styling
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

.chat-window {
    flex-grow: 1; overflow-y: auto; max-height: 60vh;
    padding: 15px; display: flex; flex-direction: column-reverse;
    gap: 15px;
}

.user,
.bot {
    align-self: center;
    width: 100%;
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

# Auto-scroll JS
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

# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# Define responses
RESPONSES = {
    "study_smart": {
        "keywords": ["study smart", "study smarter", "study tips", "study plan"],
        "reply": """Hey friend! 🌟 Here are some powerful tips to study smarter, not harder:

1. **Active recall** – quiz yourself instead of just rereading.
2. **Spaced repetition** – review material over increasing intervals.
3. **Pomodoro technique** – work 25 mins, break 5, repeat! 🍅
4. **Teach what you learn** – if you can explain it, you’ve mastered it.
5. **Plan weekly goals** – focus on outcomes, not just time spent.

And don’t forget: rest is part of the process 💤. Your brain loves clarity, not clutter. You’ve got this! 🚀"""
    },
    "tired": {
        "keywords": ["tired", "burned out", "exhausted", "no energy"],
        "reply": """Oh no 😞 You sound really drained. That’s totally okay – you’re human! 🧡

Here’s what you can try:
- ✋ Step away from the screen. Even 10 minutes helps.
- 💧 Hydrate and grab a healthy snack.
- 🌬️ Breathe in deeply 5 times. Slowly. Really slowly.
- 💤 Nap or stretch your legs – your body needs care.

You’re doing more than enough. Let go of pressure. Come back stronger 💪 I believe in you!"""
    },
    "greeting": {
        "keywords": ["hello", "hi", "hey", "heyy"],
        "reply": """Hey there! 👋 Welcome back!

I'm AverlinMz, your loyal study buddy 📚✨ Ready to dive into a new topic, crush a challenge, or just chat for motivation?

Whatever you're facing today, you're not alone. Let’s go! 💪🌟"""
    },
    "capabilities": {
        "keywords": ["what can you do", "abilities", "features", "skills"],
        "reply": """Great question! 🤖 Here’s what I can do:

✅ Cheer you on when you're tired
✅ Give personalized study tips
✅ Answer questions on school subjects
✅ Remind you to rest and stay kind to yourself
✅ Chat when you need a break or a friend 💛

I’m still learning — and growing with you! 🌱"""
    },
    "default": {
        "keywords": [],
        "reply": "Hmm 🤔 I’m still learning. Could you rephrase that a bit? You're doing awesome anyway! 🌈"
    }
}

FALLBACK_REPLIES = [
    "You're making real progress – don’t stop now! 💥",
    "Every step matters, even the tiny ones 🐾 Keep going!",
    "You are capable of amazing things. Believe it 💫"
]

# Helper functions
def contains_keyword(msg, keywords, cutoff=0.75):
    msg = msg.lower()
    for kw in keywords:
        if kw in msg:
            return True
        for w in msg.split():
            if difflib.SequenceMatcher(None, w, kw).ratio() >= cutoff:
                return True
    return False

def generate_reply(user_msg):
    lm = user_msg.lower()
    for data in RESPONSES.values():
        if contains_keyword(lm, data["keywords"]):
            return data["reply"]
    return random.choice(FALLBACK_REPLIES)

# Chat input form
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
        reply = generate_reply(user_input)
        st.session_state.last_bot_reply = reply
        st.session_state.messages.append({"role": "bot", "content": None})
        st.session_state.typing = True

# Render chat window
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)

# Display all messages, newest first
messages = st.session_state.messages[:]
messages.reverse()

for i in range(0, len(messages), 2):
    if i + 1 < len(messages):
        user_msg = messages[i + 1]
        bot_msg = messages[i]

        st.markdown(f'<div class="user">{escape(user_msg["content"]).replace("\n","<br>")}</div>', unsafe_allow_html=True)

        if bot_msg["content"] is None:
            container = st.empty()
            if st.session_state.typing:
                container.markdown('<div class="bot">🤖 Typing...</div>', unsafe_allow_html=True)
                time.sleep(2)
                container.markdown(f'<div class="bot">{escape(st.session_state.last_bot_reply).replace("\n","<br>")}</div>', unsafe_allow_html=True)
                # Update placeholder
                for j in range(len(st.session_state.messages) - 1, -1, -1):
                    if st.session_state.messages[j]["role"] == "bot" and st.session_state.messages[j]["content"] is None:
                        st.session_state.messages[j]["content"] = st.session_state.last_bot_reply
                        break
                st.session_state.typing = False
            else:
                container.markdown(f'<div class="bot">{escape(st.session_state.last_bot_reply).replace("\n","<br>")}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot">{escape(bot_msg["content"]).replace("\n","<br>")}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
