from services.gemini_client import generate_text
from services.prompts import counselor_prompt
from config import get_settings


def get_chat_response(
    profile,
    message,
    conversation=None,
    experience_level="Beginner",
):
    settings = get_settings()

    # Convert conversation into a simple text history
    conversation_text = ""

    if conversation:
        for item in conversation:
            role = item.get("role", "user")
            content = item.get("content", "")
            conversation_text += f"{role}: {content}\n"

    # Build the counselor prompt
    prompt = counselor_prompt(
        message,
        profile,
        None,
        experience_level,
    )

    # Add conversation history if available
    if conversation_text:
        prompt = (
            "Previous conversation:\n"
            f"{conversation_text}\n\n"
            "Current question:\n"
            f"{prompt}"
        )

    return generate_text(
        prompt,
        settings.gemini_api_key,
        settings.gemini_model,
    )
