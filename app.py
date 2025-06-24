import streamlit as st
import random
import difflib

# — Page config —
st.set_page_config(
    page_title="AylinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# — CSS styling —
st.markdown("""
<style>
/* Hide Streamlit UI */
header, footer { display: none !important; }
#MainMenu { visibility: hidden !important; }

/* Welcome title styling */
.welcome {
    padding-top: 20px;
    text-align: center;
    font-family: 'Poppins', sans-serif;
    font-size: 24px;
    color: #000;
    font-weight: 600;
}

/* Full-screen chat window */
.chat-window {
    position: fixed;
    top: 120px; /* space below welcome */
    left: 0;
    right: 0;
    bottom: 100px; /* space above input */
    overflow-y: auto;
    padding: 20px 0;
    background-color: #F7F9FA;
    box-sizing: border-box;
    z-index: 0;
}

.chat-container {
    display: flex;
    flex-direction: column-reverse; /* newest messages at top */
    gap: 12px;
    max-width: 800px;
    margin: auto;
}

/* User bubble */
.user {
    align-self: flex-end;
    background-color: #D1F2EB;
    color: #0B3D2E;
    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;
    font-family: 'Poppins', sans-serif;
    max-width: 80%;
    word-wrap: break-word;
}

/* Bot bubble */
.bot {
    align-self: flex-start;
    background-color: #EFEFEF;
    color: #333333;
    padding: 10px 14px;
    border-radius: 16px 16px 16px 4px;
    font-family: 'Poppins', sans-serif;
    max-width: 80%;
    word-wrap: break-word;
}

/* Input area fixed at bottom */
.input-area {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #FFFFFF;
    padding: 10px 20px;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 8px;
    box-sizing: border-box;
    z-index: 10;
}
</style>
""", unsafe_allow_html=True)

# — Welcome title —
st.markdown('<div class="welcome">👋 Welcome to <b>AylinMz</b> – your motivational study companion!</div>', unsafe_allow_html=True)

# — Initialize conversation history in session —
if "messages" not in st.session_state:
    st.session_state.messages = []

# — Helper function for fuzzy keyword matching —
def contains_keyword(msg, keywords, cutoff=0.75):
    words = msg.split()
    for kw in keywords:
        if kw in msg:
            return True
        for w in words:
            if difflib.SequenceMatcher(None, w, kw).ratio() >= cutoff:
                return True
    return False

# — The main chatbot reply logic, with all your conditions included —
def generate_reply(user_msg):
    msg = user_msg.lower()

    # 1) Introduce / creator
    if contains_keyword(msg, ["introduce","who are you","your name","about you","creator","who made you"]):
        return ("Hello! I’m AverlinMz, your study chatbot 🌱. "
                "My creator is Aylin Muzaffarli (b.2011, Azerbaijan). "
                "She loves music, programming, robotics, AI, physics, and more. "
                "Reach her at muzaffaraylin@gmail.com. Good luck!")

    # 2) What can you do?
    if contains_keyword(msg, ["what can you do","what you can do","what can u do"]):
        return ("I can cheer you on, share study tips (general or subject-specific!), "
                "and offer emotional support. Chat anytime you need a boost!")

    # 3) Olympiad tips (typo‐tolerant)
    if contains_keyword(msg, ["olymp","olympuad"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Olympiad tips 💡: Study smart—focus on core concepts, practice past problems, "
                "review mistakes, and balance work with rest. Quality > quantity!")

    # 4) Subject-specific advice
    if contains_keyword(msg, ["biology"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Biology 🧬: Master cell structure, genetics, and ecology. Draw diagrams, "
                "use flashcards, and practice Olympiad questions.")
    if contains_keyword(msg, ["history"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("History 📜: Build timelines, practice structured essays, analyze sources, "
                "and quiz yourself on key dates.")
    if contains_keyword(msg, ["geography"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Geography 🌍: Read maps, memorize landforms, study case-studies, "
                "and practice spatial reasoning.")
    if contains_keyword(msg, ["language","english","russian"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Languages 🗣️: Read diverse texts, listen actively, learn grammar in context, "
                "and practice speaking or writing regularly.")

    # 5) Affection
    if contains_keyword(msg, ["i love you","i like you"]):
        return ("Aww, that warms my circuits! 💖 I’m here whenever you need support.")

    # 6) Talk to me
    if contains_keyword(msg, ["talk to me"]):
        return ("I’m listening! 🎧 Tell me how your study is going or what’s on your mind.")

    # 7) Greetings
    if contains_keyword(msg, ["hey","hi","hello","hrllo","helo"]):
        return ("Hey there! What are you studying right now? Starting is half the battle—you’ve done it!")

    # 8) Emotional support
    if contains_keyword(msg, ["tired","exhausted"]):
        return ("Feeling tired? 😴 Take a break—stretch, hydrate, breathe—and come back refreshed.")
    if contains_keyword(msg, ["sad","down","depressed","crying"]):
        return ("I’m sorry you’re feeling that way 💙. You’re not alone—take it one step at a time.")
    if contains_keyword(msg, ["anxious","worried","panic","nervous"]):
        return ("Anxiety is tough. Pause, breathe, or take a short walk 🧘.")

    # 9) Failure & doubt
    if contains_keyword(msg, ["failed","mistake","i can't","gave up"]):
        return ("Every mistake teaches you something 📚. Failure is feedback—keep going!")

    # 10) Celebration & gratitude
    if contains_keyword(msg, ["i did it","solved it","success"]):
        return ("🎉 Congrats! You did amazing—celebrate this win!")
    if contains_keyword(msg, ["good job","well done"]):
        return ("Thanks—you’re the one working hard! 💪")
    if contains_keyword(msg, ["thank you","thanks"]):
        return ("You’re welcome! 😊 Keep shining.")

    # 11) Help
    if contains_keyword(msg, ["help"]):
        return ("Sure—I’m here. What’s on your mind?")

    # 12) Farewells
    if contains_keyword(msg, ["goodbye","bye","see ya","see you"]):
        return ("See you later! 👋 Come back anytime you need a boost.")

    # 13) Productivity & planning
    if contains_keyword(msg, ["consistent","discipline","productive"]):
        return ("Discipline > motivation. Set micro-goals, track progress, forgive slip-ups.")
    if contains_keyword(msg, ["break","rest","sleep"]):
        return ("Rest is part of the plan 💤. A fresh mind learns better.")
    if contains_keyword(msg, ["smart","study plan","study smarter"]):
        return ("Smart study: active recall, spaced repetition, and focus on key topics.")

    # 14) Fallback motivational replies
    fallback_replies = [
        "Keep going 💪. Every small effort counts.",
        "Progress > perfection—you’re doing great!",
        "Believe in your growth—one step at a time.",
        "You’ve got this 🌟. Keep moving forward.",
        "Struggle means growth. Be patient with yourself."
    ]
    return random.choice(fallback_replies)

# — Input area (fixed at bottom) —
st.markdown('<div class="input-area">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="Write your message…", key="inp")
    send = st.form_submit_button("Send")
    if send and user_input.strip():
        # Add user message then bot reply on top of chat history
        st.session_state.messages.insert(0, {"user": user_input})
        st.session_state.messages.insert(0, {"bot": generate_reply(user_input)})
st.markdown('</div>', unsafe_allow_html=True)

# — Chat window displaying conversation —
st.markdown('<div class="chat-window"><div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f'<div class="user">{msg["user"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{msg["bot"]}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
