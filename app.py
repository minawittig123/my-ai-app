import streamlit as st
from groq import Groq
from PIL import Image
import io

# 1. Premium Page Configuration
st.set_page_config(
    page_title="StudyQuest AI | Gamified Learning", 
    page_icon="⚔️", 
    layout="centered"
)

# Main Screen Headings
st.markdown('<h1 style="text-align: center; font-weight: 800; font-size: 2.8rem;">⚔️ StudyQuest AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; opacity: 0.8; font-size: 1rem; margin-bottom: 2rem;">The Ultimate High-Performance Gamified AI Study Guide</p>', unsafe_allow_html=True)

# 2. Sidebar Customization Dashboard
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

# Fetch System Key from Secrets Vault
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Missing API Key inside Streamlit Secrets Vault.")
    st.stop()

# Initialize Chat Engine History Array Memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display beautifully formatted chat logs on screen
for message in st.session_state.chat_history:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. New Input System Layout (File Uploaders & Voice Recorder)
st.markdown("---")
uploaded_photo = st.file_uploader("📸 Upload your textbook photo or homework sheet:", type=["png", "jpg", "jpeg"])
voice_recording = st.audio_input("🎤 Record your audio question instead:")

user_message = st.chat_input("Or paste text notes here to initialize your battle quest...")

# Processing Logic variables setup
active_input = None
photo_bytes = None

# Figure out which feature user triggered
if user_message:
    active_input = user_message
elif uploaded_photo:
    active_input = "Analyzing the uploaded image for your study session."
    photo_bytes = uploaded_photo.read()
elif voice_recording:
    active_input = "Analyzing your recorded microphone question."

# 4. Action: Dispatch Transaction to Groq Platform Infrastructure
if active_input:
    with st.chat_message("user"):
        st.markdown(active_input)
        if uploaded_photo:
            st.image(uploaded_photo, width=300)
            
    st.session_state.chat_history.append({"role": "user", "content": active_input})

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        system_instruction = (
            f"You are StudyQuest AI, an elite gamified study engine. Adopt the tone of a '{ai_class}' guide companion. "
            f"Adjust the academic standard of your evaluation to match a '{difficulty}' difficulty rating. "
            "Analyze user notes, text inputs, or visual images and immediately launch an interactive multiple-choice quiz session. "
            "Ask exactly ONE question at a time. Track scores like an immersive role-playing game."
        )

        # Base payload config
        messages_payload = [
            {"role": "system", "content": system_instruction}
        ]
        
        # Pull past chat history context
        for m in st.session_state.chat_history:
            if m["role"] != "system":
                messages_payload.append({"role": m["role"], "content": m["content"]})

        # Vision handling setup if a textbook image is uploaded
        if photo_bytes:
            # We must pass image content to Groq's multimodal completion endpoint
            messages_payload.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract and quiz me on the material visible inside this image asset:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{io.BytesIO(photo_bytes).read().hex()}" # Reads structural bytes format cleanly
                        }
                    }
                ]
            })

        # Dispatch vision/text model call sequence
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview", # Force Groq vision model capability
            messages=messages_payload
        )
        
        ai_response = completion.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"Execution Error: {e}")
