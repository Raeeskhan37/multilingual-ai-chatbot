import os
import tempfile

import streamlit as st
from google import genai
from gtts import gTTS


# -----------------------------
# PAGE SETTINGS
# -----------------------------

st.set_page_config(
    page_title="Multilingual AI Chatbot",
    page_icon="🌍"
)


# -----------------------------
# TITLE
# -----------------------------

st.title("🌍 Multilingual AI Chatbot")

st.caption(
    "Chat with AI using text or voice in multiple languages."
)


# -----------------------------
# GEMINI CLIENT
# -----------------------------

api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)


# -----------------------------
# CHAT MEMORY
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# LANGUAGE SELECTION
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
# DISPLAY CHAT HISTORY
# -----------------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])


# -----------------------------
# TEXT INPUT
# -----------------------------

message = st.chat_input(
    "Type your message..."
)


# -----------------------------
# VOICE INPUT
# -----------------------------

audio = st.audio_input(
    "🎤 Or record your message"
)


# -----------------------------
# TEXT TO SPEECH LANGUAGES
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
# TEXT TO SPEECH FUNCTION
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

    tts.save(
        temp_file.name
    )

    return temp_file.name


# -----------------------------
# GEMINI TEXT FUNCTION
# -----------------------------

def ask_gemini(prompt):

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    return response.text


# -----------------------------
# TEXT MESSAGE
# -----------------------------

if message:

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    # Display user message
    with st.chat_message("user"):

        st.write(message)


    # Build conversation history
    conversation = ""

    for msg in st.session_state.messages:

        conversation += (
            f'{msg["role"]}: {msg["content"]}\n'
        )


    # Create AI prompt
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

        answer = ask_gemini(
            prompt
        )


        # Save AI answer
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        # Display AI answer
        with st.chat_message("assistant"):

            st.write(answer)

            st.markdown(
                "🔊 **Voice Output**"
            )


            # Generate voice
            try:

                audio_file = generate_voice(
                    answer,
                    language
                )

                with open(
                    audio_file,
                    "rb"
                ) as f:

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

        # Save audio
        audio_path = "/tmp/voice.wav"

        with open(
            audio_path,
            "wb"
        ) as f:

            f.write(
                audio.getvalue()
            )


        # Upload audio to Gemini
        uploaded_audio = client.files.upload(
            file=audio_path
        )


        # Build conversation history
        conversation = ""

        for msg in st.session_state.messages:

            conversation += (
                f'{msg["role"]}: {msg["content"]}\n'
            )


        # Ask Gemini to understand the audio
        prompt = f"""
You are a helpful multilingual AI assistant.

The user has sent a voice message.

First understand what the user said from the audio.

Then answer the user's question or request.

Respond naturally, clearly, and accurately in {language}.

Do not explain that the message was audio.

Conversation history:

{conversation}

Answer the user's voice message.
"""


        # Gemini processes audio directly
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=[
                prompt,
                uploaded_audio
            ]
        )


        answer = response.text


        if not answer:

            st.error(
                "❌ Gemini received the voice message but returned no answer."
            )

            st.stop()


        # Save user voice message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": "🎤 Voice message"
            }
        )


        # Display user voice message
        with st.chat_message("user"):

            st.write(
                "🎤 Voice message"
            )


        # Save AI answer
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        # Display AI answer
        with st.chat_message("assistant"):

            st.write(answer)

            st.markdown(
                "🔊 **Voice Output**"
            )


            # Generate voice output
            try:

                audio_file = generate_voice(
                    answer,
                    language
                )

                with open(
                    audio_file,
                    "rb"
                ) as f:

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
            f"Voice/Gemini error: {e}"
        )
