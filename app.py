import streamlit as st
import random

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

def generate_reply(user_msg):
    msg = user_msg.lower()

    # 1) Introduce / creator
    if any(x in msg for x in ["introduce", "who are you", "your name", "about you", "creator", "who made you"]):
        return ("Hello! I’m AverlinMz, your study chatbot 🌱. "
                "My creator is Aylin Muzaffarli, born in 2011 in Azerbaijan. "
                "She's into music, programming, robotics, AI, physics, and more. "
                "Questions? Reach her at muzaffaraylin@gmail.com. Good luck!")
    # 2) What can you do?
    if "what can you do" in msg or "what you can do" in msg:
        return ("I can cheer you on, give study tips, emotional support, and subject-specific advice. "
                "Just type your thoughts or questions anytime!")
    # 3) Affection
    if any(x in msg for x in ["i love you", "i like you"]):
        return ("Aww, that means a lot! 💖 I’m here to help you study and stay motivated anytime.")
    # 4) Talk to me
    if "talk to me" in msg:
        return ("I’m all ears! 🎧 Tell me what’s on your mind or how your study went today.")
    # 5) Subject-specific Olympiad advice
    if "prep for biology" in msg or ("biology" in msg and "advice" in msg):
        return ("Biology tips 🧬: Master the core concepts (cell, genetics, ecology), "
                "practice diagram drawing, review past Olympiad problems, and make flashcards for terms.")
    if "history" in msg and "advice" in msg:
        return ("History tips 📜: Create timelines, practice writing structured essays, "
                "use primary sources, and quiz yourself on key dates and events.")
    if "geography" in msg and "advice" in msg:
        return ("Geography tips 🌍: Learn to read maps, memorize key physical features, "
                "understand case studies, and practice spatial reasoning questions.")
    if ("language" in msg or "english" in msg or "russian" in msg) and "advice" in msg:
        return ("Language learning tips 🗣️: Read varied texts, do listening practice, "
                "learn grammar in context, and speak or write regularly to build fluency.")
    # 6) Greetings (including common typos)
    if any(greet in msg for greet in ["hey", "hi", "hello", "hrllo", "helo"]):
        return ("Hey there! What are you studying right now? "
                "Starting is half the battle — you’ve already won that part!")
    # 7) Emotional support
    if any(word in msg for word in ["tired", "exhausted"]):
        return ("Feeling tired? 😴 Take a short break—stretch, hydrate, breathe—and come back refreshed.")
    if any(word in msg for word in ["sad", "down", "depressed", "crying"]):
        return ("I’m sorry you’re feeling that way 💙. It’s okay to feel sad; you’ve got support here.")
    if any(word in msg for word in ["anxious", "worried", "panic", "nervous"]):
        return ("Anxiety is tough. Try a breathing exercise or a 5-minute walk. One step at a time 🧘‍♀️.")
    # 8) Failure & doubt
    if any(word in msg for word in ["failed", "mistake", "i can't", "gave up"]):
        return ("Every mistake teaches you something. 📚 Failure is feedback, not final. Keep at it!")
    # 9) Celebration & gratitude
    if any(word in msg for word in ["i did it", "solved it", "success"]):
        return ("🎉 Congratulations! Your hard work paid off—celebrate this win, you earned it!")
    if any(word in msg for word in ["good job", "well done"]):
        return ("Thank you, but the real credit is yours—you’re putting in the effort every day! 💪")
    if any(word in msg for word in ["thank you", "thanks"]):
        return ("You’re welcome! 😊 Keep shining, and don’t hesitate to drop by again.")
    # 10) Help & check-ins
    if "help" in msg:
        return ("Sure—I’m here for help or just to listen. What’s on your mind today?")
    # 11) Farewells
    if any(bye in msg for bye in ["goodbye", "bye", "see ya", "see you"]):
        return ("See you later! 👋 Keep up the great work, and come back anytime you need a boost.")
    # 12) General Olympiad advice
    if "advice" in msg or ("prepare" in msg and "olympiad" in msg):
        return ("Olympiad prep 💡: Study smart—focus on concepts, practice past problems, "
                "review your mistakes, and balance rest with work. Quality > quantity!")
    # 13) Productivity & planning
    if any(word in msg for word in ["consistent", "discipline", "productive"]):
        return ("Discipline > motivation. Set tiny daily goals, track progress, and forgive slip-ups.")
    if any(word in msg for word in ["break", "rest", "sleep"]):
        return ("Rest is part of the plan. 💤 A well-rested mind retains more and learns faster.")
    if any(word in msg for word in ["smart", "study plan", "study smarter"]):
        return ("Smart study means prioritizing high-value topics, active recall, and spaced repetition.")
    # 14) Fallback motivational
    replies = [
        "Keep going 💪. Every small effort adds up to big results.",
        "Progress > perfection. You’re doing amazing!",
        "Believe in your growth. Your journey is unfolding one step at a time.",
        "You’ve got this 🌟. Just one more problem, one more paragraph—keep moving forward.",
        "Struggle means you’re learning. Be patient with yourself."
    ]
    return random.choice(replies)


# Chat input & display
user_input = st.text_input("Write your message:")
if st.button("Send") and user_input.strip():
    st.session_state.messages.insert(0, {"bot": generate_reply(user_input)})
    st.session_state.messages.insert(0, {"user": user_input})

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f'<div class="user">{msg["user"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{msg["bot"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
