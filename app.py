# Add this to your app.py after imports
def load_css():
    with open("globals.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call it in your main app
load_css()
