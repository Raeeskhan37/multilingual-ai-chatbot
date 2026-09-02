import os
import json
import streamlit as st
import streamlit.components.v1 as components
from google import genai


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
# Browser Voice Output
# -----------------------------------

def speak_button(text, language):

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

    # Convert Python text into safe JavaScript text
    text_json = json.dumps(text, ensure_ascii=False)
    lang_json = json.dumps(lang_code)

    components.html(
        f"""
        <!DOCTYPE html>

        <html>

        <head>

        <meta charset="UTF-8">

        <style>

        button {{
            background-color: #f0f2f6;
            border: 1px solid #999;
            border-radius: 8px;
            padding: 10px 18px;
            font-size: 16px;
            cursor: pointer;
        }}

        button:active {{
            transform: scale(0.98);
        }}

        </style>

        </head>

        <body>

        <button onclick="speakAnswer()">
            🔊 Speak Answer
        </button>

        <script>

        const answerText = {text_json};

        const answerLanguage = {lang_json};


        function speakAnswer() {{

            // Check whether browser supports speech
            if (!("speechSynthesis" in window)) {{

                alert(
                    "Speech output is not supported by this browser."
                );

                return;
            }}


            // Stop any previous speech
            window.speechSynthesis.cancel();


            // Create speech
            const speech =
                new SpeechSynthesisUtterance(answerText);


            // Set selected language
            speech.lang = answerLanguage;


            // Speech speed
            speech.rate = 0.9;


            // Normal pitch
            speech.pitch = 1.0;


            // Try to find a matching voice
            const voices =
                window.speechSynthesis.getVoices();

            const languagePrefix =
                answerLanguage
                .split("-")[0]
                .toLowerCase();


            const matchingVoice =
                voices.find(
                    voice =>
                        voice.lang
                        .toLowerCase()
                        .startsWith(languagePrefix)
                );


            if (matchingVoice) {{

                speech.voice = matchingVoice;

            }}


            // Speak
            window.speechSynthesis.speak(speech);

        }}

        </script>

        </body>

        </html>
        """,
        height=60
    )


# -----------------------------------
# Ask AI
# -----------------------------------

if st.button("Ask AI"):


    # =================================
    # TEXT INPUT
    # =================================

    if message:

        prompt = f"""
Understand the user's message regardless of the language used.

Answer naturally, clearly, and accurately in {language}.

User message:
{message}
"""


        try:

            response = client.models.generate_content(

                model="gemini-3.6-flash",

                contents=prompt

            )


            answer = response.text


            # Display answer
            st.write(answer)


            # Voice output
            st.markdown("### 🔊 Voice Output")

            speak_button(answer, language)


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

Respond naturally, clearly, and accurately in {language}.
"""


            response = client.models.generate_content(

                model="gemini-3.6-flash",

                contents=[
                    prompt,
                    uploaded_audio
                ]

            )


            answer = response.text


            # Display answer
            st.write(answer)


            # Voice output
            st.markdown("### 🔊 Voice Output")

            speak_button(answer, language)


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
