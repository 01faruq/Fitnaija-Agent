"""Exercise visual guide generator for FitNaija+.

Drafts tailored clinical illustration prompts based on client biometrics and joint safety,
and integrates with Google Gemini for real-time visual generation.
"""

import base64
import requests
from typing import Optional, Dict


def draft_exercise_visual_prompt(
    exercise_name: str,
    user_name: str = "Client",
    gender: str = "Female",
    age: int = 30,
    weight_kg: float = 80.0,
    joint_pain: bool = True,
    language: str = "English"
) -> str:
    """Agent that crafts a detailed, biomechanically precise prompt for exercise visuals."""
    gender_desc = "African female" if "female" in str(gender).lower() else "African male"
    
    if "wall push" in exercise_name.lower() or "odi" in exercise_name.lower() or "mgbidi" in exercise_name.lower() or "bango" in exercise_name.lower():
        movement_details = (
            "demonstrating wall push-ups at a strict 45-degree angle against a clean wall. "
            "Palms flat at shoulder-width, cervical and lumbar spine in a completely neutral line, "
            "zero wrist hyperextension, zero axial spinal compression."
        )
    elif "squat" in exercise_name.lower() or "aga" in exercise_name.lower() or "oche" in exercise_name.lower() or "kujera" in exercise_name.lower():
        movement_details = (
            "demonstrating a chair sit-to-stand squat with a sturdy wooden chair behind them. "
            "Knees tracking over toes but strictly stopping at a 90-degree angle, chest upright, "
            "core engaged, weight driving through heels, protecting the patellar tendon and knees."
        )
    else:
        movement_details = (
            "demonstrating controlled flat-ground marching in place. "
            "Knees lifting gently to hip height with upright posture, rhythmic arm swing, "
            "soft-landing on the balls of the feet with zero bouncing and zero joint shock."
        )

    return (
        f"A photorealistic clinical medical fitness infographic featuring an athletic {gender_desc} (approx {age} years old) "
        f"wearing comfortable, tasteful modern activewear in a warm, minimalist modern Nigerian home interior. "
        f"The person is {movement_details} "
        f"Includes subtle, clean graphic medical overlay arrows illustrating proper joint alignment and safe angles. "
        f"High definition, medical health guide photography style, bright natural daylight, calm and encouraging atmosphere."
    )


def draft_exercise_video_prompt(
    exercise_name: str,
    user_name: str = "Client",
    gender: str = "Male",
    age: int = 30,
    weight_kg: float = 88.0,
    joint_pain: bool = True,
    language: str = "English"
) -> Dict[str, str]:
    """Crafts high-precision cinematic video and GIF generation prompts for Google Veo and text-to-video models."""
    gender_desc = "Nigerian male" if "male" in str(gender).lower() and "female" not in str(gender).lower() else "Nigerian female"

    if "wall push" in exercise_name.lower():
        motion_desc = (
            f"Slow, continuous cinematic video of an athletic {gender_desc} (approx {age} years old, {weight_kg}kg) "
            "performing wall push-ups at a strict 45-degree angle. Hands firmly placed flat on a smooth wall at shoulder width. "
            "Smooth 3-second eccentric tempo lowering chest toward wall, 1-second pause, then smoothly pushing back. "
            "Completely neutral lumbar spine, zero neck strain, zero wrist pain. "
            "Ultra-smooth 60fps slow motion, 4k cinematic lighting, warm natural morning daylight in a contemporary Nigerian living room."
        )
    elif "squat" in exercise_name.lower():
        motion_desc = (
            f"Smooth looping video of an athletic {gender_desc} (approx {age} years old, {weight_kg}kg) "
            "performing a chair sit-to-stand squat. "
            "Starting from an upright standing stance, hinging at the hips, lowering under complete control until glutes "
            "gently touch a sturdy wooden dining chair seat. Knees track perfectly over midfoot without caving. "
            "Brief pause without collapsing, driving through heels, and rising smoothly to standing. "
            "Zero joint shock, zero bouncing. 4k cinematic photorealism, gentle camera tracking, 60fps."
        )
    else:
        motion_desc = (
            f"Smooth continuous rhythmic marching demonstration on flat flooring featuring an athletic {gender_desc}. "
            "Gently lifts knees to hip level with soft forefoot strikes. "
            "Controlled rhythmic arm swings counterbalance each step. Upright clinical posture, relaxed shoulders. "
            "Zero jumping, zero impact. Cinematic lighting, smooth stabilization, 4k slow motion."
        )

    return {
        "veo_prompt": motion_desc,
        "negative_prompt": "jumping, bouncing, rapid jerky movements, knee collapse, arched spine, cartoon, blurry, distorted limbs",
        "aspect_ratio": "16:9",
        "target_model": "Google Veo 3.1 (veo-3.1-fast-generate-preview)"
    }



def generate_gemini_exercise_image(
    prompt: str,
    api_key: str,
    timeout_seconds: int = 25
) -> Optional[bytes]:
    """Attempt generating an exercise image via Google Gemini Imagen API.
    
    Returns image bytes (JPEG/PNG) or None if quota exceeded or unavailable.
    """
    if not api_key:
        return None

    # Models to attempt: imagen-3.0-generate-002, gemini-2.5-flash-image
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}",
    ]

    # Try Imagen predict format first
    try:
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1"
            }
        }
        resp = requests.post(endpoints[0], json=payload, timeout=timeout_seconds)
        if resp.status_code == 200:
            data = resp.json()
            preds = data.get("predictions", [])
            if preds and "bytesBase64Encoded" in preds[0]:
                return base64.b64decode(preds[0]["bytesBase64Encoded"])
    except Exception:
        pass

    # Try generateContent with image model
    try:
        payload = {
            "contents": [{"parts": [{"text": f"Generate image: {prompt}"}]}]
        }
        resp = requests.post(endpoints[1], json=payload, timeout=timeout_seconds)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "inlineData" in p and "data" in p["inlineData"]:
                        return base64.b64decode(p["inlineData"]["data"])
    except Exception:
        pass

    return None
