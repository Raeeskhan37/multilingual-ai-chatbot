import os
import tempfile

import streamlit as st
from google import genai
from gtts import gTTS


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Multilingual AI Chatbot",
    page_icon="🌍"
)

st.title("🌍 Multilingual AI Chatbot")
st.caption("Chat with AI using text or voice in multiple languages.")


# -----------------------------
# Gemini setup
# -----------------------------

api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


# -----------------------------
# Session memory
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Language selection
# -----------------------------

language = st.selectbox(
    "🌍 Select response language",
    [
        "English",
        "Urdu",
        "Pashto",
        "Arabic",
        "French",
        "Spanish",
        "Chinese"
    ]
)


# -----------------------------
# Show chat history
# -----------------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -----------------------------
# Text input
# -----------------------------

message = st.chat_input("Type your message...")


# -----------------------------
# Voice input
# -----------------------------

audio = st.audio_input("🎤 Or record your message")


# -----------------------------
# Text-to-speech languages
# -----------------------------

tts_languages = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh-CN"
}


# -----------------------------
# Generate voice
# -----------------------------

def generate_voice(text, language):

    language_code = tts_languages.get(
        language,
        "en"
    )

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    temp_file.close()

    tts = gTTS(
        text=text,
        lang=language_code,
        slow=False
    )

    tts.save(temp_file.name)

    return temp_file.name


# -----------------------------
# Ask Gemini
# -----------------------------

import time


def ask_gemini(contents):

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents
            )

            return response.text

        except Exception as e:

            error_message = str(e)

            if "503" in error_message or "UNAVAILABLE" in error_message:

                if attempt < 2:
                    time.sleep(2)
                    continue

            raise e


# -----------------------------
# TEXT MESSAGE
# -----------------------------

if message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    with st.chat_message("user"):
        st.write(message)

    conversation = ""

    for msg in st.session_state.messages:

        conversation += (
            f'{msg["role"]}: {msg["content"]}\n'
        )

    prompt = f"""
You are a helpful multilingual AI assistant.

Respond naturally, clearly, and accurately in {language}.

Use the conversation history to understand
the user's current question.

Conversation history:
{conversation}

Answer the user's latest message.
"""

    try:

        answer = ask_gemini(prompt)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):

            st.write(answer)

            st.markdown("🔊 **Voice Output**")

            try:

                audio_file = generate_voice(
                    answer,
                    language
                )

                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()

                st.audio(
                    audio_bytes,
                    format="audio/mp3"
                )

            except Exception as voice_error:

                st.warning(
                    f"Voice output unavailable: {voice_error}"
                )

    except Exception as e:

        st.error(
            f"Gemini error: {e}"
        )

# -----------------------------
# VOICE MESSAGE
# -----------------------------

if audio:

    try:

        audio_path = "/tmp/voice.wav"

        with open(audio_path, "wb") as f:
            f.write(audio.getvalue())

        uploaded_audio = client.files.upload(
            file=audio_path
        )

        # Transcribe the user's voice
        transcription_prompt = """
Transcribe this voice message exactly.

Return only the spoken words.
Do not translate them.
Do not add explanations.
"""

        transcription_response = client.models.generate_content(
            model="gemini-3.5-transcribe",
            contents=[
                transcription_prompt,
                uploaded_audio
            ]
        )

        user_text = transcription_response.text

if not user_text:
    st.error("❌ Speech was received, but no text was returned by the transcription model.")
    st.stop()

user_text = user_text.strip()

        # Show the transcribed message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        with st.chat_message("user"):
            st.write(f"🎤 {user_text}")

        # Build conversation history
        conversation = ""

        for msg in st.session_state.messages:

            conversation += (
                f'{msg["role"]}: {msg["content"]}\n'
            )

        # Ask Gemini to answer
        prompt = f"""
You are a helpful multilingual AI assistant.

Respond naturally, clearly, and accurately in {language}.

Conversation history:
{conversation}

Answer the user's latest message.
"""

        answer = ask_gemini(prompt)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):

            st.write(answer)

            st.markdown("🔊 **Voice Output**")

            try:

                audio_file = generate_voice(
                    answer,
                    language
                )

                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()

                st.audio(
                    audio_bytes,
                    format="audio/mp3"
                )

            except Exception as voice_error:

                st.warning(
                    f"Voice output unavailable: {voice_error}"
                )

    except Exception as e:

        st.error(
            f"Voice transcription/Gemini error: {e}"
        )
