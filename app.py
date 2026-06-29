import streamlit as st
from groq import Groq
import base64
import hashlib


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="StudyQuest AI | Gamified Learning",
    page_icon="⚔️",
    layout="centered"
)


# ==========================================================
# SESSION STATE ENGINE
# ==========================================================

defaults = {

    "chat_history": [],

    "game_score": 0,

    "current_level": 1,

    "xp_points": 45,

    "last_processed_audio": None

}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value



# ==========================================================
# HELPERS
# ==========================================================


def encode_bytes_to_data_url(file):

    data = file.getvalue()

    encoded = base64.b64encode(data).decode()

    return f"data:{file.type};base64,{encoded}"



def audio_fingerprint(audio):

    return hashlib.md5(
        audio.getvalue()
    ).hexdigest()



def flatten_for_groq(content):

    """
    Converts UI structured messages into
    flat strings required by gpt-oss-120b
    """

    if isinstance(content, str):

        return content


    text = ""


    for item in content:

        if item.get("type") == "text":

            text += item.get("text", "")


        elif item.get("type") == "image_url":

            text += (
                "\n[User uploaded an image. "
                "Image processing unavailable in text-only model.]"
            )


    return text



# ==========================================================
# SECRET
# ==========================================================


try:

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]


except Exception:

    st.error(
        "Missing GROQ_API_KEY in Streamlit Secrets."
    )

    st.stop()



# ==========================================================
# SIDEBAR
# ==========================================================


st.sidebar.title("⚔️ Quest Dashboard")


difficulty = st.sidebar.select_slider(

    "Difficulty",

    options=[
        "Casual Player",
        "Scholar",
        "Hardcore Legend"
    ]

)



ai_class = st.sidebar.selectbox(

    "AI Companion",

    [
        "Cyberpunk Hacker Mage",
        "Strict Medieval King",
        "Chill Retro Gamer",
        "Sarcastic Robot Coach"
    ]

)



st.sidebar.divider()



st.sidebar.subheader("🎒 Inventory")



st.sidebar.progress(

    st.session_state.xp_points / 100,

    text=
    f"Level {st.session_state.current_level} "
    f"({st.session_state.xp_points}/100 XP)"

)



st.sidebar.metric(

    "🏆 Score",

    st.session_state.game_score

)



if st.sidebar.button(
    "🔄 Reset Quest",
    use_container_width=True
):

    st.session_state.chat_history = []

    st.session_state.game_score = 0

    st.session_state.current_level = 1

    st.session_state.xp_points = 0

    st.session_state.last_processed_audio = None


    st.toast(
        "Quest reset!",
        icon="🧹"
    )

    st.rerun()



# ==========================================================
# HEADER
# ==========================================================


st.markdown(
"""
<h1 style="
text-align:center;
font-size:2.8rem;
font-weight:900;
">
⚔️ StudyQuest AI
</h1>

<p style="
text-align:center;
opacity:.75;
">
The Ultimate Gamified AI Study Companion
</p>

""",
unsafe_allow_html=True
)



# ==========================================================
# CHAT DISPLAY
# ==========================================================


for msg in st.session_state.chat_history:


    if msg["role"] == "system":

        continue



    with st.chat_message(msg["role"]):


        content = msg["content"]


        if isinstance(content,list):


            for item in content:


                if item["type"]=="text":

                    st.markdown(
                        item["text"]
                    )


                elif item["type"]=="image_url":

                    st.image(
                        item["image_url"]["url"],
                        width=300
                    )


        else:

            st.markdown(content)



# ==========================================================
# CSS PILL CHAT BAR
# ==========================================================


