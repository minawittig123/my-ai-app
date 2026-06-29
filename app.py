import streamlit as st
from groq import Groq
import io
import base64

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

# Helper function to convert binary images to Base64 Data URIs for Groq Vision safely
def encode_bytes_to_data_url(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_encoded = base64.b64encode(bytes_data).decode("utf-8")
    return f"data:{uploaded_file.type};base64,{base64_encoded}"

# 2. Sidebar Customization Dashboard
st.sidebar.title("Quest Dashboard")
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

# Reset Options Container
if st.sidebar.button("🔄 Reset Current Quest", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.game_score = 0
    st.session_state.current_level = 1
    st.session_state.xp_points = 0
    st.session_state.last_processed_audio = None
    st.toast("Quest board wiped clean! Start fresh.", icon="🧹")
    st.rerun()

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
        if isinstance(message["content"], list):
            for item in message["content"]:
                if item["type"] == "text":
                    st.markdown(item["text"])
                elif item["type"] == "image_url":
                    st.image(item["image_url"]["url"], caption="Uploaded Quest Image", width=300)
        else:
            st.markdown(message["content"])

# 3. Inject Pill Container Style Overlay using native st.html
st.html("""
<style>
    /* Scope styling safely to modern capsule bar dimensions */
    div[data-testid="stForm"] {
        border: 1px solid #e6e8eb !important;
        border-radius: 9999px !important;
        padding: 6px 18px !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    }
    div[data-testid="stForm"] button {
        border: none !important;
        background: transparent !important;
    }
</style>
""")

active_text_input = None
uploaded_photo = None
voice_recording = None

# 4. The Pill Bar UI Engine Layout Form
with st.form("pill_chat_deck", clear_on_submit=True):
    # Form layout matching the image layout structure smoothly
    ui_cols = st.columns([1, 10, 1, 1])
    
    with ui_cols[0]:
        # The attachment anchor sign node selector
        uploaded_photo = st.file_uploader("➕", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        
    with ui_cols[1]:
        # Main typing box layer
        user_message = st.text_input("Ask anything", placeholder="Ask anything", label_visibility="collapsed")
        
    with ui_cols[2]:
        # Micro recorder attachment deck hook
        voice_recording = st.audio_input("🎤", label_visibility="collapsed")
        
    with ui_cols[3]:
        # The active circular black submission control waveform
        submit_quest = st.form_submit_button("📊")

# 5. Handle Text vs. Audio Processing priority layers
if submit_quest:
    if voice_recording and voice_recording != st.session_state.last_processed_audio:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            with st.spinner("🎙️ Transcribing voice note..."):
                audio_bytes = voice_recording.getvalue()
                audio_file = ("audio.wav", audio_bytes, "audio/wav")
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3", 
                    response_format="text"
                )
                active_text_input = str(transcription).strip()
                st.session_state.last_processed_audio = voice_recording
        except Exception as audio_err:
            st.error(f"Audio Scanner Failure: {audio_err}")
            
    if user_message:
        active_text_input = user_message

# 6. Core Game Reasoning Generation System Loop (100% Flat String History Layer Fix)
if active_text_input or uploaded_photo:
    
    # Store standard visual logs inside memory local variables
    display_payload = []
    if active_text_input:
        display_payload.append({"type": "text", "text": active_text_input})
    if uploaded_photo:
        image_data_url = encode_bytes_to_data_url(uploaded_photo)
        display_payload.append({"type": "image_url", "image_url": {"url": image_data_url}})
    
    # Visual screen logging render
    with st.chat_message("user"):
        if active_text_input:
            st.markdown(active_text_input)
        if uploaded_photo:
            st.image(uploaded_photo, caption="Uploaded Quest Photo", width=300)
            
    st.session_state.chat_history.append({"role": "user", "content": display_payload})

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        system_instruction = (
            f"You are StudyQuest AI, an elite gamified study engine. Adopt the tone of a '{ai_class}' guide companion. "
            f"Adjust the academic standard of your evaluation to match a '{difficulty}' difficulty rating. "
            "Analyze user notes, text responses, and audio descriptions. Grade their inputs, reward point gains explicitly, "
            "and always ask exactly ONE multiple-choice quiz question at a time."
        )
        
        # BULLETPROOF RE-INDEX FIX: Convert ALL message payloads into strict flat strings to stop 400 bad parameter payload breaks!
        payload = [{"role": "system", "content": system_instruction}]
        
        for msg in st.session_state.chat_history:
            # Flatten array item maps to pristine clear simple text content segments
            if isinstance(msg["content"], list):
                text_accumulator = ""
                for segment in msg["content"]:
                    if segment["type"] == "text":
                        text_accumulator += segment["text"] + " "
                payload.append({"role": msg["role"], "content": text_accumulator.strip()})
            else:
                payload.append({"role": msg["role"], "content": str(msg["content"])})

        with st.spinner("⚔️ AI is thinking..."):
            # Switched to the permanent text engine model to ensure flawless execution with flat string arrays
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=payload
            )
        
        ai_response = completion.choices[0].message.content
        
        # Point parser scoring rules adjustments
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
        
        st.rerun()

    except Exception as e:
        st.error(f"Execution Error: {e}")
