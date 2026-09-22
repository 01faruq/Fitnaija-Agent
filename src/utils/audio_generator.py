"""Audio coach voice generator for FitNaija+.

Provides studio-quality Nigerian voice coaching across:
- English (Nigerian Clinical Accent)
- Yoruba (Èdè Yorùbá)
- Igbo (Asụsụ Igbo)
- Hausa (Harshen Hausa)

Supported Voice Engines:
1. Primary: YarnGPT (saheedniyi / yarngpt.ai) - Specialized Nigerian accent and indigenous language AI.
2. Fallback: Edge TTS (en-NG-EzinneNeural / en-NG-AbeoNeural) & Google TTS (Hausa native).
"""

import io
import time
import uuid
import asyncio
import requests
import concurrent.futures
from typing import Optional, Tuple, Dict, Any
from src.schemas.models import FitNaijaPlan
from src.core.config import get_yarngpt_api_key, get_gemini_api_key

# YarnGPT API endpoints
YARNGPT_TTS_URL = "https://yarngpt.ai/api/v1/tts"
YARNGPT_STATUS_URL = "https://yarngpt.ai/api/v1/status"

# YarnGPT authentic voice mappings
YARNGPT_VOICE_MAP = {
    "Yoruba": {
        "Female": "idera",
        "Male": "tayo",
    },
    "Igbo": {
        "Female": "chinenye",
        "Male": "jude",
    },
    "Hausa": {
        "Female": "zainab",
        "Male": "umar",
    },
    "English": {
        "Female": "remi",
        "Male": "osagie",
    },
}

# Edge TTS fallback voices
EDGE_VOICE_MAP = {
    "Female": "en-NG-EzinneNeural",
    "Male": "en-NG-AbeoNeural",
}


import re

def sanitize_for_tts_prosody(text: str, language: str = "English") -> str:
    """Prepare text for TTS engines by converting digits to phonetic words,
    stripping brackets, markdown, and decimal points, and normalizing prosody.
    """
    if not text:
        return ""

    clean = text.strip()

    # 1. Strip markdown symbols
    for ch in ["*", "#", "_", "~", "`", ">"]:
        clean = clean.replace(ch, "")

    # 2. Strip brackets and parentheses
    clean = re.sub(r"[\(\)\[\]\{\}]", " ", clean)

    # 3. Strip raw decimal numbers like 88.0 -> 88
    clean = re.sub(r"(\d+)\.0\b", r"\1", clean)

    # 4. Phonetic number translations for common small counts (1-12)
    lang_lower = str(language).lower()
    if "yoruba" in lang_lower:
        num_map = {
            r"\b1\b": "kan",
            r"\b2\b": "méjì",
            r"\b3\b": "mẹ́ta",
            r"\b4\b": "mẹ́rin",
            r"\b5\b": "márùn-ún",
            r"\b6\b": "mẹ́fà",
            r"\b7\b": "méje",
            r"\b8\b": "mẹ́jọ",
            r"\b9\b": "mẹ̀sán",
            r"\b10\b": "mẹ́wàá",
            r"\b12\b": "méjìlá",
        }
    elif "igbo" in lang_lower:
        num_map = {
            r"\b1\b": "otu",
            r"\b2\b": "abụọ",
            r"\b3\b": "atọ",
            r"\b4\b": "anọ",
            r"\b5\b": "ise",
            r"\b6\b": "isii",
            r"\b7\b": "asaa",
            r"\b8\b": "asatọ",
            r"\b9\b": "itoolu",
            r"\b10\b": "iri",
            r"\b12\b": "iri na abụọ",
        }
    elif "hausa" in lang_lower:
        num_map = {
            r"\b1\b": "ɗaya",
            r"\b2\b": "biyu",
            r"\b3\b": "uku",
            r"\b4\b": "huɗu",
            r"\b5\b": "biyar",
            r"\b6\b": "shida",
            r"\b7\b": "bakwai",
            r"\b8\b": "takwas",
            r"\b9\b": "tara",
            r"\b10\b": "goma",
            r"\b12\b": "sharan biyu",
        }
    else:
        num_map = {
            r"\b1\b": "one",
            r"\b2\b": "two",
            r"\b3\b": "three",
            r"\b4\b": "four",
            r"\b5\b": "five",
            r"\b6\b": "six",
            r"\b7\b": "seven",
            r"\b8\b": "eight",
            r"\b9\b": "nine",
            r"\b10\b": "ten",
        }

    for pat, rep in num_map.items():
        clean = re.sub(pat, rep, clean)

    # 5. Clean up multiple spaces and punctuation spacing
    clean = re.sub(r"\s+", " ", clean)
    clean = re.sub(r"\s+([,\.!?;:])", r"\1", clean)

    return clean.strip()


