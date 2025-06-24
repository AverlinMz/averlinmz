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

# CSS styling (same as before, condensed here)
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
    padding: 15px; display: flex; flex-direction: column;
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

# Auto-scroll JS (scrolls to bottom after new messages)
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


# Rich, warm replies
RESPONSES = {
    "introduction": {
        "keywords": ["introduce","who are you","your name","about you","creator","who made you"],
        "reply": (
            "🌟 Hey! I'm AverlinMz, your personal study chatbot, here to support you through your learning journey. "
            "I was created by the brilliant Aylin Muzaffarli, who’s passionate about music, programming, robotics, AI, and physics! "
            "Whether you want study tips, motivation, or just a friendly chat, I’m here 24/7 for you. Let's make learning fun and effective together! 🎉📚"
        )
    },
    "capabilities": {
        "keywords": ["what can you do","what you can do","what can u do","capabilities","help"],
        "reply": (
            "🤖 Glad you asked! Here's what I can do for you:\n\n"
            "✨ Provide detailed, subject-specific study advice.\n"
            "💪 Motivate and encourage you when the going gets tough.\n"
            "❤️ Offer emotional support when you’re feeling stressed, tired, or overwhelmed.\n"
            "🎯 Help you plan and organize your study sessions for maximum efficiency.\n"
            "💡 Answer questions honestly and challenge you to think deeper.\n\n"
            "Think of me as your study buddy and personal cheerleader, always ready to help! 🚀"
        )
    },
    "olympiad_tips": {
        "keywords": ["olymp","olympuad","tip","tips","advise","advice"],
        "reply": (
            "🏅 Preparing for Olympiads? Here’s how you can shine bright:\n\n"
            "1️⃣ Focus on truly understanding core concepts instead of rote memorization.\n"
            "2️⃣ Solve as many past Olympiad problems as you can — it's the best practice!\n"
            "3️⃣ Analyze your mistakes deeply and learn from them — this turns failures into successes.\n"
            "4️⃣ Balance your study with rest and hobbies to keep your mind fresh and creative.\n"
            "5️⃣ Stay curious and enjoy the challenge — your passion will carry you far! 🌈\n\n"
            "Remember, Olympiads are about growth and learning, not just winning. Keep believing in yourself! 💫"
        )
    },
    "tired": {
        "keywords": ["tired","burned out","exhausted","fatigue"],
        "reply": (
            "😴 Feeling tired is completely natural when you’re pushing hard! Here’s some advice:\n\n"
            "🧘‍♀️ Take a short break — stretch, breathe deeply, or go for a quick walk.\n"
            "💧 Hydrate yourself well; sometimes fatigue is a sign your body needs water.\n"
            "💤 Don’t underestimate power naps — even 15-20 minutes can recharge your brain.\n"
            "🌿 Remember, rest is an essential part of effective learning, not wasted time.\n\n"
            "Your body and mind will thank you, and you’ll come back stronger and sharper! Keep going, you’re doing amazing! 🌟"
        )
    },
    "sad": {
        "keywords": ["sad","down","depressed","crying"],
        "reply": (
            "I’m really sorry you’re feeling this way 💙. Remember, it’s okay to have tough days.\n"
            "Your feelings are valid, and you’re not alone — I’m here to listen anytime you want to share.\n"
            "Sometimes, a little rest, talking to a friend, or a calm walk can help lighten the load.\n"
            "You’re stronger than you think, and this moment will pass. 🌈"
        )
    },
    "anxious": {
        "keywords": ["anxious","worried","panic","nervous"],
        "reply": (
            "Anxiety can be really tough, but you’re doing your best and that matters 🧡.\n"
            "Try to pause for a moment — take slow, deep breaths or step outside for some fresh air 🌿.\n"
            "Breaking tasks into small steps can make things feel more manageable.\n"
            "Remember, I believe in you and I’m here for every step of your journey! 💪"
        )
    },
    "failure": {
        "keywords": ["failed","mistake","i can't","gave up", "lost"],
        "reply": (
            "Mistakes and setbacks are part of the learning adventure! 📚\n"
            "Every mistake teaches you something new and brings you closer to your goals.\n"
            "Be kind to yourself and remember, persistence beats perfection.\n"
            "You have the strength to rise again and improve — keep going, I believe in you! 🌟"
        )
    },
    "success": {
        "keywords": ["i did it","solved it","success","finished","completed"],
        "reply": (
            "🎉 Congratulations! That’s fantastic news.\n"
            "Celebrate this achievement — every win, big or small, deserves recognition.\n"
            "Keep this momentum going and remember, I’m always here cheering you on! 🚀"
        )
    },
    "thanks": {
        "keywords": ["thank you","thanks","thx","ty"],
        "reply": (
            "You’re very welcome! 😊 I’m proud of your efforts.\n"
            "Feel free to come back anytime you need advice, motivation, or just a chat. Keep up the amazing work! 🌟"
        )
    },
    "farewell": {
        "keywords": ["goodbye","bye","see ya","see you","later"],
        "reply": (
            "See you later! 👋 Keep up the great work and don’t hesitate to come back when you need a boost.\n"
            "Wishing you all the best on your study journey! ✨"
        )
    },
    "productivity": {
        "keywords": ["consistent","discipline","productive","motivation"],
        "reply": (
            "Discipline truly beats motivation — here’s how to build it:\n\n"
            "✅ Set small, achievable goals each day to keep momentum.\n"
            "✅ Track your progress and celebrate even minor wins.\n"
            "✅ Be patient and forgive yourself when things don’t go perfectly.\n"
            "Consistency over time leads to amazing results. You’ve got this! 💪🔥"
        )
    },
    "rest": {
        "keywords": ["break","rest","sleep","relax"],
        "reply": (
            "Rest is a vital part of learning and growth! 💤\n"
            "Your brain processes and consolidates knowledge best when it’s well rested.\n"
            "Make sure to get quality sleep, take short breaks during study, and balance work with fun.\n"
            "Remember: rest fuels your focus and creativity. Treat yourself kindly! 🌿"
        )
    },
    "study_smart": {
        "keywords": ["study smart", "study smarter", "study advice", "study tips"],
        "reply": (
            "📘 Let's dive into some powerful ways to study smarter, not harder:\n\n"
            "1️⃣ **Active recall**: test yourself often rather than passively rereading. Use flashcards or apps like Anki!\n"
            "2️⃣ **Spaced repetition**: revisit topics multiple times spaced over days or weeks to lock them into long-term memory.\n"
            "3️⃣ **Prioritize key topics**: focus first on foundational concepts before tackling complex details.\n"
            "4️⃣ **Mix subjects**: switch between different topics to keep your brain active and improve retention.\n"
            "5️⃣ **Take quality breaks**: short breaks rejuvenate your mind and improve focus when you return.\n"
            "6️⃣ **Set micro-goals**: break your study into small, achievable tasks to stay motivated and track progress.\n\n"
            "Keep consistency, not cramming, as your goal. You’re capable of amazing things — keep pushing forward! 💪🚀"
        )
    }
}