st.html(
"""
<style>


div[data-testid="stForm"] {

border-radius:9999px !important;

border:1px solid #ddd !important;

padding:8px 16px !important;

background:white !important;

box-shadow:
0 5px 25px rgba(0,0,0,.06);

}



div[data-testid="stFileUploader"],
div[data-testid="stAudioInput"],
.stDropzone {


background:transparent !important;

border:none !important;

padding:0 !important;

}



div[data-testid="stHorizontalBlock"] {

align-items:center;

}



div[data-testid="stFormSubmitButton"] button {


background:black !important;

color:white !important;

border-radius:50% !important;

width:42px !important;

height:42px !important;


}



input {


background:transparent !important;

border:none !important;


}


</style>

"""
)



# ==========================================================
# CHAT INPUT FORM
# ==========================================================


with st.form(

    "pill_chat_deck",

    clear_on_submit=True

):


    c1,c2,c3,c4 = st.columns(
        [0.1,0.7,0.1,0.1]
    )



    with c1:

        uploaded_photo = st.file_uploader(

            "➕",

            type=[
                "png",
                "jpg",
                "jpeg"
            ],

            label_visibility="collapsed"

        )



    with c2:

        user_message = st.text_input(

            "Ask anything",

            placeholder="Ask anything",

            label_visibility="collapsed"

        )



    with c3:

        voice_recording = st.audio_input(

            "🎤",

            label_visibility="collapsed"

        )



    with c4:

        submit = st.form_submit_button(

            "📊"

        )



# ==========================================================
# INPUT PROCESSING
# ==========================================================


active_text = None



if submit:


    if voice_recording:


        fingerprint = audio_fingerprint(
            voice_recording
        )


        if fingerprint != st.session_state.last_processed_audio:


            try:


                client = Groq(
                    api_key=GROQ_API_KEY
                )


                audio_file = (

                    "audio.wav",

                    voice_recording.getvalue(),

                    "audio/wav"

                )



                transcription = client.audio.transcriptions.create(

                    file=audio_file,

                    model="whisper-large-v3",

                    response_format="text"

                )



                if str(transcription).strip():

                    active_text = str(
                        transcription
                    ).strip()



                st.session_state.last_processed_audio = fingerprint



            except Exception as e:


                st.error(
                    f"Audio error: {e}"
                )



    if user_message.strip() != "":


        active_text = user_message.strip()



# ==========================================================
# GROQ ENGINE
# ==========================================================


if active_text or uploaded_photo:


    display = []


    if active_text:


        display.append({

            "type":"text",

            "text":active_text

        })



    if uploaded_photo:


        display.append({

            "type":"image_url",

            "image_url":{

                "url":
                encode_bytes_to_data_url(
                    uploaded_photo
                )

            }

        })



    st.session_state.chat_history.append({

        "role":"user",

        "content":display

    })



    try:


        client = Groq(

            api_key=GROQ_API_KEY

        )



        system_prompt = f"""

You are StudyQuest AI.

Persona:
{ai_class}

Difficulty:
{difficulty}

Rules:

- Teach clearly.
- Act like an RPG companion.
- Reward progress using +XP.
- Ask exactly one multiple choice question.

"""



        messages = [{

            "role":"system",

            "content":system_prompt

        }]



        for item in st.session_state.chat_history:


            messages.append({

                "role":item["role"],

                "content":
                flatten_for_groq(
                    item["content"]
                )

            })



        with st.spinner(
            "⚔️ AI thinking..."
        ):


            completion = client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=messages

            )



        ai_response = (
            completion
            .choices[0]
            .message
            .content
        )



        if (

            "correct" in ai_response.lower()

            or

            "+xp" in ai_response.lower()

        ):


            st.session_state.game_score += 10

            st.session_state.xp_points += 15



            if st.session_state.xp_points >= 100:


                st.session_state.current_level += 1

                st.session_state.xp_points %= 100


                st.toast(

                    "🎉 LEVEL UP!",

                    icon="👑"

                )



        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                ai_response
            )



        st.session_state.chat_history.append({

            "role":"assistant",

            "content":ai_response

        })


        st.rerun()



    except Exception as e:


        st.error(
            f"Groq Failure: {e}"
        )
