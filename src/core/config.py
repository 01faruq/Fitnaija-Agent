"""Configuration and safe secrets loading for FitNaija+."""

import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def sanitize_secret(val: str | None) -> str | None:
    """Clean and validate secret string, stripping quotes and whitespace."""
    if not val:
        return None
    cleaned = str(val).strip().strip('"').strip("'").strip()
    if not cleaned:
        return None
    # Filter out dummy placeholder values
    if cleaned.lower() in ("your_groq_api_key_here", "none", "null", ""):
        return None
    if cleaned.startswith("your_") or cleaned.startswith("gsk_your_"):
        return None
    return cleaned


def get_groq_api_key() -> str | None:
    """Retrieve Groq API key safely from Streamlit secrets or OS environment.
    
    Priority:
    1. Streamlit secrets (`st.secrets["GROQ_API_KEY"]`)
    2. Local environment variables (`os.environ["GROQ_API_KEY"]`), re-reading .env with override
    """
    # Force fresh load of .env if it exists so changes in the file are picked up
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    else:
        load_dotenv(override=True)

    key = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            key = sanitize_secret(st.secrets.get("GROQ_API_KEY"))
    except Exception:
        pass

    if not key:
        key = sanitize_secret(os.environ.get("GROQ_API_KEY"))

    return key


def get_groq_model() -> str:
    """Retrieve default Groq model identifier."""
    model = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_MODEL" in st.secrets:
            model = sanitize_secret(st.secrets.get("GROQ_MODEL"))
    except Exception:
        pass

    if not model:
        model = sanitize_secret(os.environ.get("GROQ_MODEL"))

    return model if model else DEFAULT_GROQ_MODEL


def get_yarngpt_api_key() -> str | None:
    """Retrieve YarnGPT API key safely from Streamlit secrets or OS environment.
    
    YarnGPT (saheedniyi/yarngpt.ai) provides studio-grade Nigerian accent
    and indigenous language (Yoruba, Igbo, Hausa) text-to-speech.
    """
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    else:
        load_dotenv(override=True)

    key = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "YARNGPT_API_KEY" in st.secrets:
            key = sanitize_secret(st.secrets.get("YARNGPT_API_KEY"))
    except Exception:
        pass

    if not key:
        key = sanitize_secret(os.environ.get("YARNGPT_API_KEY"))

    # Smart fallback: inspect .env lines for any raw sk_live_ token
    if not key and ENV_PATH.exists():
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if "sk_live_" in line_str:
                        # Extract token part
                        token_part = line_str.split("=")[-1].strip().strip('"').strip("'")
                        if token_part.startswith("sk_live_"):
                            key = sanitize_secret(token_part)
                            break
        except Exception:
            pass

    return key


def get_gemini_api_key() -> str | None:
    """Retrieve Google Gemini API key safely from Streamlit secrets, .env, or OS environment.
    
    Get a free API key at: https://aistudio.google.com/app/apikey
    """
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    else:
        load_dotenv(override=True)

    key = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = sanitize_secret(st.secrets.get("GEMINI_API_KEY"))
    except Exception:
        pass

    if not key:
        key = sanitize_secret(os.environ.get("GEMINI_API_KEY"))

    return key


DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"


def get_gemini_model() -> str:
    """Retrieve default Google Gemini model identifier."""
    model = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_MODEL" in st.secrets:
            model = sanitize_secret(st.secrets.get("GEMINI_MODEL"))
    except Exception:
        pass

    if not model:
        model = sanitize_secret(os.environ.get("GEMINI_MODEL"))

    return model if model else DEFAULT_GEMINI_MODEL
