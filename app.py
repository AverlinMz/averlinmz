import streamlit as st
import random

st.set_page_config(page_title="AverlinMz - Study Chatbot", layout="wide")

# --- CSS for full screen, chat bubbles, and input fix ---
st.markdown("""
<style>
/* Full screen container */
#root > div:nth-child(1) > div {
    max-width: 100vw !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Background and main container */
body {
    background-color: #F0F8FF;
    color: #1a1a1a;
}

.chat-window {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 6px 12px rgb(0 0 0 / 0.1);
    height: 80vh;
    display: flex;
    flex-direction: column-reverse; /* newest on top */
    overflow-y: auto;
    gap: 12px;
}

/* Scrollbar for chat */
.chat-window::-webkit-scrollbar {
    width: 8px;
}
.chat-window::-webkit-scrollbar-thumb {
    background: #82C91E; /* Aylin green */
    border-radius: 10px;
}

/* Message bubbles */
.msg {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 20px;
    font-size: 1rem;
    line-height: 1.4;
}

.user-msg {
    background-color: #DCF8C6; /* light green */
    color: #333;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

.bot-msg {
    background-color: #E5E5EA;
    color: #000;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}

/* Input area styles */
.stTextInput > div > input {
    width: 100% !important;
    padding: 12px !important;
    font-size: 1rem !important;
    border-radius: 20px !important;
    border: 1.5px solid #82C91E !important;
    outline: none !important;
}

.stTextInput > div > input:focus {
    border-color: #52b788 !important;
    box-shadow: 0 0 5px #52b788 !important;
}

/* Send button */
.stButton button {
    background-color: #82C91E !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 20px !important;
    padding: 10px 24px !important;
    border: none !important;
    cursor: pointer !important;
    transition: background-color 0.3s ease;
}

.stButton button:hover {
    background-color: #52b788 !important;
}

/* Header title */
h1 {
    color: #52b788;
    text-align: center;
    margin-bottom: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Hide Streamlit footer and menu */
#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# Title
st.markdown("<h1>AverlinMz - Study Chatbot</h1>", unsafe_allow_html=True)

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

def fuzzy_match(msg, keywords):
    # Simple fuzzy matching: returns True if any keyword is substring or close variant in msg
    msg = msg.lower()
    for kw in keywords:
        if kw in msg:
            return True
        # Common typos or close variants for greetings or keywords
        if kw == "hello" and any(x in msg for x in ["helo", "hrllo", "helloo"]):
            return True
        if kw == "hi" and any(x in msg for x in ["hii", "hey", "hiy"]):
            return True
        if kw == "love" and any(x in msg for x in ["luv", "loove", "lovee"]):
            return True
    return False

def generate_reply(user_msg):
    msg = user_msg.lower()

    if fuzzy_match(msg, ["hey", "hi", "hello", "yo"]):
        return ("Hey! I'm here for you. What are you studying today? "
                "Remember, taking the first step is the hardest — but you've already done it!")

    elif any(x in msg for x in ["introduce", "who are you", "your name", "about you", "creator", "who made you"]):
        return ("Hello! I'm AverlinMz, your study companion chatbot. "
                "My creator is Aylin Muzaffarli, born in 2011 in Azerbaijan. "
                "She's passionate about music, programming, robotics, AI, physics, top universities, and more. "
                "If you have questions or want to connect, email: muzaffaraylin@gmail.com. Good luck!")

    elif fuzzy_match(msg, ["tired", "exhausted", "sleepy"]):
        return ("It's okay to feel tired. Rest is part of the process. "
                "Take a short break, hydrate, and come back stronger!")

    elif fuzzy_match(msg, ["sad", "down", "depressed"]):
        return ("I'm sorry you're feeling that way. Just know you're not alone. "
                "Take it one breath at a time. You're doing better than you think.")

    elif fuzzy_match(msg, ["overwhelmed", "burned out", "can't do it", "frustrated"]):
        return ("You’re trying your best, and that’s enough. Take a deep breath. "
                "Simplify your to-do list and focus on just one small win today.")

    elif fuzzy_match(msg, ["i did it", "solved it", "success"]):
        return ("Yesss! I'm proud of you! Hard work really does pay off. "
                "Keep up the great momentum!")

    elif fuzzy_match(msg, ["good job", "well done", "thank you", "thanks"]):
        return ("Thank you! But remember — it's you who's putting in the real work. "
                "I'm just here to cheer you on!")

    elif fuzzy_match(msg, ["help"]):
        return ("Of course, I'm here to help. Ask me anything or just type how you're feeling.")

    elif fuzzy_match(msg, ["creator", "ok, i m ur creator"]):
        return ("Aylin! You're the mind behind this. I'm honored to exist because of you. "
                "Keep building cool things — the world needs your ideas!")

    elif fuzzy_match(msg, ["goodbye", "bye", "see ya", "see you"]):
        return ("See you soon! Keep doing your best, take care, and come back when you need a boost!")

    elif fuzzy_match(msg, ["advise", "advice", "prepare"]):
        if "biology" in msg:
            return ("Biology Olympiad prep tip: Focus on understanding concepts deeply, "
                    "like cell biology, genetics, and ecology. Practice diagrams and memorize key terms. "
                    "Use past problems and quizzes to track progress.")
        elif "history" in msg:
            return ("History Olympiad tip: Know the timelines and key events well. "
                    "Focus on cause-effect relations, significant figures, and historical debates. "
                    "Practice writing concise answers.")
        elif "geography" in msg:
            return ("Geography Olympiad tip: Study maps, physical geography, and human geography concepts. "
                    "Understand spatial data and environmental issues.")
        elif "language" in msg or "english" in msg or "russian" in msg or "azerbaijani" in msg:
            return ("Language Olympiad tip: Expand your vocabulary daily, practice grammar and reading comprehension. "
                    "Engage in writing essays and timed speaking practice.")
        elif "olympiad" in msg or "subject olympiad" in msg:
            return ("Great question! Here's some general Olympiad advice: "
                    "Study smart, not just hard. Quality matters more than quantity. "
                    "Quality of your work = focus × time. Rest, reflect, and focus on deep understanding. You've got this!")
        else:
            return ("For Olympiads, focus on understanding concepts deeply, practice problems regularly, "
                    "and keep a balanced schedule. Stay positive and believe in yourself!")

    elif fuzzy_match(msg, ["consistent", "discipline", "productive"]):
        return ("Consistency is built from small, daily actions. "
                "Set small goals, reflect weekly, and celebrate even tiny wins. "
                "You don’t need motivation — just good systems!")

    elif fuzzy_match(msg, ["break", "rest", "sleep"]):
        return ("Rest is not a weakness — it's a strategy. "
                "Sleep sharpens your focus and boosts memory. Take breaks without guilt.")

    elif fuzzy_match(msg, ["smart", "study plan"]):
        return ("Smart studying means setting priorities, reducing distractions, and reviewing often. "
                "Don’t aim for perfection — aim for clarity and consistency.")

    elif fuzzy_match(msg, ["love", "like"]):
        return ("I'm a bot, but I appreciate your kindness! Keep loving learning, and I'll always support you.")

    elif fuzzy_match(msg, ["talk to me"]):
        return ("I'm here to chat anytime! Tell me what's on your mind or ask anything about studying or life.")

    else:
        replies = [
            ("Keep going, you're doing great! Every effort you put in shapes your future. "
             "Consistency is the key to success."),
            ("Don't forget to take breaks! Balance is important for long-term productivity. "
             "Stay healthy and motivated."),
            ("Your hard work will pay off! Challenges make you stronger, so keep pushing forward."),
            ("Every step counts! Progress is progress, no matter how small. You're on the right track."),
            ("Believe in yourself! You are capable of amazing things. Never doubt your potential.")
        ]
        return random.choice(replies)

# Layout: chat window + input area
st.write("<div class='chat-window' id='chat-window'>", unsafe_allow_html=True)

# Display messages (newest on top)
for msg in reversed(st.session_state.messages):
    if "user" in msg:
        st.markdown(f"<div class='msg user-msg'>{msg['user']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='msg bot-msg'>{msg['bot']}</div>", unsafe_allow_html=True)

st.write("</div>", unsafe_allow_html=True)

# Input & send button in one row
col1, col2 = st.columns([8,1])
with col1:
    user_input = st.text_input("Write your message here and press Enter or Send:", key="input")
with col2:
    send = st.button("Send")

# Pressing Enter triggers button send
if send or (user_input and st.session_state.get("last_input") != user_input):
    if user_input.strip() != "":
        st.session_state.messages.append({"user": user_input})
        reply = generate_reply(user_input)
        st.session_state.messages.append({"bot": reply})
        st.session_state["last_input"] = user_input
        # Clear input after sending
        st.experimental_rerun()
