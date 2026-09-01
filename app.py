import os
import streamlit as st
from google import genai

api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

st.title("🌍 Multilingual AI Chatbot")

message = st.text_area("Enter your message")
language = st.selectbox("Select response language", ["English", "Urdu", "Pashto", "Arabic", "French", "Spanish", "Chinese"])

response = client.models.generate_content(model="gemini-3.6-flash", contents=f"Understand the user's message regardless of its input language. Respond naturally in {language}. User message: {message}") if st.button("Ask AI") and message else None

st.write(response.text if response else "")
