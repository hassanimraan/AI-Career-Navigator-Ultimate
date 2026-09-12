from services.gemini_client import generate_text
from services.prompts import counselor_prompt

def chat_with_counselor(
    question,
    profile,
    assessment,
    level,
    api_key,
    model,
):
    prompt = counselor_prompt(question, profile, assessment, level)
    return generate_text(prompt, api_key, model)
