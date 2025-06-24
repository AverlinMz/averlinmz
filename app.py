import streamlit as st
import random
import difflib

# — Page config for full-width layout —
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# — CSS for full-screen chat & bubbles —
st.markdown("""
<style>
body, .css-18e3th9 {  /* streamlit main container */
    padding: 0;
    margin: 0;
    background-color: #F7F9FA;
}
header, footer { display: none; }  /* hide header/footer */
#MainMenu, .css-1v3fvcr { visibility: hidden; }  /* hide menu bar */

.chat-window {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 60px;  /* leave space for input */
    overflow-y: auto;
    padding: 20px;
    box-sizing: border-box;
}
.chat-container {
    display: flex;
    flex-direction: column-reverse;  /* newest first */
    gap: 12px;
    max-width: 800px;
    margin: auto;
}
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
.input-area {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    padding: 10px 20px;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
}
input, button {
    font-family: 'Poppins', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# — Title (centered via layout), color changed to black —
st.markdown("<h1 style='color: black; text-align: center; font-family: Poppins;'>AverlinMz – Study Chatbot</h1>", unsafe_allow_html=True)

# Initialize history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fuzzy keyword helper
def contains_keyword(msg, keywords, cutoff=0.75):
    words = msg.split()
    for kw in keywords:
        if kw in msg:
            return True
        for w in words:
            if difflib.SequenceMatcher(None, w, kw).ratio() >= cutoff:
                return True
    return False

# Reply logic
def generate_reply(user_msg):
    msg = user_msg.lower()
    # Introduce
    if contains_keyword(msg, ["introduce","who are you","your name","about you","creator","who made you"]):
        return ("Hello! I’m AverlinMz, your study chatbot 🌱. "
                "My creator is Aylin Muzaffarli (b.2011, Azerbaijan). "
                "She loves music, programming, robotics, AI, physics, and more. "
                "Reach her at muzaffaraylin@gmail.com. Good luck!")
    # What can u/you do
    if contains_keyword(msg, ["what can you do","what you can do","what can u do"]):
        return ("I can cheer you on, share study tips (general or subject-specific!), "
                "and offer emotional support. Chat anytime you need a boost!")
    # Olympiad tips
    if contains_keyword(msg, ["olymp","olympuad"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Olympiad tips 💡: Study smart—focus on core concepts, practice past problems, "
                "review mistakes, and balance work with rest. Quality > quantity!")
    # Subject advice
    if contains_keyword(msg, ["biology"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Biology 🧬: Master cell structure, genetics, and ecology. Draw diagrams, "
                "use flashcards, and practice Olympiad questions.")
    if contains_keyword(msg, ["history"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("History 📜: Build timelines, practice structured essays, analyze sources, "
                "and quiz yourself on key dates.")
    if contains_keyword(msg, ["geography"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Geography 🌍: Interpret maps, memorize landforms, study case-studies, "
                "and practice spatial reasoning.")
    if contains_keyword(msg, ["language","english","russian"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Languages 🗣️: Read varied texts, listen actively, learn grammar contextually, "
                "and speak/write regularly to build fluency.")
    # Affection
    if contains_keyword(msg, ["i love you","i like you"]):
        return ("Aww, that warms my circuits! 💖 I’m here to support you anytime.")
    # Talk to me
    if contains_keyword(msg, ["talk to me"]):
        return ("I’m listening! 🎧 Tell me how your study is going or what’s on your mind.")
    # Greetings
    if contains_keyword(msg, ["hey","hi","hello","hrllo","helo"]):
        return ("Hey there! What are you studying right now? Starting is half the battle—you’ve done it!")
    # Emotional
    if contains_keyword(msg, ["tired","exhausted"]):
        return ("Feeling tired? 😴 Pause for a break—stretch, hydrate, breathe—and come back refreshed.")
    if contains_keyword(msg, ["sad","down","depressed","crying"]):
        return ("I’m sorry you’re feeling down 💙. Your feelings are valid, and I’m here with you.")
    if contains_keyword(msg, ["anxious","worried","panic","nervous"]):
        return ("Anxiety’s tough. Pause, breathe deeply, or take a 5-minute walk. One step at a time 🧘.")
    # Failure/doubt
    if contains_keyword(msg, ["failed","mistake","i can't","gave up"]):
        return ("Mistakes are lessons. 📚 They guide you forward—keep going!")
    # Celebration
    if contains_keyword(msg, ["i did it","solved it","success"]):
        return ("🎉 You did it! Celebrate this win—you earned it!")
    if contains_keyword(msg, ["good job","well done"]):
        return ("Thanks—but you’re the hero here. You put in the work!")
    if contains_keyword(msg, ["thank you","thanks"]):
        return ("You’re welcome! 😊 I’m proud of you. Come back any time.")
    # Help
    if contains_keyword(msg, ["help"]):
        return ("Of course—I’m here to assist or just listen. What’s up?")
    # Farewell
    if contains_keyword(msg, ["goodbye","bye","see ya","see you"]):
        return ("See you later 👋. Keep up the great work and return when you need a boost.")
    # Productivity
    if contains_keyword(msg, ["consistent","discipline","productive"]):
        return ("Discipline > motivation. Set micro-goals, track progress, forgive slip-ups.")
    if contains_keyword(msg, ["break","rest","sleep"]):
        return ("Rest is part of the process. 💤 A fresh mind learns faster.")
    if contains_keyword(msg, ["smart","study plan","study smarter"]):
        return ("Study smart: active recall, spaced repetition, and high-impact topics.")
    # Fallback
    replies = [
        "Keep going 💪. Every small effort counts.",
        "Progress > perfection—you’re doing great!",
        "Believe in your growth. One step at a time.",
        "You’ve got this 🌟. Keep moving forward.",
        "Struggle means growth. Be patient with yourself."
    ]
    return random.choice(replies)

# — Chat input form (enter to send) —
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="Write your message…")
    send = st.form_submit_button("Send")
    if send and user_input.strip():
        st.session_state.messages.insert(0, {"bot": generate_reply(user_input)})
        st.session_state.messages.insert(0, {"user": user_input})

# — Render chat window & bubbles —
st.markdown('<div class="chat-window">', unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f'<div class="user">{msg["user"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{msg["bot"]}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