def _compile_igbo_script(plan: FitNaijaPlan) -> str:
    """Compile a natural, conversational spoken Asụsụ Igbo coach audio briefing."""
    user_name = plan.user_name or "Enyi m"
    target_cal = plan.biometrics.target_calories
    water_liters = plan.biometrics.water_target_liters
    water_sachets = getattr(plan.biometrics, "water_sachets_50cl", max(5, int(round(water_liters / 0.5))))
    motivation = plan.coach_motivation or "Ahụike bụ akụ! Nwayọọ nwayọọ ka e ji arị ugwu. Jisie ike!"

    raw_script = (
        f"Nnọọ {user_name}! Ndewo rịenne. Nke a bụ nduzi ahụike sitere na FitNaija. Ahụike bụ akụ! "
        f"Ihe mgbaru ọsọ gị bụ kalori {target_cal}, yana sachet mmiri {water_sachets} kwa ụbọchị ka ahụ gị dị jụụ. "
        f"Maka nri: Jiri iwu ọkpọ aka maka nri elo dịka amala ma ọ bụ akpụ, ejila ihe karịrị otu ọkpọ aka gị. "
        f"Wụsa ọkara efere gị ofe akwụkwọ nri na-enweghị mmanụ dịka ofe nsala ma ọ bụ okra. "
        f"Chebe ikpere na nkwonkwo gị: emela mmega ahụ na-amali elu ma ọ bụ na-akụ ala; mee mgbatị ahụ n'elu mgbidi na oche. "
        f"{motivation}"
    )
    return sanitize_for_tts_prosody(raw_script, "Igbo")


def _compile_yoruba_script(plan: FitNaijaPlan) -> str:
    """Compile a natural, conversational spoken Èdè Yorùbá coach audio briefing."""
    user_name = plan.user_name or "Ọ̀rẹ́ mi"
    water_liters = plan.biometrics.water_target_liters
    water_sachets = getattr(plan.biometrics, "water_sachets_50cl", max(5, int(round(water_liters / 0.5))))
    motivation = plan.coach_motivation or "Ìlera l'ọrọ! Ìlọsíwájú kékeré lójúmọ́ ló ń mú àṣeyọrí wá. Ẹ ku ifarada!"

    raw_script = (
        f"Káàsán o, {user_name}! Ẹ ku ifarada. Ìlera l'ọrọ o! "
        f"Mo ti wo gbogbo àkọsílẹ̀ rẹ dáadáa. "
        f"Ọ̀rọ̀ oúnjẹ rẹ kò le rárá: rántí ìlànà wa, ìwọ̀n ẹ̀ṣẹ́ ọwọ́ kan péré ni kí o fi jẹ àmàlà tàbí ẹ̀bà rẹ. "
        f"Bu Èwèdù tàbí ọbẹ̀ ilá tí kò ní epo púpọ̀ sí i. "
        f"Omi náà ṣe pàtàkì: mu omi sachet {water_sachets} lójúmọ́ kí ara rẹ lè fúyẹ́. "
        f"Ní ti eré ìmárale, a gbọ́dọ̀ dáàbò bo orúkún rẹ: má ṣe fò sókè rárá! "
        f"Ṣe àwọn ìmárale orí ògiri àti orí àga tí a kọ sílẹ̀ fún ọ. "
        f"{motivation}"
    )
    return sanitize_for_tts_prosody(raw_script, "Yoruba")


