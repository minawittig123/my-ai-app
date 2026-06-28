import streamlit as st
from groq import Groq
import io

# 1. Premium Page Configuration
st.set_page_config(
    page_title="StudyQuest AI | Gamified Learning", 
    page_icon="⚔️", 
    layout="centered"
)

# 2. Sidebar Customization Dashboard (Re-integrated Graphics & Links)
st.sidebar.image("https://githubusercontent.com", width=60)
st.sidebar.title("🛠️ Quest Dashboard")
st.sidebar.write("Customize your AI study adventure.")

# Game Difficulty Options
difficulty = st.sidebar.select_slider(
    "Select Game Difficulty:",
    options=["Casual Player", "Scholar", "Hardcore Legend"]
)

# AI Companion Persona Options
ai_class = st.sidebar.selectbox(
    "Choose your AI Guide Companion:",
    ["Cyberpunk Hacker Mage", "Strict Medieval King", "Chill Retro Gamer", "Sarcastic Robot Coach"]
)

# Visual RPG Progress Level Element Tracker
st.sidebar.markdown("---")
st.sidebar.subheader("🎒 Your Inventory")
st.sidebar.progress(45, text="✨ Level 3 Apprentice Wizard (45/100 XP)")

# Monetization Support link setup
st.sidebar.markdown("---")
st.sidebar.subheader("🎁 Support the Project")
st.sidebar.write("I'm a newly turned 13-year-old developer! Consider dropping a few bucks in my tip jar to help support the application.")
st.sidebar.link_button("☕ Support on Buy Me A Coffee", "https://buymeacoffee.com", use_container_width=True)

# Main Screen Headings
st.markdown('<h1 style="text-align: center; font-weight: 800; font-size: 2.8rem;">⚔️ StudyQuest AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; opacity: 0.8; font-size: 1rem; margin-bottom: 2rem;">The Ultimate High-Performance Gamified AI Study Guide</p>', unsafe_allow_html=True)

# Fetch System Key from Secrets Vault
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Missing API Key inside Streamlit Secrets Vault.")
    st.stop()

# Initialize Chat Engine History Memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display beautifully formatted chat logs on screen
for message in st.session_state.chat_history:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Dedicated Inputs Interface Layout
st.markdown("---")
voice_recording = st.audio_input("🎤 Record your audio question:")
user_message = st.chat_input("Paste text notes or type answers here...")

# Active logic parameters
active_text_input = None

# 4. Action: Audio Processing Loop (Whisper Speech-to-Text)
if voice_recording:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Read the microphone wave buffer data safely
        audio_bytes = voice_recording.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav" # Give it a file naming layout context
        
        with st.spinner("🎙️ Transcribing your voice question..."):
            # Dispatch transcription query to Groq's dedicated audio translation engine
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3", # Global production audio speed model standard
                response_format="text"
            )
            active_text_input = str(transcription)
    except Exception as audio_err:
        st.error(f"Audio Scanner Error: {audio_err}")

# If they typed a text instead, prioritize the text entry box
if user_message:
    active_text_input = user_message

# 5. Core Game Reasoning Generation System Loop
if active_text_input:
    with st.chat_message("user"):
        st.markdown(active_text_input)
        
    st.session_state.chat_history.append({"role": "user", "content": active_text_input})

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        system_instruction = {
            "role": "system", 
            "content": (
                f"You are StudyQuest AI, an elite gamified study engine. Adopt the tone of a '{ai_class}' guide companion. "
                f"Adjust the academic standard of your evaluation to match a '{difficulty}' difficulty rating. "
                "Analyze user notes and immediately launch an interactive multiple-choice quiz session. "
                "Ask exactly ONE question at a time. Track scores like an immersive role-playing game."
            )
        }
        
        payload = [system_instruction] + [m for m in st.session_state.chat_history if m["role"] != "system"]
        
        # Dispatch stable production text generation model execution
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=payload
        )
        
        ai_response = completion.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"Execution Error: {e}")
