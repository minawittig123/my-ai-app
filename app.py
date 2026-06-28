import streamlit as st
from groq import Groq

# 1. Premium Page Configuration (Dark Tech Theme Layout)
st.set_page_config(
    page_title="StudyQuest AI | Gamified Learning", 
    page_icon="⚔️", 
    layout="centered"
)

# Custom CSS to force a unified, beautiful dark mode skin across all elements
st.markdown("""
    <style>
    /* Force main canvas background color */
    .stApp, div[data-testid="stAppViewContainer"] {
        background-color: #0d0d10 !important;
        color: #E2E8F0 !important;
    }
    
    /* Force sidebar to blend perfectly with the dark canvas */
    section[data-testid="stSidebar"] {
        background-color: #121216 !important;
        border-right: 1px solid #1f1f29;
    }
    
    /* Style Chat Input box to look modern like ChatGPT */
    div[data-testid="stChatInput"] textarea {
        background-color: #1a1a24 !important;
        color: #ffffff !important;
        border: 1px solid #2d2d3d !important;
        border-radius: 12px !important;
    }
    
    /* Make chat bubbles easily readable in custom dark mode */
    div[data-testid="stChatMessage"] {
        background-color: #161620 !important;
        border: 1px solid #232333 !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    
    /* Main Screen Titles */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(45deg, #FF6B6B, #4D96FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Customization Dashboard (Personalization Options)
# Fixed the broken image link with a working icon url
st.sidebar.image("https://icons8.com", width=80)
st.sidebar.title("🛠️ Quest Dashboard")
st.sidebar.write("Customize your AI study adventure.")

# Customization Option 1: Game Difficulty
difficulty = st.sidebar.select_slider(
    "Select Game Difficulty:",
    options=["Casual Player", "Scholar", "Hardcore Legend"]
)

# Customization Option 2: AI Personality Subclass
ai_class = st.sidebar.selectbox(
    "Choose your AI Guide Companion:",
    ["Cyberpunk Hacker Mage", "Strict Medieval King", "Chill Retro Gamer", "Sarcastic Robot Coach"]
)

# Customization Option 3: User Level Tracker (Visual RPG Element)
st.sidebar.markdown("---")
st.sidebar.subheader("🎒 Your Inventory")
st.sidebar.progress(45, text="✨ Level 3 Apprentice Wizard (45/100 XP)")

# 3. Monetization: The Support Tip Jar
st.sidebar.markdown("---")
st.sidebar.subheader("🎁 Support the Project")
st.sidebar.write(
    "I'm a newly turned 13-year-old developer! If this app helps you crush your classes, "
    "consider dropping a few bucks in my tip jar to help fund better features."
)
# Yellow Buy Me A Coffee Button
st.sidebar.markdown(
    '<a href="https://buymeacoffee.com" target="_blank">'
    '<img src="https://buymeacoffee.com" '
    'alt="Buy Me A Coffee" style="height: 45px !important;width: 162px !important;" ></a>',
    unsafe_allow_html=True
)

# 4. App Main Screen Title Elements
st.markdown('<h1 class="main-title">⚔️ StudyQuest AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">The Ultimate High-Performance Gamified AI Study Guide</p>', unsafe_allow_html=True)

# 5. Fetch Secure API Key from Vault
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GROQ_API_KEY inside your Streamlit Secrets Vault.")
    st.stop()

# 6. Initialize Chat Engine & Session History Memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display beautifully formatted chat logs on screen
for message in st.session_state.chat_history:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Action: Process User Input Note text
if user_message := st.chat_input("Paste textbook text or notes here to initialize your battle quest..."):
    with st.chat_message("user"):
        st.markdown(user_message)
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Advanced Dynamic System Prompt injecting the personalization options chosen in the sidebar!
        system_instruction = {
            "role": "system", 
            "content": (
                f"You are StudyQuest AI, an elite gamified study engine. "
                f"Adopt the tone of a '{ai_class}' guide companion. "
                f"Adjust the academic standard of your evaluation to match a '{difficulty}' difficulty rating. "
                "Analyze user provided text and immediately launch an interactive multiple-choice quiz session. "
                "Ask exactly ONE question at a time. Evaluate their accuracy immediately after their turn, "
                "track their score like an immersive role playing game, and provide highly customized, thematic feedback."
            )
        }
        
        # Build complete dialogue payload ensuring dynamic system directives sit at the index root
        payload = [system_instruction] + [m for m in st.session_state.chat_history if m["role"] != "system"]
        
        # Dispatch transaction to Groq platform infrastructure
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

