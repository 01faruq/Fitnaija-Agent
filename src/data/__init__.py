"""Data package for FitNaija+ regional nutritional databases."""
from src.data.nigerian_foods import (
    NIGERIAN_REGIONAL_FOODS,
    WAFCT_CITATION,
    NUTRITIONAL_BENCHMARK_CITATION,
    get_regional_foods,
    format_food_ground_truth_for_prompt,
)

__all__ = [
    "NIGERIAN_REGIONAL_FOODS",
    "WAFCT_CITATION",
    "NUTRITIONAL_BENCHMARK_CITATION",
    "get_regional_foods",
    "format_food_ground_truth_for_prompt",
]
