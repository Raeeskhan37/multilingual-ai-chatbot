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

if st.button("Ask AI") and message:

    prompt = f"""
    Understand the user's message regardless of its input language.
    Respond naturally in {language}.

    User message:
    {message}
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            st.write(response.text)
            break

        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                st.error("Gemini is temporarily unavailable. Please try again.")
