import streamlit as st
from groq import Groq

# Set up the title of your website
st.set_page_config(page_title="StudyQuest AI", page_icon="⚔️", layout="centered")
st.title("⚔️ StudyQuest AI")
st.write("Turn your dry school notes into a gamified quiz.")

# 1. Hardcode your working API key safely for testing
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# 2. Setup memory storage for the chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages on the screen
for message in st.session_state.chat_history:
    # Skip displaying the hidden system instructions to the user
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Handle user typing a message
if user_message := st.chat_input("Paste your notes or textbook text here to start the game..."):
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_message)
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    try:
        # Connect to Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        # Inject the system instructions at the very beginning of the history context
        system_instruction = {
            "role": "system", 
            "content": (
                "You are StudyQuest AI, a gamified high school study bot. Your job is to take whatever "
                "text, notes, or topics the user gives you and immediately turn them into a fun, "
                "multiple-choice quiz game. Present one question at a time. Tell them if they got it right "
                "or wrong after they answer, track their score like an RPG game, and give punchy, encouraging feedback."
            )
        }
        
        # Build full payload ensuring system prompt is at the top
        payload = [system_instruction] + [m for m in st.session_state.chat_history if m["role"] != "system"]
        
        # Request response from the model
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=payload
        )
        
        # Get response text
        ai_response = completion.choices[0].message.content
        
        # Show AI message
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"Something went wrong: {e}")
