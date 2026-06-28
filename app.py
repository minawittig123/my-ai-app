import streamlit as st
from groq import Groq
import io
import base64
# Import the new advanced custom component that you added to requirements.txt
from st_chat_input_multimodal import st_chat_input_multimodal

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

# Helper function to convert binary images to Base64 Data URIs for Groq Vision
def encode_bytes_to_data_url(image_bytes, mime_type="image/png"):
    base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{base64_encoded}"

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

# 3. Formatted Multi-Input ChatGPT Style Custom Widget Component
st.markdown("---")

# This renders exactly one unified bar at the bottom containing Text, Image Attachment, and Voice audio records
custom_submission = st_chat_input_multimodal(
    placeholder="Ask anything...",
    support_images=True,
    support_voice=True
)

active_text_input = None
uploaded_image_bytes = None

# 4. Action: Parse incoming Data from Unified Component
if custom_submission:
    client = Groq(api_key=GROQ_API_KEY)
    
    # Check if the user typed text
    if custom_submission.get("text"):
        active_text_input = custom_submission["text"].strip()
        
    # Check if a voice recording was captured directly inside the input bar
    if custom_submission.get("audio_bytes"):
        try:
            with st.spinner("🎙️ Transcribing voice from chatbar..."):
                raw_audio = custom_submission["audio_bytes"]
                audio_file = ("audio.wav", raw_audio, "audio/wav")
                
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3", 
                    response_format="text"
                )
                active_text_input = str(transcription).strip()
        except Exception as audio_err:
            st.error(f"Voice Processing Error: {audio_err}")
            
    # Check if an image was dropped/attached inside the chat bar
    if custom_submission.get("image_bytes"):
        uploaded_image_bytes = custom_submission["image_bytes"]

# 5. Core Game Reasoning Generation System Loop
if active_text_input or uploaded_image_bytes:
    
    user_content_payload = []
    
    # Process text segment
    if active_text_input:
        user_content_payload.append({"type": "text", "text": active_text_input})
    else:
        user_content_payload.append({"type": "text", "text": "[Sent an image for analysis]"})
        
    # Process visual element payload configuration
    if uploaded_image_bytes:
        image_data_url = encode_bytes_to_data_url(uploaded_image_bytes)
        user_content_payload.append({
            "type": "image_url",
            "image_url": {"url": image_data_url}
        })
        
    # Render user prompt locally
    with st.chat_message("user"):
        if active_text_input:
            st.markdown(active_text_input)
        if uploaded_image_bytes:
            st.image(uploaded_image_bytes, caption="Uploaded Quest Photo", width=300)
        
    st.session_state.chat_history.append({"role": "user", "content": user_content_payload})

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        system_instruction = {
            "role": "system", 
            "content": (
                f"You are StudyQuest AI, an elite gamified study engine. Adopt the tone of a '{ai_class}' guide companion. "
                f"Adjust the academic standard of your evaluation to match a '{difficulty}' difficulty rating. "
                "Analyze user inputs and any uploaded visual homework photos, grade their work if applicable, and reward XP or point gains explicitly. "
                "Always ask exactly ONE multiple-choice quiz question at a time. Include point rewards for correctness."
            )
        }
        
        payload = [system_instruction] + [m for m in st.session_state.chat_history if m["role"] != "system"]
        
        with st.spinner("⚔️ AI is thinking..."):
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=payload
            )
        
        # FIX: Access the first element in choices list using [0] to avoid TypeErrors
        ai_response = completion.choices[0].message.content
        
        # Point parser logic rules checking
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
