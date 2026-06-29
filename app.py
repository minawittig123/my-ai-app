import streamlit as st
from groq import Groq
import base64
import hashlib


# ==========================================================
# CONFIG
# ==========================================================

st.set_page_config(
    page_title="StudyQuest AI | Gamified Learning",
    page_icon="⚔️",
    layout="centered"
)


# ==========================================================
# SESSION STATE
# ==========================================================

defaults = {

    "chat_history": [],

    "game_score": 0,

    "current_level": 1,

    "xp_points": 45,

    "last_processed_audio": None,

    "last_submission": None,

    "is_processing": False

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



def make_hash(data):

    return hashlib.md5(data).hexdigest()



def flatten_for_groq(content):

    if isinstance(content, str):

        return content


    text = ""


    for item in content:


        if item["type"] == "text":

            text += item["text"]


        elif item["type"] == "image_url":

            text += (
                "\n[User uploaded an image. "
                "Ask the user to describe it.]"
            )


    return text




# ==========================================================
# API KEY
# ==========================================================


try:

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]


except Exception:

    st.error(
        "Missing GROQ_API_KEY."
    )

    st.stop()




# ==========================================================
# SIDEBAR
# ==========================================================


st.sidebar.title("⚔️ Quest Dashboard")



difficulty = st.sidebar.select_slider(

    "Difficulty",

    [
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

    text=f"Level {st.session_state.current_level} "
         f"({st.session_state.xp_points}/100 XP)"

)



st.sidebar.metric(

    "🏆 Score",

    st.session_state.game_score

)



if st.sidebar.button(
    "🔄 Reset Quest"
):

    for key in defaults:

        if isinstance(defaults[key], list):

            st.session_state[key] = []

        else:

            st.session_state[key] = defaults[key]



    st.toast(
        "Quest reset!",
        icon="🧹"
    )




# ==========================================================
# HEADER
# ==========================================================


st.markdown(

"""
<h1 style="
text-align:center;
font-size:2.8rem;
font-weight:900;">
⚔️ StudyQuest AI
</h1>

<p style="
text-align:center;
opacity:.7;">
The Ultimate Gamified AI Study Companion
</p>

""",

unsafe_allow_html=True

)




# ==========================================================
# CHAT DISPLAY
# ==========================================================


for message in st.session_state.chat_history:


    with st.chat_message(
        message["role"]
    ):


        if isinstance(
            message["content"],
            list
        ):


            for item in message["content"]:


                if item["type"] == "text":

                    st.markdown(
                        item["text"]
                    )


                elif item["type"] == "image_url":

                    st.image(
                        item["image_url"]["url"],
                        width=300
                    )


        else:

            st.markdown(
                message["content"]
            )




# ==========================================================
# CSS PILL BAR
# ==========================================================


st.html(
"""
<style>


div[data-testid="stForm"] {

border-radius:9999px !important;

border:1px solid #ddd !important;

padding:8px 15px !important;

background:white !important;

}



div[data-testid="stFileUploader"],
div[data-testid="stAudioInput"] {

background:transparent !important;

border:none !important;

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
# INPUT
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


    if user_message.strip() != "":

        active_text = user_message.strip()



    if voice_recording:


        audio_id = make_hash(
            voice_recording.getvalue()
        )


        if audio_id != st.session_state.last_processed_audio:


            try:


                client = Groq(
                    api_key=GROQ_API_KEY
                )


                result = client.audio.transcriptions.create(

                    file=(

                        "audio.wav",

                        voice_recording.getvalue(),

                        "audio/wav"

                    ),

                    model="whisper-large-v3",

                    response_format="text"

                )


                if str(result).strip():

                    active_text = str(result).strip()


                st.session_state.last_processed_audio = audio_id



            except Exception as e:

                st.error(
                    f"Audio error: {e}"
                )




# ==========================================================
# AI ENGINE
# ==========================================================


submission_id = None



if active_text:

    submission_id = active_text



elif uploaded_photo:

    submission_id = make_hash(
        uploaded_photo.getvalue()
    )




if (

    (active_text or uploaded_photo)

    and

    submission_id != st.session_state.last_submission

    and

    not st.session_state.is_processing

):


    st.session_state.is_processing = True

    st.session_state.last_submission = submission_id



    user_payload = []



    if active_text:

        user_payload.append({

            "type":"text",

            "text":active_text

        })



    if uploaded_photo:

        user_payload.append({

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

        "content":user_payload

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

- Be a gamified study companion.
- Explain clearly.
- Give rewards.
- Use +XP when appropriate.
- Ask one multiple choice question.

"""



        messages = [

            {

            "role":"system",

            "content":system_prompt

            }

        ]



        for msg in st.session_state.chat_history:


            messages.append({

                "role":msg["role"],

                "content":
                flatten_for_groq(
                    msg["content"]
                )

            })




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

            or

            "xp" in ai_response.lower()

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




        st.session_state.chat_history.append({

            "role":"assistant",

            "content":ai_response

        })



        st.session_state.is_processing = False



    except Exception as e:


        st.session_state.is_processing = False


        st.error(
            f"Execution Error: {e}"
        )
