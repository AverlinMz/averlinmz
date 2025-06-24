import streamlit as st
import random

st.title("AverlinMz - Study Chatbot")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

def generate_reply(user_msg):
    msg = user_msg.lower()

    if any(greet in msg for greet in ["hey", "hi", "hello", "yo"]):
        return ("Hey! I'm here for you. What are you studying today? "
                "Remember, taking the first step is the hardest — but you got this!")
    
    elif any(x in msg for x in ["introduce", "who are you", "your name", "about you", "creator", "who made you"]):
    return ("Hello. My name is AverlinMz, your study chatbot. "
            "My creator is Aylin Muzaffarli, born in 2011 in Azerbaijan. "
            "She's passionate about music, programming, robotics, AI, physics, top universities, and more. "
            "If you have questions, you can write to: muzaffaraylin@gmail.com. Good luck!")


    elif "tired" in msg or "exhausted" in msg:
        return ("It's okay to feel tired. Rest is part of the process. "
                "Take a short break, hydrate, and come back stronger!")

    elif "sad" in msg or "down" in msg or "depressed" in msg:
        return ("I'm sorry you're feeling that way. Just know you're not alone. "
                "Take it one breath at a time. You're doing better than you think.")

    elif "overwhelmed" in msg or "burned out" in msg or "can't do it" in msg:
        return ("You’re trying your best, and that’s enough. Take a deep breath. "
                "Simplify your to-do list and focus on just one small win today.")

    elif "i did it" in msg or "solved it" in msg or "success" in msg:
        return ("Yesss! I'm proud of you! Hard work really does pay off. "
                "Keep up the great momentum!")

    elif "good job" in msg or "well done" in msg:
        return ("Thank you! But remember — it's you who's putting in the real work. "
                "I'm just here to cheer you on!")

    elif "help" in msg:
        return ("Of course, I'm here to help. Ask me anything or just type how you're feeling.")

    elif "creator" in msg or "ok, i m ur creator" in msg:
        return ("Aylin! You're the mind behind this. I'm honored to exist because of you. "
                "Keep building cool things — the world needs your ideas!")

    elif any(bye in msg for bye in ["goodbye", "bye", "see ya", "see you"]):
        return ("See you soon! Keep doing your best, take care, and come back when you need a boost!")

    elif "advise" in msg or "advice" in msg or ("prepare" in msg and "olympiad" in msg):
        return ("Great question! Here's some Olympiad advice: "
                "Study smart, not just hard. Quality matters more than quantity. "
                "Quality of your work = focus × time. Rest, reflect, and focus on deep understanding. You've got this!")

    elif "consistent" in msg or "discipline" in msg or "productive" in msg:
        return ("Consistency is built from small, daily actions. "
                "Set small goals, reflect weekly, and celebrate even tiny wins. "
                "You don’t need motivation — just systems!")

    elif "break" in msg or "rest" in msg or "sleep" in msg:
        return ("Rest is not a weakness — it's a strategy. "
                "Sleep sharpens your focus and boosts memory. Take breaks without guilt.")

    elif "smart" in msg or "study plan" in msg:
        return ("Smart studying means setting priorities, reducing distractions, and reviewing often. "
                "Don’t aim for perfection — aim for clarity and consistency.")

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

# User input
user_input = st.text_input("Write your message:")

if st.button("Send"):
    if user_input.strip() != "":
        st.session_state.messages.append({"user": user_input})
        reply = generate_reply(user_input)
        st.session_state.messages.append({"bot": reply})

# Display conversation history
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f"**You:** {msg['user']}")
    else:
        st.markdown(f"**Bot:** {msg['bot']}")
