import os
import tempfile

import streamlit as st
from google import genai
from gtts import gTTS


# -----------------------------------
# Gemini API
# -----------------------------------

api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


# -----------------------------------
# App Title
# -----------------------------------

st.title("🌍 Multilingual AI Chatbot")


# -----------------------------------
# User Inputs
# -----------------------------------

message = st.text_area("Enter your message")

audio = st.audio_input("🎤 Record your message")


language = st.selectbox(
    "Select response language",
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


# -----------------------------------
# gTTS Language Codes
# -----------------------------------

tts_languages = {
    "English": "en",
    "Urdu": "ur",
    "Pashto": "ps",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh-CN"
}


# -----------------------------------
# Generate Voice
# -----------------------------------

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


# -----------------------------------
# Ask AI
# -----------------------------------

if st.button("Ask AI"):

    # =================================
    # TEXT INPUT
    # =================================

    if message:

        prompt = f"""
Understand the user's message regardless
of the language used.

Answer naturally, clearly, and accurately
in {language}.

User message:
{message}
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            answer = response.text

            # Display text answer
            st.write(answer)

            # Generate voice
            st.markdown("### 🔊 Voice Output")

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

                st.error(
                    f"Voice generation error: {voice_error}"
                )


        except Exception as e:

            st.error(
                f"Gemini error: {e}"
            )


    # =================================
    # VOICE INPUT
    # =================================

    elif audio:

        try:

            audio_path = "/tmp/voice.wav"

            # Save recorded audio
            with open(audio_path, "wb") as f:

                f.write(audio.getvalue())


            # Upload audio to Gemini
            uploaded_audio = client.files.upload(
                file=audio_path
            )


            prompt = f"""
Listen carefully to the user's voice message.

Understand what the user is saying regardless
of the language used.

Respond naturally, clearly, and accurately
in {language}.
"""


            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    prompt,
                    uploaded_audio
                ]
            )


            answer = response.text

            # Display text answer
            st.write(answer)

            # Generate voice
            st.markdown("### 🔊 Voice Output")

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

                st.error(
                    f"Voice generation error: {voice_error}"
                )


        except Exception as e:

            st.error(
                f"Voice/Gemini error: {e}"
            )


    # =================================
    # NO INPUT
    # =================================

    else:

        st.warning(
            "Please type a message or record your voice."
        )
