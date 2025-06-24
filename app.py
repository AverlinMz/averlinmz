import streamlit as st
import random

st.title("AverlinMz - Study Chatbot")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

def generate_reply(user_msg):
    msg = user_msg.lower()
    if any(greet in msg for greet in ["hey", "hi", "hello", "yo"]):
        return "Hey! I'm here for you. What are you studying today?"
    elif "tired" in msg or "exhausted" in msg:
        return "It's okay to rest sometimes. Take a short break and come back stronger!"
    elif "sad" in msg or "down" in msg:
        return "I’m sorry you’re feeling down. Remember, tough times don’t last!"
    elif "good job" in msg or "well done" in msg:
        return "Thank you! Your progress inspires me too."
    elif "help" in msg:
        return "I’m here to support you. What do you need help with?"
    else:
        # Default motivational replies
        replies = [
            "Keep going, you're doing great!",
            "Don't forget to take breaks!",
            "Your hard work will pay off!",
            "Every step counts!",
            "Believe in yourself!"
        ]
        return random.choice(replies)

# User input
user_input = st.text_input("Write your message:")

if st.button("Send"):
    if user_input.strip() != "":
        # Add user message to history
        st.session_state.messages.append({"user": user_input})
        # Generate bot reply
        reply = generate_reply(user_input)
        st.session_state.messages.append({"bot": reply})

# Display conversation history
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f"**You:** {msg['user']}")
    else:
        st.markdown(f"**Bot:** {msg['bot']}")