def _compile_hausa_script(plan: FitNaijaPlan) -> str:
    """Compile a natural, conversational spoken Harshen Hausa coach audio briefing."""
    user_name = plan.user_name or "Abokina"
    water_liters = plan.biometrics.water_target_liters
    water_sachets = getattr(plan.biometrics, "water_sachets_50cl", max(5, int(round(water_liters / 0.5))))
    motivation = plan.coach_motivation or "Lafiya ita ce jari! Kowane ƙaramin mataki yana da amfani. Allah Ya ba da lafiya!"

    raw_script = (
        f"Sannu, {user_name}! Lafiya ita ce jari! "
        f"Na duba dukkan bayanan jikinka sosai. "
        f"A bangaren abinci, ka kiyaye dokar dunkulen hannu ɗaya don cin tuwo, kada ya wuce girman dunkulen hannunka. "
        f"Ku ci miya mai ganye sosai kamar miyan kuka da zogale ba tare da yawan man ja ba. "
        f"Sha ledar pure water {water_sachets} a kowace rana don samun isasshen ruwa. "
        f"Kare gwiwoyi da gabobinku: kada ku yi tsalle ko gudu a kan kankare; ku yi amfani da dabarun jingina da bango da kujera. "
        f"{motivation}"
    )
    return sanitize_for_tts_prosody(raw_script, "Hausa")


def _compile_english_script(plan: FitNaijaPlan) -> str:
    """Compile a spoken Nigerian English coach audio briefing."""
    user_name = plan.user_name or "Friend"
    water_liters = plan.biometrics.water_target_liters
    water_sachets = getattr(plan.biometrics, "water_sachets_50cl", max(5, int(round(water_liters / 0.5))))
    motivation = plan.coach_motivation or "Stay consistent, celebrate every healthy step, and take it one day at a time!"

    raw_script = (
        f"Hello {user_name}! Coach here. Health is your true wealth! "
        f"Drink at least {water_sachets} pure water sachets daily to keep your hydration high. "
        f"Always follow the one-fist swallow rule for Amala, Tuwo, or Eba: never more than one clenched fist. "
        f"Fill half your plate with un-oiled greens like Ewedu or Okra, and use at most one tablespoon of oil. "
        f"Protect your knees and back: strictly zero jumping; focus on wall push-ups and chair squats. "
        f"{motivation}"
    )
    return sanitize_for_tts_prosody(raw_script, "English")


def compile_audio_script(plan: FitNaijaPlan, language: str = "English") -> str:
    """Compile a warm, culturally resonant spoken coach audio briefing in the target language.
    
    Prioritizes bespoke AI-generated spoken coach briefing if available, or falls back to
    idiomatic native scripts.
    """
    lang_lower = str(language).lower()
    custom_script = getattr(plan, "coach_motivation", None)
    # Check if coach_motivation is an extended bespoke AI-generated script
    if custom_script and len(custom_script.strip()) > 60:
        return sanitize_for_tts_prosody(custom_script.strip(), language)

    if "igbo" in lang_lower:
        return _compile_igbo_script(plan)
    elif "yoruba" in lang_lower:
        return _compile_yoruba_script(plan)
    elif "hausa" in lang_lower:
        return _compile_hausa_script(plan)
    else:
        return _compile_english_script(plan)


def get_yarngpt_voice_name(language: str = "English", voice_gender: str = "Male") -> str:
    """Determine the authentic YarnGPT voice identifier based on language and coach gender."""
    lang_key = "English"
    lang_lower = str(language).lower()
    if "yoruba" in lang_lower:
        lang_key = "Yoruba"
    elif "igbo" in lang_lower:
        lang_key = "Igbo"
    elif "hausa" in lang_lower:
        lang_key = "Hausa"

    gender_key = "Male" if "male" in str(voice_gender).lower() and "female" not in str(voice_gender).lower() else "Female"
    return YARNGPT_VOICE_MAP[lang_key][gender_key]


