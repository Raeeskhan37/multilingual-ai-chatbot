import os
import time
import streamlit as st
from google import genai

# Get API key securely
api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Page title
st.title("🌍 Multilingual AI Chatbot")

# Response language
languages = [
    "English",
    "Urdu",
    "Pashto",
    "Arabic",
    "French",
    "Spanish",
    "Chinese"
]

language = st.selectbox(
    "Select response language",
    languages
)

# Text input
st.subheader("✍️ Type your message")
message = st.text_area("Enter your message")

# Voice input
st.subheader("🎤 Or speak your message")
audio = st.audio_input("Record your message")

# Ask AI button
if st.button("Ask AI"):

    if not message and not audio:
        st.warning("Please type a message or record your voice.")

    else:

        prompt = f"""
        You are a multilingual AI assistant.

        Understand the user's message regardless of the language
        in which it was provided.

        Respond naturally in {language}.

        If the user provides audio, first understand what the
        user said and then respond in the selected language.
        """

        for attempt in range(3):

            try:

                if audio:
                    # Send recorded audio to Gemini
                    audio_bytes = audio.getvalue()

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            prompt,
                            {
                                "inline_data": {
                                    "mime_type": "audio/wav",
                                    "data": audio_bytes
                                }
                            }
                        ]
                    )

                else:
                    # Send typed message to Gemini
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            prompt,
                            message
                        ]
                    )

                st.success("AI Response")
                st.write(response.text)

                break

            except Exception as e:

                if attempt < 2:
                    time.sleep(2)

                else:
                    st.error(
                        "Gemini is temporarily unavailable. "
                        "Please try again."
                    )
