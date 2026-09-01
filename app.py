import os
import time
import streamlit as st
from google import genai

api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

st.title("🌍 Multilingual AI Chatbot")

message = st.text_area("Enter your message")

language = st.selectbox(
    "Select response language",
    ["English", "Urdu", "Pashto", "Arabic", "French", "Spanish", "Chinese"]
)

st.subheader("🎤 Or speak your message")
audio = st.audio_input("Record your message")

if audio:
    st.audio(audio)

if st.button("Ask AI"):

    if not message and not audio:
        st.warning("Please type a message or record your voice.")

    else:

        prompt = f"""
        Understand the user's message regardless of its language.

        Respond naturally in {language}.

        If the user provides audio, first understand what the
        user said and then respond in the selected language.
        """

        for attempt in range(3):

            try:

                if audio:

                    # Upload recorded audio to Gemini
                    audio_file = client.files.upload(
                        file=audio
                    )

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            audio_file,
                            prompt
                        ]
                    )

                else:

                    # Existing working text path
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=f"""
                        {prompt}

                        User message:
                        {message}
                        """
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
