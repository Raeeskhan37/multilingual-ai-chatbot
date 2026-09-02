import os
import tempfile
import hashlib

import streamlit as st
from google import genai
from gtts import gTTS


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Multilingual AI Chatbot by R@ees Khan",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 2.25rem;
        font-weight: 750;
        margin-top: 0.5rem;
        margin-bottom: 0.1rem;
        letter-spacing: -0.5px;
    }

    .developer-name {
        text-align: center;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.15rem;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 650;
        margin-top: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🌍 Multilingual AI Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="developer-name">by R@ees Khan</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Chat naturally using text, voice, or images in multiple languages.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# GEMINI CLIENT
# --------------------------------------------------

api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = None

if "uploaded_image_hash" not in st.session_state:
    st.session_state.uploaded_image_hash = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

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

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.processed_audio = None
        st.session_state.uploaded_image_hash = None

        st.rerun()

    st.divider()

    # --------------------------------------------------
    # ABOUT
    # --------------------------------------------------

    with st.expander("ℹ️ About"):

        st.markdown(
            """
            ### 🌍 Multilingual AI Chatbot

            An AI-powered chatbot designed to make
            AI interaction more accessible through
            **text, voice, and images**.

            ### ✨ Features

            • Multilingual AI conversation  
            • Text input  
            • Voice input  
            • Image upload  
            • Camera capture  
            • Image understanding  
            • AI-generated responses  
            • Voice output  
            • Conversation memory  
            • Mobile-friendly interface  

            ### 👨‍💻 Developer

            **R@ees Khan**

            Assistant Director Technical, NADRA

            This project demonstrates practical use
            of Generative AI, multilingual interaction,
            voice-enabled communication, and
            multimodal AI.

            ### 🎯 Purpose

            To demonstrate how modern AI can provide
            a simple and accessible conversational
            interface for users communicating through
            text, voice, and images.
            """
        )

    # --------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------

    with st.expander("💬 Feedback"):

        st.markdown(
            "Your feedback helps improve this project."
        )

        rating = st.select_slider(
            "How would you rate your experience?",
            options=[1, 2, 3, 4, 5],
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

    st.caption("Powered by Google Gemini")


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])

        if (
            msg["role"] == "assistant"
            and "audio" in msg
            and msg["audio"] is not None
        ):

            st.audio(
                msg["audio"],
                format="audio/mp3"
            )


# --------------------------------------------------
# TEXT TO SPEECH
# --------------------------------------------------

tts_languages = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh-CN"
}


def generate_voice(text, language):

    language_code = tts_languages.get(language)

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

    tts.save(temp_file.name)

    return temp_file.name


# --------------------------------------------------
# GEMINI TEXT FUNCTION
# --------------------------------------------------

def ask_gemini(prompt):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text


# --------------------------------------------------
# CONVERSATION HISTORY
# --------------------------------------------------

def build_conversation():

    conversation = ""

    for msg in st.session_state.messages:

        conversation += (
            f'{msg["role"]}: '
            f'{msg["content"]}\n'
        )

    return conversation


# --------------------------------------------------
# IMAGE & CAMERA
# --------------------------------------------------

st.markdown(
    '<div class="section-title">🖼️ Image & Camera</div>',
    unsafe_allow_html=True
)

image_tab1, image_tab2 = st.tabs(
    [
        "🖼️ Upload Image",
        "📷 Take Photo"
    ]
)


# --------------------------------------------------
# IMAGE UPLOAD
# --------------------------------------------------

uploaded_image = None

with image_tab1:

    uploaded_image = st.file_uploader(
        "Choose an image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        help="Upload an image for Gemini to analyze."
    )


# --------------------------------------------------
# CAMERA
# --------------------------------------------------

camera_image = None

with image_tab2:

    camera_image = st.camera_input(
        "Take a photo"
    )


# --------------------------------------------------
# SELECT IMAGE
# --------------------------------------------------

selected_image = None

if camera_image is not None:

    selected_image = camera_image

elif uploaded_image is not None:

    selected_image = uploaded_image


