import streamlit as st
import random
import difflib

# — Page config & brand theme —
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="centered"
)

# — CSS for interface & chat bubbles —
st.markdown("""
<style>
body {
    background-color: #F7F9FA;
}
h1 {
    color: #3CA887;  /* brand green */
    text-align: center;
    font-family: 'Poppins', sans-serif;
}
.chat-container {
    max-width: 600px;
    margin: auto;
    display: flex;
    flex-direction: column-reverse; /* newest first */
    gap: 12px;
    padding: 16px;
    background: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.user {
    align-self: flex-end;
    background-color: #D1F2EB;  /* light teal */
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
input, button {
    font-family: 'Poppins', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.title("AverlinMz – Study Chatbot")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fuzzy‐match helper
def contains_keyword(msg, keywords, cutoff=0.75):
    words = msg.split()
    for kw in keywords:
        if kw in msg:
            return True
        for w in words:
            if difflib.SequenceMatcher(None, w, kw).ratio() >= cutoff:
                return True
    return False

def generate_reply(user_msg):
    msg = user_msg.lower()

    # 1) Introduce / creator
    if contains_keyword(msg, ["introduce","who are you","your name","about you","creator","who made you"]):
        return ("Hello! I’m AverlinMz, your study chatbot 🌱. "
                "My creator is Aylin Muzaffarli (b.2011, Azerbaijan). "
                "She loves music, programming, robotics, AI, physics, and more. "
                "For questions: muzaffaraylin@gmail.com. Good luck!")

    # 2) What can you do?
    if contains_keyword(msg, ["what can you do","what you can do"]):
        return ("I can cheer you on, share study tips (even subject-specific!), "
                "and offer emotional support. Just type whenever you need a boost!")

    # 3) Olympiad tips (typo-tolerant + “tip(s)”)
    if contains_keyword(msg, ["olymp","olympuad"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Olympiad tips 💡: Study smart — focus on concepts, not just problems. "
                "Quality of work = Focus × Time. Practice past problems, review mistakes, "
                "and keep balance with rest.")
    
    # 4) Subject-specific advice
    if contains_keyword(msg, ["biology"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Biology 🧬: Master cell structure, genetics, ecology. Draw diagrams, "
                "use flashcards, and solve past Olympiad questions.")
    if contains_keyword(msg, ["history"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("History 📜: Build timelines, practice structured essays, analyze primary sources, "
                "and quiz yourself on key dates.")
    if contains_keyword(msg, ["geography"]) and contains_keyword(msg, ["tip","tips","advise","advice"]):
        return ("Geography 🌍: Read and interpret maps, memorize major landforms, "
                "study case-studies, and practice spatial questions.")
    if (contains_keyword(msg, ["language","english","russian"]) 
        and contains_keyword(msg, ["tip","tips","advise","advice"])):
        return ("Languages 🗣️: Read diverse texts, listen actively, learn grammar in context, "
                "and practice speaking or writing regularly.")
    
    # 5) Affection
    if contains_keyword(msg, ["i love you","i like you"]):
        return ("Aww, thanks! 💖 I’m here to keep you motivated whenever you need.")

    # 6) Talk to me
    if contains_keyword(msg, ["talk to me"]):
        return ("I’m all ears! 🎧 Tell me what’s on your mind or how your study went.")

    # 7) Greetings
    if contains_keyword(msg, ["hey","hi","hello","hrllo","helo"]):
        return ("Hey there! What are you studying right now? "
                "Starting is half the battle — you’ve already done that!")

    # 8) Emotional support
    if contains_keyword(msg, ["tired","exhausted"]):
        return ("Feeling tired? 😴 Take a short break—stretch, hydrate, breathe—and return refreshed.")
    if contains_keyword(msg, ["sad","down","depressed","crying"]):
        return ("I’m sorry you’re feeling that way 💙. It’s okay to feel sad; you’ve got support here.")
    if contains_keyword(msg, ["anxious","worried","panic","nervous"]):
        return ("Anxiety can be tough. Pause, breathe, or take a 5-minute walk. One step at a time 🧘.")

    # 9) Failure & doubt
    if contains_keyword(msg, ["failed","mistake","i can't","gave up"]):
        return ("Every mistake teaches you something. 📚 Failure is feedback, not final. Keep going!")
    
    # 10) Celebration & gratitude
    if contains_keyword(msg, ["i did it","solved it","success"]):
        return ("🎉 Congrats! Your hard work paid off—celebrate this win, you earned it!")
    if contains_keyword(msg, ["good job","well done"]):
        return ("Thanks! But the real credit is yours—you put in the effort 💪.")
    if contains_keyword(msg, ["thank you","thanks"]):
        return ("You’re welcome! 😊 Keep shining, and come back anytime.")

    # 11) Help & check-ins
    if contains_keyword(msg, ["help"]):
        return ("Sure—I’m here to help or just listen. What’s up?")

    # 12) Farewells
    if contains_keyword(msg, ["goodbye","bye","see ya","see you"]):
        return ("See ya! 👋 Keep up the great work, and return when you need a boost.")

    # 13) Productivity & planning
    if contains_keyword(msg, ["consistent","discipline","productive"]):
        return ("Discipline > motivation. Set tiny daily goals, reflect weekly, and forgive slip-ups.")
    if contains_keyword(msg, ["break","rest","sleep"]):
        return ("Rest is part of the plan. 💤 A well-rested mind learns faster.")
    if contains_keyword(msg, ["smart","study plan","study smarter"]):
        return ("Study smart: active recall, spaced repetition, and focus on high-impact topics.")

    # 14) Fallback motivational
    replies = [
        "Keep going 💪. Every small effort adds up.",
        "Progress > perfection. You’re doing amazing!",
        "Believe in your growth. One step at a time.",
        "You’ve got this 🌟. Keep moving forward.",
        "Struggle means growth. Be patient with yourself."
    ]
    return random.choice(replies)

# — Chat form (allows Enter to send) —
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message:", "")
    send = st.form_submit_button("Send")
    if send and user_input.strip():
        st.session_state.messages.insert(0, {"bot": generate_reply(user_input)})
        st.session_state.messages.insert(0, {"user": user_input})

# — Display chat bubbles —
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f'<div class="user">{msg["user"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{msg["bot"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
