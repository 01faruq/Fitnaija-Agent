"""Biometric and clinical calculations for FitNaija+.

Implements clinical formulas including:
- BMI (Body Mass Index) & WHO categories
- BMR (Basal Metabolic Rate) using the Mifflin-St Jeor equation
- TDEE (Total Daily Energy Expenditure) based on physical activity multipliers
- Caloric deficit target based on preventative health goals
- Tropical climate hydration targets (recommended ~35 ml/kg/day)
"""

from typing import Dict, Any, Literal


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate Body Mass Index (BMI).
    
    Formula: weight (kg) / [height (m)]^2
    """
    if height_cm <= 0:
        raise ValueError("Height must be greater than zero.")
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")
        
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 1)


def get_bmi_category(bmi: float) -> str:
    """Classify BMI based on WHO epidemiological thresholds."""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25.0:
        return "Normal Weight"
    elif 25.0 <= bmi < 30.0:
        return "Overweight"
    elif 30.0 <= bmi < 35.0:
        return "Obese (Class I)"
    elif 35.0 <= bmi < 40.0:
        return "Obese (Class II)"
    else:
        return "Severely Obese (Class III)"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.
    
    Mifflin-St Jeor is recognized as the most reliable predictive equation for BMR:
    - Men: 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) + 5
    - Women: 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) - 161
    """
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        raise ValueError("Weight, height, and age must be positive values.")
        
    base_bmr = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    
    if gender.strip().capitalize() == "Male":
        bmr = base_bmr + 5.0
    else:
        bmr = base_bmr - 161.0
        
    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: str = "Beginner (Sedentary)") -> float:
    """Calculate Total Daily Energy Expenditure (TDEE).
    
    Activity Multipliers:
    - Sedentary / Beginner: 1.2
    - Moderate Walker / Lightly Active: 1.375
    - Active / Strenuous: 1.55
    """
    activity_lower = activity_level.lower()
    if "active" in activity_lower and "moderate" not in activity_lower:
        multiplier = 1.55
    elif "moderate" in activity_lower or "walker" in activity_lower:
        multiplier = 1.375
    else:
        multiplier = 1.2
        
    return round(bmr * multiplier, 1)


def calculate_target_calories(tdee: float, goal: str, gender: str = "Female") -> int:
    """Calculate safe daily target caloric intake.
    
    For Weight Loss:
    - Creates a clinical deficit of ~450-500 kcal/day (targeting ~0.5kg/week fat loss)
    - Enforces safe minimum caloric floor (1200 kcal for women, 1500 kcal for men)
    For Maintenance or Conditioning:
    - Matches TDEE
    """
    goal_lower = goal.lower()
    min_floor = 1500 if gender.strip().capitalize() == "Male" else 1200
    
    if "loss" in goal_lower or "deficit" in goal_lower:
        target = int(tdee - 450)
        return max(target, min_floor)
    elif "conditioning" in goal_lower:
        return int(tdee)
    else:
        return int(tdee)


def calculate_water_target(weight_kg: float) -> float:
    """Calculate baseline daily water intake in Liters.
    
    In tropical African climates, standard recommendation is ~35ml per kg of bodyweight.
    Minimum baseline is 2.5L, capped reasonably at 4.5L for safe kidney clearance.
    """
    water_liters = (weight_kg * 35.0) / 1000.0
    return round(max(2.5, min(water_liters, 4.5)), 1)


def calculate_water_sachets(water_liters: float) -> int:
    """Convert daily water target into standard Nigerian 50cl sachets / 50cl bottles."""
    return max(5, int(round(water_liters / 0.5)))


def calculate_swallow_calorie_savings() -> Dict[str, Any]:
    """Calculate caloric difference between standard Nigerian bukateria portions and the 1-Fist Rule."""
    buka_portion_g = 350
    buka_calories = 420
    fitnaija_portion_g = 150
    fitnaija_calories = 165
    savings_per_meal = buka_calories - fitnaija_calories
    weekly_savings = savings_per_meal * 7  # 1 swallow meal per day

    return {
        "buka_portion_g": buka_portion_g,
        "buka_calories": buka_calories,
        "fitnaija_portion_g": fitnaija_portion_g,
        "fitnaija_calories": fitnaija_calories,
        "savings_per_meal": savings_per_meal,
        "weekly_savings": weekly_savings,
        "weekly_fat_loss_est_kg": round(weekly_savings / 7700.0, 2),
    }


