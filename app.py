import os
import tempfile
import hashlib

import streamlit as st
from google import genai
from gtts import gTTS


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Multilingual AI Chatbot",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 1.5rem;
    }

    .about-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .feature-card {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.20);
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🌍 Multilingual AI Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Chat naturally using text or voice in multiple languages.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# GEMINI CLIENT
# =========================================================

api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🌍 Settings")

    language = st.selectbox(
        "Response language",
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

    st.divider()

    # -----------------------------------------------------
    # CLEAR CHAT
    # -----------------------------------------------------

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.processed_audio = None

        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # ABOUT
    # -----------------------------------------------------

    with st.expander("ℹ️ About"):

        st.markdown(
            """
            ### 🌍 Multilingual AI Chatbot

            An AI-powered chatbot designed to make
            AI interaction more accessible through
            **text and voice**.

            ### ✨ Features

            • Multilingual AI conversation  
            • Text input  
            • Voice input  
            • AI-generated responses  
            • Voice output  
            • Conversation memory  
            • Mobile-friendly interface  

            ### 👨‍💻 Developer

            **Raees Khan**

            Assistant Director Technical, NADRA

            This project was developed as an AI
            application demonstrating practical use
            of Generative AI, multilingual interaction,
            and voice-enabled communication.

            ### 🎯 Purpose

            To demonstrate how modern AI can provide
            a simple and accessible conversational
            interface for users communicating in
            different languages.
            """
        )

    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    with st.expander("💬 Feedback"):

        st.markdown(
            "Your feedback helps improve this project."
        )

        rating = st.select_slider(
            "How would you rate your experience?",
            options=[
                1,
                2,
                3,
                4,
                5
            ],
            value=5
        )

        feedback_type = st.selectbox(
            "Feedback type",
            [
                "👍 Good experience",
                "💡 Suggestion",
                "🐛 Report a problem",
                "📝 Other"
            ]
        )

        feedback_text = st.text_area(
            "Your comments",
            placeholder="Tell us what you think..."
        )

        if st.button(
            "📨 Submit Feedback",
            use_container_width=True
        ):

            st.success(
                "Thank you for your feedback! ❤️"
            )

            st.info(
                "Feedback collection can be connected "
                "to Google Forms in the next step."
            )

    st.divider()

    st.caption(
        "Powered by Google Gemini"
    )


# =========================================================
# DISPLAY PREVIOUS MESSAGES
# =========================================================

for msg in st.session_state.messages:

    with st.chat_message(
        msg["role"]
    ):

        st.write(
            msg["content"]
        )

        # Play saved voice response if available
        if (
            msg["role"] == "assistant"
            and "audio" in msg
            and msg["audio"] is not None
        ):

            st.audio(
                msg["audio"],
                format="audio/mp3"
            )


# =========================================================
# TEXT TO SPEECH
# =========================================================

tts_languages = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh-CN"
}


def generate_voice(
    text,
    language
):

    language_code = tts_languages.get(
        language
    )

    if not language_code:
        return None

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


# =========================================================
# GEMINI TEXT RESPONSE
# =========================================================

def ask_gemini(
    prompt
):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text


# =========================================================
# BUILD CONVERSATION HISTORY
# =========================================================

def build_conversation():

    conversation = ""

    for msg in st.session_state.messages:

        conversation += (
            f'{msg["role"]}: '
            f'{msg["content"]}\n'
        )

    return conversation


# =========================================================
# CHAT INPUT
# =========================================================

chat_input = st.chat_input(
    "Type a message or tap 🎤 to speak...",
    accept_audio=True,
    audio_sample_rate=16000,
    key="main_chat_input"
)


# =========================================================
# PROCESS CHAT INPUT
# =========================================================

if chat_input:

    text_message = chat_input.text
    audio_message = chat_input.audio

    # -----------------------------------------------------
    # TEXT MESSAGE
    # -----------------------------------------------------

    if text_message:

        user_text = text_message.strip()

        if user_text:

            # Save user message
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_text
                }
            )

            # Display user message
            with st.chat_message("user"):

                st.write(
                    user_text
                )

            conversation = build_conversation()

            prompt = f"""
You are a helpful multilingual AI assistant.

Respond naturally, clearly, and accurately
in {language}.

Keep responses concise unless the user asks
for detailed information.

Use the conversation history to understand
the current question.

Conversation history:

{conversation}

Answer the user's latest message.
"""

            try:

                with st.chat_message(
                    "assistant"
                ):

                    with st.spinner(
                        "🤖 Thinking..."
                    ):

                        answer = ask_gemini(
                            prompt
                        )

                    st.write(
                        answer
                    )

                    # Voice output
                    try:

                        audio_file = generate_voice(
                            answer,
                            language
                        )

                        audio_bytes = None

                        if audio_file:

                            with open(
                                audio_file,
                                "rb"
                            ) as f:

                                audio_bytes = f.read()

                            st.audio(
                                audio_bytes,
                                format="audio/mp3"
                            )

                        else:

                            st.caption(
                                "🔊 Voice output is not "
                                "currently available for this language."
                            )

                    except Exception as voice_error:

                        st.caption(
                            f"🔊 Voice output unavailable: "
                            f"{voice_error}"
                        )


                # Save assistant response
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "audio": audio_bytes
                    }
                )

            except Exception as e:

                st.error(
                    f"Gemini error: {e}"
                )


    # -----------------------------------------------------
    # VOICE MESSAGE
    # -----------------------------------------------------

    elif audio_message:

        # Create unique fingerprint
        audio_bytes = audio_message.getvalue()

        audio_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        # Prevent duplicate processing
        if (
            audio_hash
            == st.session_state.processed_audio
        ):

            st.stop()

        st.session_state.processed_audio = audio_hash

        try:

            # Save temporary audio
            audio_path = "/tmp/user_voice.wav"

            with open(
                audio_path,
                "wb"
            ) as f:

                f.write(
                    audio_bytes
                )


            # Upload audio to Gemini
            uploaded_audio = client.files.upload(
                file=audio_path
            )


            conversation = build_conversation()


            # Direct audio understanding
            prompt = f"""
You are a helpful multilingual AI assistant.

The user has sent a voice message.

Understand the user's spoken words from
the audio and answer their request.

Respond naturally, clearly, and accurately
in {language}.

Keep the response concise unless the user
asks for a detailed explanation.

Do not describe the audio.
Do not explain your processing.

Conversation history:

{conversation}

Answer the user's voice message.
"""


            with st.chat_message(
                "user"
            ):

                st.write(
                    "🎤 Voice message"
                )


            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "🎤 Understanding and thinking..."
                ):

                    response = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=[
                            prompt,
                            uploaded_audio
                        ]
                    )


                answer = response.text


                if not answer:

                    st.error(
                        "Gemini received the voice "
                        "message but returned no answer."
                    )

                    st.stop()


                st.write(
                    answer
                )


                # Voice output
                audio_output = None

                try:

                    audio_file = generate_voice(
                        answer,
                        language
                    )

                    if audio_file:

                        with open(
                            audio_file,
                            "rb"
                        ) as f:

                            audio_output = f.read()


                        st.audio(
                            audio_output,
                            format="audio/mp3"
                        )

                    else:

                        st.caption(
                            "🔊 Voice output is not "
                            "currently available for this language."
                        )

                except Exception as voice_error:

                    st.caption(
                        f"🔊 Voice output unavailable: "
                        f"{voice_error}"
                    )


            # Save voice interaction
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": "🎤 Voice message"
                }
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "audio": audio_output
                }
            )


        except Exception as e:

            st.error(
                f"Voice/Gemini error: {e}"
            )
