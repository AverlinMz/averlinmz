import streamlit as st
import random

st.title("AverlinMz - Study Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

def generate_reply(user_msg):
    replies = [
        "Keep going, you're doing great!",
        "Don't forget to take breaks!",
        "Your hard work will pay off!",
        "Every step counts!",
        "Believe in yourself!"
    ]
    return random.choice(replies)

user_input = st.text_input("Write your message:")

if st.button("Send"):
    if user_input.strip() != "":
        st.session_state.messages.append({"user": user_input})
        reply = generate_reply(user_input)
        st.session_state.messages.append({"bot": reply})

for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f"**You:** {msg['user']}")
    else:
        st.markdown(f"**Bot:** {msg['bot']}")
