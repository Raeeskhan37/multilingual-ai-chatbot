import os
import streamlit as st
from google import genai

api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

st.title("🌍 Multilingual AI Chatbot")

message = st.text_area("Enter your message")

audio = st.audio_input("🎤 Record your message")

language = st.selectbox(
    "Select response language",
    ["English", "Urdu", "Pashto", "Arabic", "French", "Spanish", "Chinese"]
)

if st.button("Ask AI"):

    # TEXT INPUT
    if message:

        prompt = f"""
Understand the user's message regardless of its input language.
Respond naturally in {language}.

User message:
{message}
"""

        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            st.write(response.text)

        except Exception as e:
            st.error(f"Gemini error: {e}")

    # VOICE INPUT
    elif audio:

        try:
            audio_path = "/tmp/voice.wav"

            with open(audio_path, "wb") as f:
                f.write(audio.getvalue())

            uploaded_audio = client.files.upload(file=audio_path)

            prompt = f"""
Listen to the user's voice message.
Understand what the user is saying.
Respond naturally in {language}.

If the voice message is in any language, understand it and answer in the selected language.
"""

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt, uploaded_audio]
            )

            st.write(response.text)

        except Exception as e:
            st.error(f"Voice/Gemini error: {e}")

    else:
        st.warning("Please type a message or record your voice.")
