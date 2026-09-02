import os
import streamlit as st
import streamlit.components.v1 as components
from google import genai

# Get Gemini API key from Streamlit Secrets
api_key = os.environ["GEMINI_API_KEY"]

# Create Gemini client
client = genai.Client(api_key=api_key)

# App title
st.title("🌍 Multilingual AI Chatbot")

# Text input
message = st.text_area("Enter your message")

# Voice input
audio = st.audio_input("🎤 Record your message")

# Response language
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


# Browser/device voice output
def speak_text(text, language):

    language_codes = {
        "English": "en-US",
        "Urdu": "ur-PK",
        "Pashto": "ps-PK",
        "Arabic": "ar-SA",
        "French": "fr-FR",
        "Spanish": "es-ES",
        "Chinese": "zh-CN"
    }

    lang_code = language_codes.get(language, "en-US")

    # Make text safe for JavaScript
    safe_text = (
        text
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    components.html(
        f"""
        <script>
            const text = `{safe_text}`;

            const speech = new SpeechSynthesisUtterance(text);

            speech.lang = "{lang_code}";
            speech.rate = 0.9;
            speech.pitch = 1.0;

            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(speech);
        </script>
        """,
        height=0
    )


# Ask AI button
if st.button("Ask AI"):

    # -----------------------------
    # TEXT INPUT
    # -----------------------------
    if message:

        prompt = f"""
Understand the user's message regardless of the language used.

Answer naturally and clearly in {language}.

User message:
{message}
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            answer = response.text

            st.write(answer)

            st.markdown("🔊 **Voice Output**")

            speak_text(answer, language)

        except Exception as e:

            st.error(f"Gemini error: {e}")


    # -----------------------------
    # VOICE INPUT
    # -----------------------------
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
Listen to the user's voice message.

Understand what the user is saying, regardless of the language.

Respond naturally and clearly in {language}.
"""

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    prompt,
                    uploaded_audio
                ]
            )

            answer = response.text

            st.write(answer)

            st.markdown("🔊 **Voice Output**")

            speak_text(answer, language)

        except Exception as e:

            st.error(f"Voice/Gemini error: {e}")


    # -----------------------------
    # NO INPUT
    # -----------------------------
    else:

        st.warning(
            "Please type a message or record your voice."
        )
