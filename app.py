import os
import tempfile

import streamlit as st
from google import genai
from gtts import gTTS


st.set_page_config(
    page_title="Multilingual AI Chatbot",
    page_icon="🌍"
)

st.title("🌍 Multilingual AI Chatbot")
st.caption("Chat with AI using text or voice in multiple languages.")


api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


if "messages" not in st.session_state:
    st.session_state.messages = []


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


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


message = st.chat_input("Type your message...")


audio = st.audio_input("🎤 Or record your message")


tts_languages = {
    "English": "en",
    "Urdu": "ur",
    "Pashto": "ps",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh-CN"
}


def generate_voice(text, language):

    language_code = tts_languages.get(language, "en")

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


def ask_gemini(contents):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents
    )

    return response.text


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

Conversation:
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
