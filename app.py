import streamlit as st
from groq import Groq

# 1. Page Config Setup
st.set_page_config(
    page_title="StudyQuest AI | Gamified Learning", 
    page_icon="⚔️", 
    layout="centered"
)

# 2. Sidebar Layout Elements
st.sidebar.image("https://githubusercontent.com", width=60)
st.sidebar.title("🛠️ Quest Dashboard")
st.sidebar.write("Customize your AI study adventure.")

# THEME MANAGER - 8 High-Contrast Theme Settings
theme_choice = st.sidebar.selectbox(
    "🎨 Choose Website Theme Color:",
    [
        "Obsidian Night (Dark)", 
        "Glacier Mint (Light)", 
        "Deep Cyber Purple", 
        "Retro Amber Gold", 
        "Crimson Battle", 
        "Ocean Abyss", 
        "Forest Grove", 
        "Matrix Green"
    ]
)

# High-contrast mapping: Ensures text is always readable against the canvas background
theme_styles = {
    "Obsidian Night (Dark)": {"bg": "#0D0D10", "text": "#FFFFFF", "sidebar": "#16161C", "input": "#1C1C24", "bubble": "#16161C"},
    "Glacier Mint (Light)": {"bg": "#FFFFFF", "text": "#000000", "sidebar": "#F1F5F9", "input": "#E2E8F0", "bubble": "#F1F5F9"},
    "Deep Cyber Purple": {"bg": "#120E2E", "text": "#FFFFFF", "sidebar": "#1B1643", "input": "#241D59", "bubble": "#1B1643"},
    "Retro Amber Gold": {"bg": "#2B1A04", "text": "#FFFFFF", "sidebar": "#3D2506", "input": "#543308", "bubble": "#3D2506"},
    "Crimson Battle": {"bg": "#260505", "text": "#FFFFFF", "sidebar": "#3D0A0A", "input": "#541010", "bubble": "#3D0A0A"},
    "Ocean Abyss": {"bg": "#051622", "text": "#FFFFFF", "sidebar": "#0B2D44", "input": "#114263", "bubble": "#0B2D44"},
    "Forest Grove": {"bg": "#0A1F11", "text": "#FFFFFF", "sidebar": "#143D22", "input": "#1D5931", "bubble": "#143D22"},
    "Matrix Green": {"bg": "#000000", "text": "#00FF00", "sidebar": "#051405", "input": "#0A290A", "bubble": "#051405"}
}

active_theme = theme_styles[theme_choice]

# Inject CSS rules to enforce theme selections
st.markdown(f"""
    <style>
    /* Main app and bottom chat block container */
    .stApp, div[data-testid="stAppViewContainer"], div[data-testid="stBottomBlockContainer"] {{
        background-color: {active_theme["bg"]} !important;
        color: {active_theme["text"]} !important;
    }}
    
    /* Sidebar Overrides */
    section[data-testid="stSidebar"] {{
        background-color: {active_theme["sidebar"]} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {active_theme["text"]} !important;
    }}
    
    /* Chat input element formatting */
    div[data-testid="stChatInput"] textarea {{
        background-color: {active_theme["input"]} !important;
        color: {active_theme["text"]} !important;
    }}
    
    /* Chat bubbles formatting */
    div[data-testid="stChatMessage"] {{
        background-color: {active_theme["bubble"]} !important;
        color: {active_theme["text"]} !important;
        border: 1px solid {active_theme["input"]} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Main Titles using active styles
st.markdown(f'<h1 style="text-align: center; color: {active_theme["text"]}; font-weight: 800; font-size: 2.8rem;">⚔️ StudyQuest AI</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: {active_theme["text"]}; opacity: 0.8; font-size: 1rem; margin-bottom: 2rem;">The Ultimate High-Performance Gamified AI Study Guide</p>', unsafe_allow_html=True)

# Game Parameters
difficulty = st.sidebar.select_slider(
    "Select Game Difficulty:",
    options=["Casual Player", "Scholar", "Hardcore Legend"]
)

ai_class = st.sidebar.selectbox(
    "Choose your AI Guide Companion:",
    ["Cyberpunk Hacker Mage", "Strict Medieval King", "Chill Retro Gamer", "Sarcastic Robot Coach"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎒 Your Inventory")
st.sidebar.progress(45, text="✨ Level 3 Apprentice Wizard (45/100 XP)")

# Monetization Link Setup
st.sidebar.markdown("---")
st.sidebar.subheader("🎁 Support the Project")
st.sidebar.write("I'm a newly turned 13-year-old developer! Consider dropping a few bucks in my tip jar to help support the application.")
st.sidebar.link_button("☕ Support on Buy Me A Coffee", "https://buymeacoffee.com", use_container_width=True)

# Key Validation
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Missing API Key inside Streamlit Secrets Vault.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_message := st.chat_input("Paste textbook text or notes here to initialize your battle quest..."):
    with st.chat_message("user"):
        st.markdown(user_message)
    st.session_state.chat_history.append({"role": "user", "content": user_message})

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
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=payload
        )
        
        # FIXED: Core list extractor array added
        ai_response = completion.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"Execution Error: {e}")
