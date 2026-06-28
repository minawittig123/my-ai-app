import streamlit as st
from groq import Groq
import io

# 1. Premium Page Configuration
st.set_page_config(
    page_title="StudyQuest AI | Gamified Learning", 
    page_icon="⚔️", 
    layout="centered"
)

# Initialize Chat Engine & Game State Variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "game_score" not in st.session_state:
    st.session_state.game_score = 0
if "current_level" not in st.session_state:
    st.session_state.current_level = 1
if "xp_points" not in st.session_state:
    st.session_state.xp_points = 45
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# 2. Sidebar Customization Dashboard
st.sidebar.image("https://github.com", width=60) # Using valid public placeholder icon
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

# Dynamically calculate XP bar rendering
xp_text = f"✨ Level {st.session_state.current_level} Adventurer ({st.session_state.xp_points}/100 XP)"
st.sidebar.progress(st.session_state.xp_points, text=xp_text)
st.sidebar.metric(label="🏆 Total Game Score", value=st.session_state.game_score)

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

active_text_input = None

# 4. Action: Audio Processing Loop (Whisper Speech-to-Text)
# Fix: Ensure we don't re-process the exact same audio clip over and over again on re-runs
if voice_recording and voice_recording != st.session_state.last_processed_audio:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        with st.spinner("🎙️ Transcribing your voice question..."):
            # Safely handle binary stream conversion
            audio_bytes = voice_recording.getvalue()
            
            # Groq audio requires a tuple with standard naming conventions
            audio_file = ("audio.wav", audio_bytes, "audio/wav")
            
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3", 
                response_format="text"
            )
            active_text_input = str(transcription).strip()
            # Save buffer state to avoid duplicating transcription on next button click
            st.session_state.last_processed_audio = voice_recording
            
    except Exception as audio_err:
        st.error(f"Audio Scanner Error: {audio_err}")

# Text box priority selection override
if user_message:
    active_text_input = user_message

# 5. Core Game Reasoning Generation System Loop
if active_text_input:
    with st.chat_message("user"):
        st.markdown(active_text_input)
        
    st.session_state.chat_history.append({"role": "user", "content": active_text_input})

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Guide system behavior explicitly to monitor user points inside responses
        system_instruction = {
            "role": "system", 
            "content": (
                f"You are StudyQuest AI, an elite gamified study engine. Adopt the tone of a '{ai_class}' guide companion. "
                f"Adjust the academic standard of your evaluation to match a '{difficulty}' difficulty rating. "
                "Analyze user inputs, grade their previous answers if applicable, and reward XP or point gains explicitly. "
                "Always ask exactly ONE multiple-choice quiz question at a time. Include point rewards for correctness."
            )
        }
        
        payload = [system_instruction] + [m for m in st.session_state.chat_history if m["role"] != "system"]
        
        with st.spinner("⚔️ AI is thinking..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=payload
            )
        
        ai_response = completion.choices[0].message.content
        
        # Simple rule engine parser to intercept point metrics dynamically back to sidebar
        if "correct" in ai_response.lower() or "+xp" in ai_response.lower():
            st.session_state.game_score += 10
            st.session_state.xp_points += 15
            if st.session_state.xp_points >= 100:
                st.session_state.current_level += 1
                st.session_state.xp_points = st.session_state.xp_points % 100
                st.toast("🎉 LEVEL UP! You earned a new tier!", icon="👑")
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Force refresh UI to instantly show point updates in sidebar panel layout
        st.rerun()

    except Exception as e:
        st.error(f"Execution Error: {e}")
