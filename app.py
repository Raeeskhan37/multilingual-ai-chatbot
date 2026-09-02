import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import os
import tempfile
import hashlib


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Multilingual AI Chatbot",
    page_icon="🌍",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    text-align: center;
    margin-bottom: 0px;
}

.developer-name {
    text-align: center;
    color: #777;
    font-size: 16px;
    margin-top: 0px;
    margin-bottom: 25px;
}

.chat-box {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<h1 class="main-title">🌍 Multilingual AI Chatbot</h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="developer-name">by R@ees Khan</div>',
    unsafe_allow_html=True
)


# =========================================================
# GEMINI API
# =========================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        API_KEY = None

if not API_KEY:
    st.error("GEMINI_API_KEY is not configured.")
    st.stop()

client = genai.Client(api_key=API_KEY)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = ""

if "processed_submission" not in st.session_state:
    st.session_state.processed_submission = ""


# =========================================================
# LANGUAGE SETTINGS
# =========================================================

languages = [
    "English",
    "Urdu",
    "Pashto",
    "Arabic",
    "French",
    "Spanish",
    "Chinese"
]

tts_languages = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh-CN"
}


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🌍 Settings")

    selected_language = st.selectbox(
        "Select response language",
        languages,
        index=0
    )

    st.divider()

    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.processed_audio = ""
        st.session_state.processed_submission = ""
        st.rerun()

    st.divider()

    with st.expander("ℹ️ About"):

        st.markdown("""
        ### Multilingual AI Chatbot

        An AI-powered chatbot that can communicate using:

        - 💬 Text
        - 🎤 Voice
        - 🖼️ Images
        - 🌐 Multiple languages
        - 🔊 Voice responses

        **Developer:** R@ees Khan

        **Assistant Director Technical, NADRA**

        This project demonstrates how AI can combine
        text, speech and image understanding in one
        simple interface.
        """)

    with st.expander("💬 Feedback"):

        rating = st.slider(
            "How would you rate the chatbot?",
            1,
            5,
            5
        )

        feedback_type = st.selectbox(
            "Feedback type",
            [
                "Good experience",
                "Suggestion",
                "Report a problem",
                "Other"
            ]
        )

        comments = st.text_area(
            "Comments"
        )

        if st.button("Submit Feedback"):

            if comments.strip():

                st.success(
                    "Thank you! Your feedback has been recorded for this demo."
                )

            else:

                st.info(
                    "Please enter a comment before submitting."
                )

    st.divider()

    st.caption("Powered by Google Gemini")


# =========================================================
# DISPLAY PREVIOUS CHAT MESSAGES
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message.get("image") is not None:
            st.image(
                message["image"],
                use_container_width=True
            )

        if message.get("audio") is not None:
            st.audio(
                message["audio"],
                format="audio/mp3"
            )

        if message.get("content"):
            st.markdown(message["content"])


# =========================================================
# HELPER: BUILD CONVERSATION
# =========================================================

def build_conversation():

    conversation = []

    for message in st.session_state.messages:

        role = message["role"]
        content = message.get("content", "")

        if content:

            conversation.append(
                f"{role.upper()}: {content}"
            )

    return "\n".join(conversation)


# =========================================================
# HELPER: TEXT RESPONSE
# =========================================================

def ask_gemini(prompt):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text


# =========================================================
# HELPER: IMAGE RESPONSE
# =========================================================

def analyze_image(image_bytes, mime_type, question):

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = f"""
You are a helpful multilingual AI assistant.

Analyze the attached image carefully.

User's question:
{question if question.strip() else "Please describe and explain what you see in this image."}

Respond in {selected_language}.

Be accurate, useful and concise.
Do not claim to see something that is not actually visible.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            image_part,
            prompt
        ]
    )

    return response.text


# =========================================================
# HELPER: VOICE RESPONSE
# =========================================================

def process_voice(audio_bytes):

    temp_audio = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as f:

            f.write(audio_bytes)
            temp_audio = f.name

        uploaded_audio = client.files.upload(
            file=temp_audio
        )

        prompt = f"""
You are a multilingual AI assistant.

Listen carefully to the user's voice message.

Understand what the user said and answer naturally.

Respond in {selected_language}.

Keep the response useful and reasonably concise.
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                prompt,
                uploaded_audio
            ]
        )

        return response.text

    finally:

        if temp_audio and os.path.exists(temp_audio):

            os.remove(temp_audio)


# =========================================================
# HELPER: TEXT TO SPEECH
# =========================================================

def generate_voice(text):

    if selected_language not in tts_languages:
        return None

    try:

        language_code = tts_languages[selected_language]

        tts = gTTS(
            text=text,
            lang=language_code
        )

        audio_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        tts.save(audio_file.name)

        with open(audio_file.name, "rb") as f:
            audio_bytes = f.read()

        os.remove(audio_file.name)

        return audio_bytes

    except Exception:

        return None


# =========================================================
# UNIFIED CHAT INPUT
# =========================================================