# --------------------------------------------------
# DISPLAY IMAGE
# --------------------------------------------------

if selected_image is not None:

    st.image(
        selected_image,
        caption="Selected image",
        use_container_width=True
    )


# --------------------------------------------------
# IMAGE QUESTION
# --------------------------------------------------

if selected_image is not None:

    image_question = st.text_input(
        "💬 What would you like me to do with this image?",
        placeholder=(
            "Example: Describe this image, "
            "read the text, or explain what you see."
        ),
        key="image_question"
    )

    analyze_image = st.button(
        "🔍 Analyze Image",
        use_container_width=True
    )

    if analyze_image:

        image_bytes = selected_image.getvalue()

        image_hash = hashlib.md5(
            image_bytes
        ).hexdigest()

        if (
            image_hash
            == st.session_state.uploaded_image_hash
        ):

            st.info(
                "This image has already been analyzed."
            )

        else:

            st.session_state.uploaded_image_hash = image_hash

            if not image_question.strip():

                image_question = (
                    "Describe this image and explain "
                    "the important information visible in it."
                )

            try:

                image_path = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".jpg"
                ).name

                with open(
                    image_path,
                    "wb"
                ) as f:

                    f.write(image_bytes)

                uploaded_file = client.files.upload(
                    file=image_path
                )

                conversation = build_conversation()

                image_prompt = f"""
You are a helpful multilingual AI assistant.

The user has provided an image.

Analyze the image carefully and answer the
user's question.

Respond naturally, clearly, and accurately
in {language}.

If the image contains text, read and explain
the text when relevant.

If the image contains an object, document,
diagram, scene, screenshot, or other visual
information, explain what is visible.

Do not claim to see information that is not
actually visible in the image.

Keep the response concise unless the user asks
for a detailed explanation.

Conversation history:

{conversation}

User's image question:

{image_question}

Answer the user's question about the image.
"""

                with st.chat_message("user"):

                    st.write(
                        f"🖼️ Image: {image_question}"
                    )

                with st.chat_message("assistant"):

                    with st.spinner(
                        "🖼️ Analyzing image..."
                    ):

                        response = client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=[
                                image_prompt,
                                uploaded_file
                            ]
                        )

                    answer = response.text

                    if not answer:

                        st.error(
                            "Gemini analyzed the image "
                            "but returned no answer."
                        )

                        st.stop()

                    st.write(answer)

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

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"🖼️ Image: "
                            f"{image_question}"
                        )
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
                    f"Image/Gemini error: {e}"
                )


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

chat_input = st.chat_input(
    "Type a message or tap 🎤 to speak...",
    accept_audio=True,
    audio_sample_rate=16000,
    key="main_chat_input"
)


# --------------------------------------------------
# TEXT OR VOICE PROCESSING
# --------------------------------------------------

if chat_input:

    text_message = chat_input.text

    audio_message = chat_input.audio


    # --------------------------------------------------
    # TEXT MESSAGE
    # --------------------------------------------------

    if text_message:

        user_text = text_message.strip()

        if user_text:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_text
                }
            )

            with st.chat_message("user"):

                st.write(user_text)

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

                with st.chat_message("assistant"):

                    with st.spinner(
                        "🤖 Thinking..."
                    ):

                        answer = ask_gemini(prompt)

                    st.write(answer)

                    audio_bytes = None

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


    # --------------------------------------------------
    # VOICE MESSAGE
    # --------------------------------------------------

    elif audio_message:

        audio_bytes = audio_message.getvalue()

        audio_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        if (
            audio_hash
            == st.session_state.processed_audio
        ):

            st.stop()

        st.session_state.processed_audio = audio_hash

        try:

            audio_path = "/tmp/user_voice.wav"

            with open(
                audio_path,
                "wb"
            ) as f:

                f.write(audio_bytes)

            uploaded_audio = client.files.upload(
                file=audio_path
            )

            conversation = build_conversation()

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

            with st.chat_message("user"):

                st.write(
                    "🎤 Voice message"
                )

            with st.chat_message("assistant"):

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

                st.write(answer)

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
