import json
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel


T = TypeVar(
    "T",
    bound=BaseModel,
)


def get_client(api_key: str):

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Please add it to Streamlit Secrets."
        )

    return genai.Client(
        api_key=api_key
    )


def generate_structured(
    prompt: str,
    schema: Type[T],
    api_key: str,
    model: str,
) -> T:

    client = get_client(
        api_key
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    # --------------------------------------------------------
    # Preferred parsed response
    # --------------------------------------------------------

    parsed = getattr(
        response,
        "parsed",
        None,
    )

    if parsed is not None:

        if isinstance(
            parsed,
            schema,
        ):
            return parsed

        return schema.model_validate(
            parsed
        )

    # --------------------------------------------------------
    # Fallback to text
    # --------------------------------------------------------

    text = getattr(
        response,
        "text",
        None,
    )

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # Remove Markdown JSON fences if Gemini returns them.
    if text.startswith(
        "```json"
    ):
        text = text[
            len("```json"):
        ]

    if text.endswith(
        "```"
    ):
        text = text[
            :-len("```")
        ]

    text = text.strip()

    try:

        return schema.model_validate_json(
            text
        )

    except Exception as json_error:

        try:

            data = json.loads(
                text
            )

            return schema.model_validate(
                data
            )

        except Exception as validation_error:

            raise ValueError(
                "Could not parse Gemini structured output. "
                f"JSON error: {json_error}. "
                f"Validation error: {validation_error}"
            ) from validation_error


def generate_text(
    prompt: str,
    api_key: str,
    model: str,
) -> str:

    client = get_client(
        api_key
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
        ),
    )

    text = getattr(
        response,
        "text",
        None,
    )

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    return text.strip()