def calculate_ideal_weight_range(height_cm: float) -> Dict[str, float]:
    """Calculate healthy weight threshold (BMI 18.5 - 24.9) for a given height."""
    height_m = height_cm / 100.0
    min_ideal = round(18.5 * (height_m ** 2), 1)
    max_ideal = round(24.9 * (height_m ** 2), 1)
    return {"min_kg": min_ideal, "max_kg": max_ideal}


def compute_biometrics_profile(
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    goal: str,
    activity_level: str = "Beginner (Sedentary)",
    user_name: str = "Faruq"
) -> Dict[str, Any]:
    """Compute complete biometric profile dictionary."""
    bmi = calculate_bmi(weight_kg, height_cm)
    bmi_category = get_bmi_category(bmi)
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_cal = calculate_target_calories(tdee, goal, gender)
    water_target = calculate_water_target(weight_kg)
    water_sachets = calculate_water_sachets(water_target)
    ideal_range = calculate_ideal_weight_range(height_cm)
    
    # Calculate recommended safe caloric deficit
    deficit = int(tdee - target_cal) if target_cal < tdee else 0

    # Weight delta to achieve normal BMI threshold (< 25.0)
    weight_delta = round(weight_kg - ideal_range["max_kg"], 1) if weight_kg > ideal_range["max_kg"] else 0.0

    return {
        "user_name": user_name,
        "age": age,
        "gender": gender,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_cal,
        "daily_deficit": deficit,
        "water_target_liters": water_target,
        "water_sachets_50cl": water_sachets,
        "max_ideal_weight_kg": ideal_range["max_kg"],
        "weight_delta_to_normal_kg": weight_delta,
        "goal": goal,
        "activity_level": activity_level,
    }


def calculate_heart_rate_zones(age: int) -> Dict[str, Any]:
    """Calculate clinical cardiorespiratory training zones based on Exercise Physiology formulas.
    
    Formulas:
    - Tanaka Equation (ACSM gold-standard for adults): HRmax = 208 - (0.7 * age)
    - Fox Formula: HRmax = 220 - age
    - Zone 1 (Active Recovery / Warmup): 50% - 60% HRmax
    - Zone 2 (FatMax / Mitochondrial Biogenesis): 60% - 70% HRmax (Optimal fat oxidation without elevated cortisol)
    - Zone 3 (Aerobic Endurance): 70% - 80% HRmax
    - Zone 4 (Anaerobic / Lactate Threshold): 80% - 90% HRmax
    """
    if age < 10 or age > 120:
        raise ValueError("Age must be between 10 and 120 years.")
        
    hr_max_tanaka = round(208.0 - (0.7 * float(age)), 1)
    hr_max_fox = 220 - age
    hr_max = int(round(hr_max_tanaka))
    
    z1_low = int(round(hr_max * 0.50))
    z1_high = int(round(hr_max * 0.60))
    
    z2_low = int(round(hr_max * 0.60))
    z2_high = int(round(hr_max * 0.70))
    
    z3_low = int(round(hr_max * 0.70))
    z3_high = int(round(hr_max * 0.80))
    
    z4_low = int(round(hr_max * 0.80))
    z4_high = int(round(hr_max * 0.90))
    
    return {
        "age": age,
        "hr_max_tanaka": hr_max_tanaka,
        "hr_max_fox": hr_max_fox,
        "hr_max": hr_max,
        "zone1_recovery": f"{z1_low} - {z1_high} bpm",
        "zone2_fatmax": f"{z2_low} - {z2_high} bpm",
        "zone3_aerobic": f"{z3_low} - {z3_high} bpm",
        "zone4_threshold": f"{z4_low} - {z4_high} bpm",
        "zone2_low": z2_low,
        "zone2_high": z2_high,
        "clinical_cue": f"Maintain heart rate between {z2_low} and {z2_high} bpm during training for maximal lipid oxidation and zero joint overload."
    }


def calculate_workout_met_burn(weight_kg: float, met: float = 3.8, duration_minutes: int = 30) -> int:
    """Calculate estimated caloric expenditure using the Compendium of Physical Activities MET formula.
    
    Formula: Energy Expenditure (kcal) = MET * weight(kg) * (duration_minutes / 60)
    """
    if weight_kg <= 0 or met <= 0 or duration_minutes <= 0:
        return 0
        
    burn = met * weight_kg * (float(duration_minutes) / 60.0)
    return int(round(burn))



