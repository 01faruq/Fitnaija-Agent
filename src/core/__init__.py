"""Core biometrics and configuration for FitNaija+."""
from src.core.calculator import (
    calculate_bmi,
    get_bmi_category,
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_water_target,
    calculate_water_sachets,
    calculate_swallow_calorie_savings,
    calculate_ideal_weight_range,
    compute_biometrics_profile,
)
from src.core.config import get_groq_api_key, get_groq_model, sanitize_secret

__all__ = [
    "calculate_bmi",
    "get_bmi_category",
    "calculate_bmr",
    "calculate_tdee",
    "calculate_target_calories",
    "calculate_water_target",
    "calculate_water_sachets",
    "calculate_swallow_calorie_savings",
    "calculate_ideal_weight_range",
    "compute_biometrics_profile",
    "get_groq_api_key",
    "get_groq_model",
    "sanitize_secret",
]
