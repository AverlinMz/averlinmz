import streamlit as st
import random
import difflib

# --- CSS for chat bubbles ---
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;
}
.user {
    align-self: flex-end;
    background-color: #DCF8C6;
    padding: 8px 12px;
    border-radius: 15px 15px 0 15px;
    max-width: 80%;
    word-wrap: break-word;
}
.bot {
    align-self: flex-start;
    background-color: #F1F0F0;
    padding: 8px 12px;
    border-radius: 15px 15px 15px 0;
    max-width: 80%;
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)

st.title("AverlinMz – Study Chatbot")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper: fuzzy‐contains
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
                "My creator is Aylin Muzaffarli, born in 2011 in Azerbaijan. "
                "She’s into music, programming, robotics, AI, physics, and more. "
                "Questions? Reach her at muzaffaraylin@gmail.com. Good luck!")
    # 2) What can you do?
    if contains_keyword(msg, ["what can you do","what you can do"]):
        return ("I can cheer you on, give study tips, emotional support, and subject-specific advice. "
                "Just type your thoughts or questions anytime!")
    # 3) Affection
    if contains_keyword(msg, ["i love you","i like you"]):
        return ("Aww, that means a lot! 💖 I’m here to help you study and stay motivated anytime.")
    # 4) Talk to me
    if contains_keyword(msg, ["talk to me"]):
        return ("I’m all ears! 🎧 Tell me what’s on your mind or how your study went today.")
    # 5) Subject advice
    if contains_keyword(msg, ["biology"]) and contains_keyword(msg, ["advice","advise","prep"]):
        return ("Biology 🧬: Master cell structure, genetics, ecology. Draw diagrams, use flashcards, "
                "and practice past Olympiad problems.")
    if contains_keyword(msg, ["history"]) and contains_keyword(msg, ["advice","advise","prep"]):
        return ("History 📜: Build timelines, practice essays, use primary sources, and quiz key dates.")
    if contains_keyword(msg, ["geography"]) and contains_keyword(msg, ["advice","advise","prep"]):
        return ("Geography 🌍: Read maps, memorize landmarks, study case-studies, and practice spatial questions.")
    if contains_keyword(msg, ["language","english","russian"]) and contains_keyword(msg, ["advice","advise","prep"]):
        return ("Languages 🗣️: Read varied texts, do listening practice, learn grammar in context, "
                "and speak or write regularly for fluency.")
    # 6) Greetings
    if contains_keyword(msg, ["hey","hi","hello","hrllo","helo","yo"]):
        return ("Hey there! What are you studying right now? "
                "Starting is half the battle — you’ve already won that part!")
    # 7) Emotional support
    if contains_keyword(msg, ["tired","exhausted"]):
        return ("Feeling tired? 😴 Take a short break—stretch, hydrate, breathe—and come back refreshed.")
    if contains_keyword(msg, ["sad","down","depressed","crying"]):
        return ("I’m sorry you’re feeling that way 💙. It’s okay to feel sad; you’ve got support here.")
    if contains_keyword(msg, ["anxious","worried","panic","nervous"]):
        return ("Anxiety is tough. Pause, breathe, or take a 5-minute walk. One step at a time 🧘‍♀️.")
    # 8) Failure & doubt
    if contains_keyword(msg, ["failed","mistake","i can't","gave up"]):
        return ("Every mistake teaches you something. 📚 Failure is feedback, not final. Keep going!")
    # 9) Celebration & gratitude
    if contains_keyword(msg, ["i did it","solved it","success"]):
        return ("🎉 Congratulations! Hard work paid off—celebrate this win, you earned it!")
    if contains_keyword(msg, ["good job","well done"]):
        return ("Thank you! But you’re the one doing the hard work. 💪")
    if contains_keyword(msg, ["thank you","thanks"]):
        return ("You’re welcome! 😊 Keep shining, and drop by any time.")
    # 10) Help & check-ins
    if contains_keyword(msg, ["help"]):
        return ("Sure—I’m here to help or just listen. What’s up?")
    # 11) Farewells
    if contains_keyword(msg, ["goodbye","bye","see ya","see you"]):
        return ("See you later! 👋 Keep up the great work, and come back whenever you need a boost.")
    # 12) Olympiad advice
    if contains_keyword(msg, ["olympiad","olympiads","olympiad prep"]) and contains_keyword(msg, ["prepare","advice","advise"]):
        return ("Olympiad prep 💡: Study smart—focus on concepts, practice past problems, review mistakes, "
                "and balance rest with work. Quality > quantity!")
    # 13) Productivity & planning
    if contains_keyword(msg, ["consistent","discipline","productive"]):
        return ("Discipline > motivation. Set tiny daily goals, reflect weekly, and forgive slip-ups.")
    if contains_keyword(msg, ["break","rest","sleep"]):
        return ("Rest is part of the plan. 💤 A well-rested mind learns faster.")
    if contains_keyword(msg, ["smart","study plan","study smarter"]):
        return ("Smart study means active recall, spaced repetition, and prioritizing high-impact topics.")
    # 14) Fallback motivational
    replies = [
        "Keep going 💪. Every small effort adds up.",
        "Progress > perfection. You’re doing amazing!",
        "Believe in your growth. Your journey unfolds one step at a time.",
        "You’ve got this 🌟. One more problem, one more fact—keep going.",
        "Struggle means you’re learning. Be patient with yourself."
    ]
    return random.choice(replies)

# Chat input & display
user_input = st.text_input("Write your message:")
if st.button("Send") and user_input.strip():
    st.session_state.messages.insert(0, {"bot": generate_reply(user_input)})
    st.session_state.messages.insert(0, {"user": user_input})

# Render bubbles
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f'<div class="user">{msg["user"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{msg["bot"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