chat_input = st.chat_input(
    "Type, attach 📎, or speak 🎤...", 
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ],
    accept_audio=True,
    audio_sample_rate=16000,
    max_upload_size=20,
    key="main_chat_input"
)


# =========================================================
# PROCESS USER SUBMISSION
# =========================================================

if chat_input:

    text_message = chat_input.text.strip()

    uploaded_files = chat_input.files
    audio_message = chat_input.audio


    # -----------------------------------------------------
    # IDENTIFY SUBMISSION
    # -----------------------------------------------------

    image_file = None

    if uploaded_files:

        for file in uploaded_files:

            if file.type and file.type.startswith("image/"):

                image_file = file
                break


    # -----------------------------------------------------
    # CREATE UNIQUE SUBMISSION ID
    # -----------------------------------------------------

    submission_data = (
        text_message
        + str(
            image_file.name
            if image_file
            else ""
        )
        + str(
            image_file.size
            if image_file
            else ""
        )
        + str(
            audio_message.name
            if audio_message
            else ""
        )
    )

    submission_hash = hashlib.md5(
        submission_data.encode()
    ).hexdigest()


    # -----------------------------------------------------
    # PREVENT DUPLICATE PROCESSING
    # -----------------------------------------------------

    if submission_hash != st.session_state.processed_submission:

        st.session_state.processed_submission = submission_hash


        # =================================================
        # IMAGE MESSAGE
        # =================================================

        if image_file:

            image_bytes = image_file.getvalue()

            st.session_state.messages.append({
                "role": "user",
                "content": text_message if text_message else "🖼️ Image",
                "image": image_bytes,
                "audio": None
            })

            with st.chat_message("user"):

                st.image(
                    image_bytes,
                    use_container_width=True
                )

                if text_message:
                    st.markdown(text_message)


            # -------------------------------------------------
            # ANALYZE IMAGE
            # -------------------------------------------------

            with st.chat_message("assistant"):

                with st.spinner("🖼️ Analyzing image..."):

                    try:

                        answer = analyze_image(
                            image_bytes,
                            image_file.type,
                            text_message
                        )

                        st.markdown(answer)

                        voice_audio = generate_voice(answer)

                        if voice_audio:

                            st.audio(
                                voice_audio,
                                format="audio/mp3"
                            )

                        elif selected_language == "Pashto":

                            st.warning(
                                "Voice output is not currently available for Pashto."
                            )

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "image": None,
                            "audio": voice_audio
                        })

                    except Exception as e:

                        st.error(
                            f"Image/Gemini error: {e}"
                        )


        # =================================================
        # VOICE MESSAGE
        # =================================================

        elif audio_message:

            audio_bytes = audio_message.getvalue()

            audio_hash = hashlib.md5(
                audio_bytes
            ).hexdigest()


            if audio_hash != st.session_state.processed_audio:

                st.session_state.processed_audio = audio_hash

                st.session_state.messages.append({
                    "role": "user",
                    "content": "🎤 Voice message",
                    "image": None,
                    "audio": audio_bytes
                })

                with st.chat_message("user"):

                    st.markdown("🎤 Voice message")

                    st.audio(
                        audio_bytes,
                        format="audio/wav"
                    )


                with st.chat_message("assistant"):

                    with st.spinner("🎤 Understanding your voice..."):

                        try:

                            answer = process_voice(
                                audio_bytes
                            )

                            st.markdown(answer)

                            voice_audio = generate_voice(
                                answer
                            )

                            if voice_audio:

                                st.audio(
                                    voice_audio,
                                    format="audio/mp3"
                                )

                            elif selected_language == "Pashto":

                                st.warning(
                                    "Voice output is not currently available for Pashto."
                                )

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "image": None,
                                "audio": voice_audio
                            })

                        except Exception as e:

                            st.error(
                                f"Voice/Gemini error: {e}"
                            )


        # =================================================
        # NORMAL TEXT MESSAGE
        # =================================================

        elif text_message:

            st.session_state.messages.append({
                "role": "user",
                "content": text_message,
                "image": None,
                "audio": None
            })

            with st.chat_message("user"):

                st.markdown(text_message)


            conversation = build_conversation()

            prompt = f"""
You are a helpful multilingual AI assistant.

Conversation so far:

{conversation}

The user has just sent a message.

Respond naturally and helpfully in {selected_language}.

Keep the response reasonably concise unless the user asks for
a detailed explanation.
"""


            with st.chat_message("assistant"):

                with st.spinner("🤖 Thinking..."):

                    try:

                        answer = ask_gemini(
                            prompt
                        )

                        st.markdown(answer)

                        voice_audio = generate_voice(
                            answer
                        )

                        if voice_audio:

                            st.audio(
                                voice_audio,
                                format="audio/mp3"
                            )

                        elif selected_language == "Pashto":

                            st.warning(
                                "Voice output is not currently available for Pashto."
                            )

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "image": None,
                            "audio": voice_audio
                        })

                    except Exception as e:

                        st.error(
                            f"Gemini error: {e}"
                        )
