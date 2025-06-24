import streamlit as st
import random

# Project name
st.title("AverlinMz - Your Study Companion")

# Motivational replies in English
replies = [
    "Great job! Keep up the amazing work.",
    "Consistency is key, you're doing fantastic!",
    "Every step counts.",
    "Take breaks and keep your balance.",
    "You are improving every day!",
    "Your dedication is inspiring — keep pushing forward!",
    "Small progress is still progress. Well done!",
    "Believe in yourself; you're capable of amazing things.",
    "Keep going! Success is just around the corner.",
    "Remember, rest fuels productivity. Take care of yourself.",
    "Your effort today builds your tomorrow.",
    "Stay positive and focused — you've got this!"
]

# Text input for study journal
entry = st.text_area("Write about your study session", height=150)

# When user submits entry
if st.button("Get Motivational Reply"):
    if entry.strip() == "":
        st.warning("Please write something about your study first!")
    else:
        # Pick random reply from English replies
        response = random.choice(replies)
        st.success(response)