def synthesize_yarngpt(
    text: str,
    voice_name: str,
    api_key: str,
    timeout_seconds: int = 25
) -> bytes:
    """Synthesize speech using the YarnGPT API (https://yarngpt.ai/api/v1/tts).
    
    Args:
        text: Spoken text script.
        voice_name: YarnGPT voice (e.g., idera, chinenye, zainab, remi, tayo, jude, umar, osagie).
        api_key: User's YarnGPT Bearer token.
        timeout_seconds: Maximum polling wait time.
        
    Returns:
        MP3 audio bytes.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Idempotency-Key": str(uuid.uuid4()),
    }
    payload = {
        "text": text,
        "voice": voice_name,
    }

    resp = requests.post(YARNGPT_TTS_URL, json=payload, headers=headers, timeout=12.0)
    if resp.status_code == 401:
        raise ValueError("Invalid YarnGPT API Key. Please verify your key at yarngpt.ai.")
    resp.raise_for_status()

    data = resp.json()

    # Case 1: Audio returned directly as URL or base64
    if "audio_url" in data and data["audio_url"]:
        audio_resp = requests.get(data["audio_url"], timeout=15.0)
        audio_resp.raise_for_status()
        return audio_resp.content

    # Case 2: Async job ID provided
    job_id = data.get("job_id")
    if not job_id:
        raise RuntimeError(f"Unexpected response from YarnGPT: {data}")

    # Poll status
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        time.sleep(1.5)
        status_resp = requests.get(f"{YARNGPT_STATUS_URL}/{job_id}", headers=poll_headers, timeout=10.0)
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            if status_data.get("status") == "completed":
                audio_url = status_data.get("audio_url")
                if audio_url:
                    audio_dl = requests.get(audio_url, timeout=15.0)
                    audio_dl.raise_for_status()
                    return audio_dl.content
            elif status_data.get("status") == "failed":
                err_msg = status_data.get("error", "Speech generation failed on YarnGPT.")
                raise RuntimeError(err_msg)

    raise TimeoutError("YarnGPT audio generation timed out.")


async def _synthesize_edge_tts(text: str, voice_key: str) -> bytes:
    """Stream audio chunks from Microsoft Edge TTS into memory."""
    import edge_tts

    voice = EDGE_VOICE_MAP.get(voice_key, "en-NG-EzinneNeural")
    communicate = edge_tts.Communicate(text, voice)
    audio_stream = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream += chunk["data"]
    return audio_stream


def _synthesize_gtts(text: str, language: str = "English") -> bytes:
    """Synthesis using Google Text-to-Speech."""
    from gtts import gTTS

    lang_code = "ha" if "hausa" in language.lower() else "en"
    tld = "com.ng" if lang_code == "en" else "com"

    tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()


def synthesize_gemini_tts(
    text: str,
    api_key: str,
    voice_gender: str = "Male",
    voice_name: Optional[str] = None,
    infuse_african_tone: bool = True
) -> bytes:
    """Synthesize speech using Google Gemini Interactions TTS API (gemini-3.1-flash-tts-preview).
    
    Converts 24kHz linear PCM stream into standard playable WAV format.
    Supports warm, encouraging West African health coach cadence prompting.
    """
    import wave
    import base64

    # Gemini voices: Puck (expressive male), Fenrir (deep male), Charon (commanding male), Kore (warm female), Aoede (melodic female)
    is_male = "male" in str(voice_gender).lower() and "female" not in str(voice_gender).lower()
    selected_voice = voice_name
    if not selected_voice or selected_voice not in ("Puck", "Fenrir", "Charon", "Kore", "Aoede"):
        selected_voice = "Puck" if is_male else "Kore"

    url = "https://generativelanguage.googleapis.com/v1beta/interactions"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
        "Api-Revision": "2026-05-20"
    }
    
    # Input is the direct spoken text ready for synthesis
    speech_input = text

    payload = {
        "model": "gemini-3.1-flash-tts-preview",
        "input": speech_input,
        "response_format": {
            "type": "audio"
        },
        "generation_config": {
            "speech_config": [
                {"voice": selected_voice}
            ]
        }
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=25.0)
    resp.raise_for_status()
    data = resp.json()

    for step in data.get("steps", []):
        for part in step.get("content", []):
            if part.get("type") == "audio":
                raw_pcm = base64.b64decode(part.get("data", ""))
                channels = part.get("channels", 1)
                sample_rate = part.get("sample_rate", 24000)

                wav_io = io.BytesIO()
                with wave.open(wav_io, "wb") as wav_file:
                    wav_file.setnchannels(channels)
                    wav_file.setsampwidth(2)  # 16-bit PCM
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(raw_pcm)

                return wav_io.getvalue()

    raise RuntimeError("No audio output returned in Gemini interactions response.")


def generate_voice_note(
    text: str,
    voice_gender: str = "Male",
    language: str = "English",
    custom_api_key: Optional[str] = None,
    preferred_engine: Optional[str] = "yarngpt",
    gemini_voice_name: Optional[str] = None,
    english_fallback_text: Optional[str] = None
) -> Tuple[bytes, str]:
    """Generate audio bytes with configurable engine priority and seamless multi-tier failover.
    
    Engines:
    - 'yarngpt': Studio-grade authentic Nigerian indigenous voices (Idera, Tayo, Chinenye, Jude, Zainab, Umar, Remi, Osagie)
    - 'gemini': Google Gemini Voice AI (gemini-3.1-flash-tts-preview with African coach cadence)
    - 'edge': Microsoft Nigerian Neural Studio (en-NG-AbeoNeural / en-NG-EzinneNeural)
    
    Args:
        text: Spoken script to synthesize.
        voice_gender: 'Male' or 'Female'.
        language: Output language preference (English, Yoruba, Igbo, Hausa).
        custom_api_key: Optional YarnGPT API key passed from UI.
        preferred_engine: User's preferred engine ('yarngpt', 'gemini', 'edge').
        gemini_voice_name: Optional specific Gemini voice ('Puck', 'Fenrir', 'Charon', 'Kore', 'Aoede').
        english_fallback_text: Optional Nigerian English coaching script used when falling back to Edge TTS.
        
    Returns:
        Tuple of (audio_bytes, engine_description_string).
    """
    text = sanitize_for_tts_prosody(text, language)
    api_key = custom_api_key or get_yarngpt_api_key()
    gemini_key = get_gemini_api_key()
    lang_lower = str(language).lower()
    engine_pref = str(preferred_engine).lower().strip() if preferred_engine else "yarngpt"

    yarn_quota_hit = False

    # Helper: Try YarnGPT
    def _try_yarngpt():
        nonlocal yarn_quota_hit
        if api_key:
            try:
                voice_name = get_yarngpt_voice_name(language, voice_gender)
                audio_bytes = synthesize_yarngpt(text, voice_name, api_key)
                if audio_bytes and len(audio_bytes) > 200:
                    return audio_bytes, f"YarnGPT AI Voice ({voice_name.capitalize()})"
            except requests.exceptions.HTTPError as he:
                if getattr(he.response, "status_code", None) == 402:
                    yarn_quota_hit = True
            except Exception:
                pass
        return None

    # Helper: Try Gemini
    def _try_gemini():
        if gemini_key:
            try:
                is_male = "male" in str(voice_gender).lower() and "female" not in str(voice_gender).lower()
                chosen_v = gemini_voice_name or ("Puck" if is_male else "Kore")
                gem_bytes = synthesize_gemini_tts(text, gemini_key, voice_gender, chosen_v, infuse_african_tone=True)
                if gem_bytes and len(gem_bytes) > 500:
                    return gem_bytes, f"Google Gemini Voice (Coach {chosen_v})"
            except Exception:
                pass
        return None

    # Helper: Try Edge TTS (with intelligent language handling to avoid accent distortion)
    def _try_edge():
        voice_choice = "Male" if "male" in voice_gender.lower() and "female" not in voice_gender.lower() else "Female"
        voice_name_label = "Coach Abeo (Male)" if voice_choice == "Male" else "Coach Ezinne (Female)"
        
        # When language is an indigenous language (Yoruba, Igbo, Hausa) but the engine is Edge TTS
        # (an English neural voice), reading Yoruba text directly creates robotic distortion.
        # So we use english_fallback_text if available, or text sanitized for English prosody.
        edge_text = text
        if "english" not in lang_lower and english_fallback_text:
            edge_text = sanitize_for_tts_prosody(english_fallback_text, "English")
            
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(asyncio.run, _synthesize_edge_tts(edge_text, voice_choice))
                audio_bytes = future.result(timeout=15.0)
                if audio_bytes and len(audio_bytes) > 500:
                    label = f"Nigerian Neural Studio ({voice_name_label})"
                    if yarn_quota_hit:
                        label += " [YarnGPT Quota Depleted]"
                    return audio_bytes, label
        except Exception:
            pass
        return None

    # Helper: Try native Hausa gTTS
    def _try_hausa_gtts():
        if "hausa" in lang_lower:
            try:
                gtts_bytes = _synthesize_gtts(text, "Hausa")
                if gtts_bytes and len(gtts_bytes) > 200:
                    return gtts_bytes, "Harshen Hausa Speech Engine"
            except Exception:
                pass
        return None

    # Route based on preferred engine
    if "gemini" in engine_pref:
        res = _try_gemini()
        if res:
            return res
        # Fallback sequence: YarnGPT -> Hausa gTTS -> Edge
        res = _try_yarngpt() or _try_hausa_gtts() or _try_edge()
        if res:
            return res

    elif "edge" in engine_pref or "neural" in engine_pref:
        res = _try_edge() or _try_hausa_gtts()
        if res:
            return res
        # Fallback sequence: YarnGPT -> Gemini
        res = _try_yarngpt() or _try_gemini()
        if res:
            return res

    else:
        # Default: YarnGPT
        res = _try_yarngpt()
        if res:
            return res
        # Fallback sequence: Gemini -> Hausa gTTS -> Edge
        res = _try_gemini() or _try_hausa_gtts() or _try_edge()
        if res:
            return res

    # Final resilient fallback
    try:
        return _synthesize_gtts(text, language), "Global TTS Fallback"
    except Exception as fallback_err:
        raise RuntimeError(f"Voice recommendation generation failed: {str(fallback_err)}")


# Alias for backwards and multi-agent compatibility
generate_coach_voice = generate_voice_note


class AudioDirectorAgent:
    """Agent 3 in the Daily Coach Motivation multi-agent pipeline.
    
    Directs acoustic synthesis for daily coach voice motivation:
    1. Normalizes prosody, converts digits to authentic phonetic terms for native dialects,
       and optimizes cadence.
    2. Directs routing across YarnGPT (indigenous voices), Google Gemini Voice Studio,
       and Microsoft Nigerian Neural Edge TTS.
    3. Handles quota fallbacks seamlessly and returns audio bytes with execution trace diagnostics.
    """

    @classmethod
    def produce_coach_audio(
        cls,
        text: str,
        language: str = "English",
        voice_gender: str = "Male",
        preferred_engine: str = "auto",
        api_key: Optional[str] = None,
        gemini_key: Optional[str] = None,
        gemini_voice_name: Optional[str] = None,
        english_fallback_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synthesize daily coach audio and return full audio metadata and trace."""
        sanitized_script = sanitize_for_tts_prosody(text, language)
        start_time = time.time()

        audio_bytes, engine_label = generate_voice_note(
            text=text,
            voice_gender=voice_gender,
            language=language,
            custom_api_key=api_key,
            preferred_engine=preferred_engine,
            gemini_voice_name=gemini_voice_name,
            english_fallback_text=english_fallback_text
        )
        duration_sec = round(time.time() - start_time, 2)

        return {
            "audio_bytes": audio_bytes,
            "engine_used": engine_label,
            "sanitized_script": sanitized_script,
            "word_count": len(sanitized_script.split()),
            "language": language,
            "voice_gender": voice_gender,
            "duration_generation_sec": duration_sec,
            "status": "success",
        }

