import os
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    gemini_api_key: str
    gemini_model: str
    esco_base_url: str

def get_settings() -> Settings:
    # Streamlit Cloud secrets take precedence over local environment variables.
    def secret_or_env(name: str, default: str = "") -> str:
        try:
            value = st.secrets.get(name, None)
            if value:
                return str(value)
        except Exception:
            pass
        return os.getenv(name, default)

    return Settings(
        gemini_api_key=secret_or_env("GEMINI_API_KEY"),
        gemini_model=secret_or_env("GEMINI_MODEL", "gemini-3.6-flash"),
        esco_base_url=secret_or_env(
            "ESCO_BASE_URL",
            "https://ec.europa.eu/esco/api",
        ),
    )
