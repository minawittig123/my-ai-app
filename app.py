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

# Helper function to convert binary images to Base64 Data URIs safely
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

# 3. Inject Precise Advanced CSS Stylesheet Overrides
st.html("""
<style>
    /* Turn the outer form container into a perfect white capsule bar */
    div[data-testid="stForm"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 9999px !important;
        padding: 6px 18px !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Remove default dark box backgrounds from the file uploader and audio toolsets */
    div[data-testid="stFileUploader"], 
    div[data-testid="stAudioInput"],
    div[data-testid="stFileUploader"] > div,
    div[data-testid="stAudioInput"] > div,
    .stDropzone {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* Strip off background layers from text input blocks */
    div[data-testid="stForm"] input {
        background-color: transparent !important;
        border: none !important;
        color: #1a202c !important;
    }
    
    /* Ensure all column boxes stack cleanly with uniform center spacing */
    div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 0px !important;
    }
    
    /* Force the submission button to be a perfectly rounded circular icon */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
</style>
""")

active_text_input = None
uploaded_photo = None
voice_recording = None

# 4. The Pill Bar UI Engine Layout Form
with st.form("pill_chat_deck", clear_on_submit=True):
    col_attach, col_text, col_mic, col_submit = st.columns([0.1, 0.7, 0.1, 0.1])
    
    with col_attach:
        uploaded_photo = st.file_uploader("➕", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        
    with col_text:
        user_message = st.text_input("Ask anything", placeholder="Ask anything", label_visibility="collapsed")
        
    with col_mic:
        voice_recording = st.audio_input("🎤", label_visibility="collapsed")
        
    with col_submit:
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
                trans_text = str(transcription).strip()
                if trans_text:
                    active_text_input = trans_text
                st.session_state.last_processed_audio = voice_recording
        except Exception as audio_err:
            st.error(f"Audio Scanner Failure: {audio_err}")
            
    if user_message and user_message.strip() != "":
        active_text_input = user_message.strip()

# 6. Core Game Reasoning Generation System Loop
if active_text_input or uploaded_photo:
    
    display_payload = []
    if active_text_input:
        display_payload.append({"type": "text", "text": active_text_input})
    else:
        display_payload.append({"type": "text", "text": "[Sent an image for analysis]"})
        
    if uploaded_photo:
        image_data_url = encode_bytes_to_data_url(uploaded_photo)
        display_payload.append({"type": "image_url", "image_url": {"url": image_data_url}})
    
    # Render user prompt locally
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
            "Analyze user inputs and any uploaded visual homework photos, grade their work if applicable, and reward XP or point gains explicitly. "
            "Always ask exactly ONE multiple-choice quiz question at a time. Do not process empty inputs."
        )
        
        payload = [{"role": "system", "content": [{"type": "text", "text": system_instruction}]}]
        
        # Build structured message logs
        for msg in st.session_state.chat_history:
            if isinstance(msg["content"], list):
                payload.append({"role": msg["role"], "content": msg["content"]})
            else:
                payload.append({"role": msg["role"], "content": [{"type": "text", "text": str(msg["content"])}]})

        with st.spinner("⚔️ AI is thinking..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=payload
            )
        
        # FIXED: Added back the exact list index position [0] wrapper constraint
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
            st.session_state.chat_history.append({"role": "assistant", "content": [{"type": "text", "text": ai_response}]})
            st.rerun()

    except Exception as e:
        st.error(f"Execution Error: {e}")
