from services.gemini_client import generate_text
from services.prompts import counselor_prompt
from config import get_settings


def chat_with_counselor(
    question,
    profile,
    assessment,
    level,
    api_key,
    model,
):
    """
    Generate a response from the AI career counselor.
    """

    prompt = counselor_prompt(
        question,
        profile,
        assessment,
        level,
    )

    return generate_text(
        prompt,
        api_key,
        model,
    )


def get_chat_response(
    profile,
    message,
    conversation=None,
    experience_level="Beginner",
):
    """
    Streamlit-friendly wrapper used by app.py.
    """

    settings = get_settings()

    # Get the latest assessment from session state if available.
    assessment = None

    try:
        import streamlit as st

        assessment = st.session_state.get(
            "assessment",
            None,
        )
    except Exception:
        assessment = None

    # Include recent conversation context.
    conversation_text = ""

    if conversation:
        recent_messages = conversation[-10:]

        for item in recent_messages:
            role = item.get(
                "role",
                "user",
            )

            content = item.get(
                "content",
                "",
            )

            conversation_text += (
                f"{role}: {content}\n"
            )

    prompt = counselor_prompt(
        message,
        profile,
        assessment,
        experience_level,
    )

    if conversation_text:
        prompt = f"""
Previous conversation:

{conversation_text}

Current request:

{prompt}
"""

    return generate_text(
        prompt,
        settings.gemini_api_key,
        settings.gemini_model,
    )