FALLBACK_REPLIES = [
    "Hmm 🤔 I’m still learning. Could you please rephrase that? You're doing amazing! 🌟",
    "Keep going! Every bit of progress counts! 💪",
    "Remember, growth is a journey, not a race. One step at a time! 🌱",
    "You've got this! I'm cheering for you! 🎉",
    "Struggles mean you're pushing your limits. Stay patient and strong! 💖"
]

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


# Simulate bot typing effect
def bot_typing_simulation(reply_text, container):
    container.markdown('<div class="bot">🤖 Typing...</div>', unsafe_allow_html=True)
    time.sleep(2)  # simulate delay
    container.markdown(f'<div class="bot">{escape(reply_text).replace("\\n","<br>")}</div>', unsafe_allow_html=True)


# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "message_input",
        placeholder="Write your message…",
        key="input_field",
        label_visibility="collapsed"
    )
    submit = st.form_submit_button("Send")
    if submit and user_input.strip():
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate bot reply
        reply = generate_reply(user_input)
        st.session_state.last_bot_reply = reply

        # Append a placeholder for bot message (None for now)
        st.session_state.messages.append({"role": "bot", "content": None})

        # Mark typing state true
        st.session_state.typing = True

# Render chat window
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)

# Show only last 6 messages (3 pairs), most recent at top (so reverse slice)
msgs_to_show = st.session_state.messages[-6:]
msgs_to_show.reverse()  # newest messages first

for msg in msgs_to_show:
    content = msg["content"]
    role = msg["role"]
    cls = "user" if role == "user" else "bot"

    if content is None and role == "bot":
        # Show typing animation container for bot message
        bot_container = st.empty()
        if st.session_state.typing:
            bot_typing_simulation(st.session_state.last_bot_reply, bot_container)
            # Replace placeholder content with actual reply in session_state
            # Update session_state messages to keep bot message content updated:
            for i in range(len(st.session_state.messages) - 1, -1, -1):
                if st.session_state.messages[i]["role"] == "bot" and st.session_state.messages[i]["content"] is None:
                    st.session_state.messages[i]["content"] = st.session_state.last_bot_reply
                    break
            st.session_state.typing = False
        else:
            bot_container.markdown(f'<div class="{cls}">{escape(st.session_state.last_bot_reply).replace("\\n","<br>")}</div>', unsafe_allow_html=True)
    else:
        # Normal rendering of messages
        st.markdown(f'<div class="{cls}">{escape(content).replace("\\n","<br>")}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
