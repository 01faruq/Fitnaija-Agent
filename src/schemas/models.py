"""Pydantic data models for FitNaija+ health engine.

Provides structured schemas suitable for:
- Internal engine typing
- Serialization to clean JSON for mobile app consumption (iOS/Android)
- Integration with clinical EHR/wellness records
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

DEFAULT_CITATION = "Nutritional benchmarks formulated using the FAO/INFOODS West African Food Composition Table & FMOH Guidelines."


class BiometricsProfile(BaseModel):
    """Clinical biometrics and energy expenditure calculations."""
    user_name: str = Field(default="Faruq", description="Client preferred name")
    age: int = Field(..., ge=10, le=120, description="Age in years")
    gender: str = Field(..., description="Biological sex (Male or Female)")
    weight_kg: float = Field(..., gt=20.0, le=350.0, description="Current weight in kg")
    height_cm: float = Field(..., gt=80.0, le=260.0, description="Height in cm")
    bmi: float = Field(..., description="Calculated Body Mass Index")
    bmi_category: str = Field(..., description="WHO BMI classification")
    bmr: float = Field(..., description="Basal Metabolic Rate in kcal via Mifflin-St Jeor")
    tdee: float = Field(..., description="Total Daily Energy Expenditure in kcal")
    target_calories: int = Field(..., description="Daily target caloric intake in kcal")
    daily_deficit: int = Field(default=0, description="Recommended caloric deficit in kcal/day")
    water_target_liters: float = Field(..., description="Target daily water intake in Liters")
    water_sachets_50cl: int = Field(default=6, description="Equivalent standard 50cl pure water sachets / bottles")
    max_ideal_weight_kg: Optional[float] = Field(default=None, description="Healthy weight ceiling at BMI 24.9")
    weight_delta_to_normal_kg: Optional[float] = Field(default=0.0, description="Kilograms to reach healthy BMI ceiling")
    goal: str = Field(..., description="Selected health focus / objective")
    activity_level: str = Field(..., description="Reported physical activity level")


class MealItem(BaseModel):
    """Structured clinical meal recommendation."""
    meal_time: str = Field(..., description="Meal designation (Breakfast, Lunch, Dinner, Snack)")
    dish: str = Field(..., description="Traditional dish name localized to user culture")
    portion_guide: str = Field(..., description="Fist/palm portion guideline (e.g., 1 clenched fist of Amala)")
    cooking_instructions: str = Field(..., description="Health preparation tips (oil reduction, boiling, steaming)")
    approx_calories: Optional[int] = Field(default=None, description="Estimated caloric content")


class NutritionPlan(BaseModel):
    """Culturally localized African nutrition regimen."""
    daily_calorie_target: int = Field(..., description="Caloric target for the day")
    water_liters: float = Field(..., description="Daily hydration target in liters")
    benchmark_citation: str = Field(
        default=DEFAULT_CITATION,
        description="Scientific food composition attribution"
    )
    swallow_portion_rules: List[str] = Field(
        default_factory=list,
        description="Portion rules for swallows (e.g. 1 cupped fist rule for Amala, Tuwo, Eba)"
    )
    oil_and_cooking_rules: List[str] = Field(
        default_factory=list,
        description="Guidelines for cutting palm/groundnut oil, boiling over frying, bulking with un-oiled greens"
    )
    meals: List[MealItem] = Field(default_factory=list, description="Prescribed daily meals")
    foods_to_embrace: List[str] = Field(default_factory=list, description="Nutrient-dense indigenous foods to prioritize")
    foods_to_minimize: List[str] = Field(default_factory=list, description="Calorie-dense, ultra-processed, or high-oil foods to limit")


class ExerciseItem(BaseModel):
    """Individual low-impact movement or exercise prescription."""
    name: str = Field(..., description="Exercise name (e.g. Wall Push-up, Chair Squat)")
    target_area: str = Field(..., description="Target muscle groups or functional movement pattern")
    reps_or_duration: str = Field(..., description="Recommended sets, reps, or time duration")
    instructions: str = Field(..., description="Step-by-step form execution")
    joint_safety_notes: str = Field(..., description="Why this exercise protects knees, hips, and lumbar spine")
    equipment_needed: str = Field(
        default="None / Bodyweight",
        description="Required equipment (e.g. Two 1.5L Water Bottles, Sturdy Chair, Mat, None)"
    )
    met_value: float = Field(
        default=3.5,
        description="Metabolic Equivalent of Task (METs) for energy burn calculation"
    )
    tempo_and_breathing: str = Field(
        default="3-sec descent, 1-sec pause, 1-sec press. Inhale on descent, exhale on exertion.",
        description="Clinical cadence and respiratory rhythm cue"
    )


class FitnessPlan(BaseModel):
    """Prescription for safe physical activity, exercise physiology, and joint mobility."""
    mobility_level: str = Field(..., description="User mobility / fitness category")
    has_joint_pain: bool = Field(..., description="Flag indicating knee, hip, or back pain")
    equipment_tier: str = Field(
        default="Home (Zero Equipment / Pure Bodyweight)",
        description="Workout modality (Home Zero Equipment, Home Low/Improvised, Gym, Outdoor)"
    )
    target_heart_rate_zone: str = Field(
        default="",
        description="Zone 2 FatMax range (e.g. 114 - 133 bpm) calculated via Tanaka equation"
    )
    rpe_target: str = Field(
        default="RPE 4-6 / Moderate Exertion (Talk Test: Speak in full sentences without gasping)",
        description="Borg CR10 Rate of Perceived Exertion target"
    )
    est_calories_burned_per_session: int = Field(
        default=160,
        description="Estimated energy expenditure per training session in kcal"
    )
    joint_precautions: List[str] = Field(
        default_factory=list,
        description="Safety warnings (e.g., strict contraindication against jumping or deep squats)"
    )
    exercises: List[ExerciseItem] = Field(default_factory=list, description="Prescribed safe exercises")
    daily_step_goal: int = Field(default=6000, description="Target daily steps for low-impact cardio")
    weekly_schedule: List[Dict[str, str]] = Field(
        default_factory=list,
        description="7-day structured periodized training microcycle"
    )
    biomechanical_focus: str = Field(
        default="Patellofemoral and lumbar decompression with zero ballistic joint impact.",
        description="Clinical rationale for joint safety and kinetic chain alignment"
    )


class FitNaijaPlan(BaseModel):
    """Complete integrated FitNaija+ health and nutrition plan."""
    plan_id: str = Field(..., description="Unique plan identifier")
    user_name: str = Field(default="Faruq", description="Client preferred name")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO 8601 generation timestamp"
    )
    language: str = Field(default="English", description="Target language of the plan")
    cultural_cuisine: str = Field(..., description="Selected regional African food profile")
    budget_tier: str = Field(..., description="Budget archetype (Open Market Staples vs Flexible)")
    biometrics: BiometricsProfile = Field(..., description="Calculated biometric profile")
    nutrition: NutritionPlan = Field(..., description="Localized nutritional regimen")
    fitness: FitnessPlan = Field(..., description="Safe exercise prescription")
    coach_motivation: str = Field(..., description="Culturally resonant motivational closing")
    full_plan_markdown: str = Field(..., description="Full human-readable formatted plan in Markdown")
    ai_engine_used: Optional[str] = Field(default="Groq", description="AI reasoning engine that synthesized the plan")
    multi_agent_trace: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Execution trace detailing Prompt Architect, Native Linguist, and Audio Director agents"
    )


