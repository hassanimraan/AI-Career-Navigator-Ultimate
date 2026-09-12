import json
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def get_client(api_key: str):
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")
    return genai.Client(api_key=api_key)

def generate_structured(
    prompt: str,
    schema: Type[T],
    api_key: str,
    model: str,
) -> T:
    client = get_client(api_key)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    if getattr(response, "parsed", None) is not None:
        parsed = response.parsed
        if isinstance(parsed, schema):
            return parsed
        return schema.model_validate(parsed)

    text = getattr(response, "text", None)
    if not text:
        raise ValueError("Gemini returned an empty response.")

    try:
        return schema.model_validate_json(text)
    except Exception as exc:
        # Helpful fallback for SDK versions that return JSON as a fenced block.
        cleaned = text.strip().removeprefix("```json").removesuffix("```").strip()
        try:
            return schema.model_validate(json.loads(cleaned))
        except Exception:
            raise ValueError(f"Could not parse Gemini structured output: {exc}") from exc

def generate_text(prompt: str, api_key: str, model: str) -> str:
    client = get_client(api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.5),
    )
    return (response.text or "").strip()
