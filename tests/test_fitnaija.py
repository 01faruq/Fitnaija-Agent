"""Unit tests for FitNaija+ modular architecture and regional Nigerian foods."""

import unittest
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
    calculate_heart_rate_zones,
    calculate_workout_met_burn,
)
from src.agents.nutrition_agent import NutritionAgent
from src.agents.fitness_agent import FitnessAgent
from src.data.nigerian_foods import (
    NIGERIAN_REGIONAL_FOODS,
    WAFCT_CITATION,
    NUTRITIONAL_BENCHMARK_CITATION,
    get_regional_foods,
    format_food_ground_truth_for_prompt,
)
from src.schemas.models import (
    BiometricsProfile,
    MealItem,
    NutritionPlan,
    ExerciseItem,
    FitnessPlan,
    FitNaijaPlan,
)
from src.utils.pdf_generator import build_pdf, sanitize_to_ascii
from src.utils.audio_generator import compile_audio_script, generate_voice_note


class TestCalculator(unittest.TestCase):
    def test_bmi_and_category(self):
        # 88kg, 168cm -> BMI = 88 / (1.68^2) = 31.179 -> 31.2
        bmi = calculate_bmi(88.0, 168.0)
        self.assertEqual(bmi, 31.2)
        self.assertEqual(get_bmi_category(bmi), "Obese (Class I)")

        # Normal weight test: 65kg, 175cm -> 21.2
        normal_bmi = calculate_bmi(65.0, 175.0)
        self.assertEqual(normal_bmi, 21.2)
        self.assertEqual(get_bmi_category(normal_bmi), "Normal Weight")

    def test_bmr_mifflin_st_jeor(self):
        # Female: 10 * 88 + 6.25 * 168 - 5 * 30 - 161 = 880 + 1050 - 150 - 161 = 1619
        female_bmr = calculate_bmr(88.0, 168.0, 30, "Female")
        self.assertEqual(female_bmr, 1619.0)

        # Male: 10 * 88 + 6.25 * 168 - 5 * 30 + 5 = 880 + 1050 - 150 + 5 = 1785
        male_bmr = calculate_bmr(88.0, 168.0, 30, "Male")
        self.assertEqual(male_bmr, 1785.0)

    def test_tdee_and_target_calories(self):
        bmr = 1619.0
        tdee_sedentary = calculate_tdee(bmr, "Beginner (Sedentary)")
        self.assertAlmostEqual(tdee_sedentary, 1619.0 * 1.2, places=1)

        # Caloric deficit for weight loss
        target_cal = calculate_target_calories(tdee_sedentary, "Weight Loss (Caloric Deficit)", "Female")
        self.assertEqual(target_cal, int(tdee_sedentary - 450))

        # Respect safe floor for women (1200 kcal)
        low_tdee = 1400.0
        target_floor = calculate_target_calories(low_tdee, "Weight Loss", "Female")
        self.assertEqual(target_floor, 1200)

    def test_water_target(self):
        # 88kg * 35ml = 3080ml -> 3.1 L
        water = calculate_water_target(88.0)
        self.assertEqual(water, 3.1)

    def test_water_sachets(self):
        # 3.1L -> 3.1 / 0.5 = 6.2 -> 6 sachets
        self.assertEqual(calculate_water_sachets(3.1), 6)
        # Floor of 5 sachets (2.5L)
        self.assertEqual(calculate_water_sachets(2.0), 5)

    def test_swallow_calorie_savings(self):
        savings = calculate_swallow_calorie_savings()
        self.assertEqual(savings["buka_calories"], 420)
        self.assertEqual(savings["fitnaija_calories"], 165)
        self.assertEqual(savings["savings_per_meal"], 255)
        self.assertEqual(savings["weekly_savings"], 255 * 7)
        self.assertGreater(savings["weekly_fat_loss_est_kg"], 0.2)

    def test_ideal_weight_range(self):
        # Height 168cm -> (1.68^2) * 18.5 = 52.2kg, (1.68^2) * 24.9 = 70.3kg
        ideal = calculate_ideal_weight_range(168.0)
        self.assertEqual(ideal["min_kg"], 52.2)
        self.assertEqual(ideal["max_kg"], 70.3)

    def test_compute_biometrics_profile(self):
        profile = compute_biometrics_profile(30, "Female", 88.0, 168.0, "Weight Loss", user_name="Faruq")
        self.assertEqual(profile["bmi"], 31.2)
        self.assertEqual(profile["bmi_category"], "Obese (Class I)")
        self.assertEqual(profile["user_name"], "Faruq")
        self.assertIn("target_calories", profile)
        self.assertIn("daily_deficit", profile)
        self.assertEqual(profile["water_sachets_50cl"], 6)
        self.assertEqual(profile["max_ideal_weight_kg"], 70.3)
        self.assertEqual(profile["weight_delta_to_normal_kg"], 17.7)


class TestNigerianFoods(unittest.TestCase):
    def test_regional_regions_exist(self):
        for region in ["Yoruba", "Hausa", "Igbo", "South-South", "General Urban"]:
            self.assertIn(region, NIGERIAN_REGIONAL_FOODS)
            staples = NIGERIAN_REGIONAL_FOODS[region]["staples"]
            self.assertGreaterEqual(len(staples), 4)

    def test_staple_fields_and_clinical_modifications(self):
        for region, data in NIGERIAN_REGIONAL_FOODS.items():
            for food in data["staples"]:
                self.assertIn("name", food)
                self.assertIn("serving_portion", food)
                self.assertGreater(food["calories_per_portion"], 0)
                self.assertIn("clinical_modifications", food)
                self.assertTrue(len(food["clinical_modifications"]) > 10)

    def test_fao_citations(self):
        self.assertIn("FAO/INFOODS", WAFCT_CITATION)
        self.assertIn("FAO/INFOODS", NUTRITIONAL_BENCHMARK_CITATION)

    def test_format_food_ground_truth(self):
        prompt_block = format_food_ground_truth_for_prompt("Yoruba")
        self.assertIn("Àmàlà", prompt_block)
        self.assertIn("Èwèdù", prompt_block)
        self.assertIn("FAO/INFOODS", prompt_block)


class TestNutritionAgent(unittest.TestCase):
    def test_cuisine_key_mapping(self):
        self.assertEqual(NutritionAgent.get_cuisine_key("Yoruba Cuisine (Amala, Ewedu)"), "Yoruba")
        self.assertEqual(NutritionAgent.get_cuisine_key("Hausa / Northern Cuisine"), "Hausa")
        self.assertEqual(NutritionAgent.get_cuisine_key("Igbo / South-East Cuisine"), "Igbo")
        self.assertEqual(NutritionAgent.get_cuisine_key("South-South Cuisine (Banga)"), "South-South")

    def test_prompt_generation_contains_swallow_rule_and_ground_truth(self):
        prompt = NutritionAgent.generate_nutrition_prompt(
            "Yoruba Cuisine (Amala, Ewedu)",
            "Open Market Staples",
            1500,
            3.0,
            "English"
        )
        self.assertIn("SWALLOW FIST RULE", prompt)
        self.assertIn("OIL RESTRICTION", prompt)
        self.assertIn("Èwèdù", prompt)
        self.assertIn("FAO/INFOODS", prompt)

    def test_default_nutrition_plan_has_citation(self):
        plan = NutritionAgent.get_default_nutrition_plan("Yoruba Cuisine", 1500, 3.0)
        self.assertEqual(plan.daily_calorie_target, 1500)
        self.assertEqual(len(plan.meals), 3)
        self.assertTrue(any("Amala" in m.dish for m in plan.meals))
        self.assertIn("FAO/INFOODS", plan.benchmark_citation)


class TestFitnessAgent(unittest.TestCase):
    def test_joint_protection_trigger(self):
        # Triggered by joint pain response
        self.assertTrue(FitnessAgent.should_enforce_joint_protection("Yes (Protect Knees/Back)", 22.0))
        # Triggered by high BMI (>= 28.0)
        self.assertTrue(FitnessAgent.should_enforce_joint_protection("No", 29.5))
        # Not triggered for low BMI with no pain
        self.assertFalse(FitnessAgent.should_enforce_joint_protection("No (Standard Bodyweight)", 23.0))

    def test_contraindications_for_joint_pain(self):
        prompt = FitnessAgent.generate_fitness_prompt("Beginner (Sedentary)", "Yes", 31.2)
        self.assertIn("STRICTLY FORBID Jumping Exercises", prompt)
        self.assertIn("STRICTLY FORBID Deep Squats", prompt)
        self.assertIn("Wall Push-Ups", prompt)
        self.assertIn("Chair Squats", prompt)

    def test_default_fitness_plan_joint_protection(self):
        plan = FitnessAgent.get_default_fitness_plan("Beginner (Sedentary)", "Yes", 31.2)
        self.assertTrue(plan.has_joint_pain)
        exercise_names = [e.name for e in plan.exercises]
        self.assertIn("Wall Push-Ups", exercise_names)
        self.assertIn("Chair Squats (Sit-to-Stands)", exercise_names)


class TestPdfGenerator(unittest.TestCase):
    def test_ascii_sanitization(self):
        tricky_text = "“Smart quotes” & ‘apostrophes’ — with bullets • and emojis 🌿🚀 and arrows →"
        cleaned = sanitize_to_ascii(tricky_text)
        self.assertNotIn("“", cleaned)
        self.assertNotIn("”", cleaned)
        self.assertNotIn("🌿", cleaned)
        self.assertNotIn("🚀", cleaned)
        self.assertIn('"Smart quotes"', cleaned)
        self.assertIn("->", cleaned)

    def test_build_pdf_success_with_user_name_and_footnote(self):
        text = "# 🎯 FitNaija Plan\n\nNutritional advice for **Amala** and *Ewedu*.\n\n- Step 1: 1 fist swallow\n- Step 2: 3L water"
        bio = {
            "user_name": "Faruq",
            "bmi": 31.2,
            "bmi_category": "Obese (Class I)",
            "target_calories": 1500,
            "bmr": 1600,
            "water_target_liters": 3.0
        }
        pdf_buf = build_pdf(text, biometrics=bio, user_name="Faruq")
        pdf_bytes = pdf_buf.getvalue()
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_igbo_pdf_generation(self):
        igbo_text = (
            "# 🎯 EBUMNUCHE BIOMETRIC NA MMIRI Ọ́ÑỤ́ÑỤ\n\n"
            "- Kalori ụbọchị niile: ≈ 1 422 kcal\n"
            "- Iwu ọkpọ aka maka nri elo (Amala, Akpu)\n"
            "- Mmiri ọñụñụ: 3.1L (~6 sachets)\n\n"
            "Ahụike bụ akụ! Nwayọọ nwayọọ ka e ji arị ugwu."
        )
        bio = {
            "user_name": "Chidimma",
            "bmi": 31.2,
            "bmi_category": "Obese (Class I)",
            "target_calories": 1422,
            "bmr": 1560,
            "water_target_liters": 3.1
        }
        pdf_buf = build_pdf(igbo_text, biometrics=bio, user_name="Chidimma")
        pdf_bytes = pdf_buf.getvalue()
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


class TestSchemas(unittest.TestCase):
    def test_fitnaija_plan_schema_json(self):
        bio_profile = compute_biometrics_profile(35, "Male", 95.0, 180.0, "Weight Loss", user_name="Faruq")
        biometrics = BiometricsProfile(**bio_profile)
        nutrition = NutritionAgent.get_default_nutrition_plan("Hausa / Northern Cuisine", 1800, 3.5)
        fitness = FitnessAgent.get_default_fitness_plan("Moderate Walker", "No", biometrics.bmi)

        plan = FitNaijaPlan(
            plan_id="FN-TEST-001",
            user_name="Faruq",
            cultural_cuisine="Hausa",
            budget_tier="Open Market Staples",
            biometrics=biometrics,
            nutrition=nutrition,
            fitness=fitness,
            coach_motivation="Ku tsaya da karfi, Faruq!",
            full_plan_markdown="# Complete Health Plan"
        )
        data = plan.model_dump()
        self.assertEqual(data["plan_id"], "FN-TEST-001")
        self.assertEqual(data["user_name"], "Faruq")
        self.assertEqual(data["biometrics"]["user_name"], "Faruq")
        self.assertEqual(data["biometrics"]["bmi_category"], "Overweight")
        self.assertIn("FAO/INFOODS", data["nutrition"]["benchmark_citation"])
        json_str = plan.model_dump_json()
        self.assertIn("FN-TEST-001", json_str)
        self.assertIn("Faruq", json_str)


class TestAudioGenerator(unittest.TestCase):
    def setUp(self):
        bio_profile = compute_biometrics_profile(32, "Female", 82.0, 165.0, "Weight Loss", user_name="Chidimma")
        biometrics = BiometricsProfile(**bio_profile)
        nutrition = NutritionAgent.get_default_nutrition_plan("Igbo / South-East Cuisine", 1450, 3.1)
        fitness = FitnessAgent.get_default_fitness_plan("Beginner (Sedentary)", "Yes", biometrics.bmi)
        self.plan = FitNaijaPlan(
            plan_id="FN-AUDIO-001",
            user_name="Chidimma",
            cultural_cuisine="Igbo",
            budget_tier="Open Market Staples",
            biometrics=biometrics,
            nutrition=nutrition,
            fitness=fitness,
            coach_motivation="Ahụike bụ akụ! Nwayọọ nwayọọ ka e ji arị ugwu.",
            full_plan_markdown="# Plan"
        )

    def test_compile_audio_script_igbo(self):
        script = compile_audio_script(self.plan, "Igbo")
        self.assertIn("Chidimma", script)
        self.assertIn("Ahụike bụ akụ", script)
        self.assertIn("Nnọọ", script)
        self.assertIn(str(self.plan.biometrics.target_calories), script)
        self.assertIn("iwu ọkpọ aka", script)
        self.assertIn("sachet mmiri", script)
        # Verify no weird committee translation
        self.assertNotIn("kọmitii ahụike", script.lower())

    def test_compile_audio_script_yoruba(self):
        script = compile_audio_script(self.plan, "Yoruba")
        self.assertIn("Ìlera l'ọrọ", script)
        # Must be ẹ̀ṣẹ́ ọwọ́ (clenched fist), NOT ẹ̀ṣọ́ (watchman)
        self.assertIn("ẹ̀ṣẹ́ ọwọ́", script)
        self.assertNotIn("ẹ̀ṣọ́ ọwọ́", script)
        self.assertIn("Èwèdù", script)
        self.assertIn("omi sachet", script)

    def test_compile_audio_script_hausa(self):
        script = compile_audio_script(self.plan, "Hausa")
        self.assertIn("Lafiya ita ce jari", script)
        self.assertIn("dunkulen hannu", script)
        self.assertIn("ledar pure water", script)
        # Must NOT tell user to drink 50kg burlap sacks of water
        self.assertNotIn("buhunan ruwa", script.lower())

    def test_compile_audio_script_english(self):
        script = compile_audio_script(self.plan, "English")
        self.assertIn("one-fist swallow rule", script)
        self.assertIn("pure water sachets", script)

    def test_yarngpt_voice_mappings(self):
        from src.utils.audio_generator import get_yarngpt_voice_name
        self.assertEqual(get_yarngpt_voice_name("Yoruba", "Female"), "idera")
        self.assertEqual(get_yarngpt_voice_name("Yoruba", "Male"), "tayo")
        self.assertEqual(get_yarngpt_voice_name("Igbo", "Female"), "chinenye")
        self.assertEqual(get_yarngpt_voice_name("Igbo", "Male"), "jude")
        self.assertEqual(get_yarngpt_voice_name("Hausa", "Female"), "zainab")
        self.assertEqual(get_yarngpt_voice_name("Hausa", "Male"), "umar")
        self.assertEqual(get_yarngpt_voice_name("English", "Female"), "remi")
        self.assertEqual(get_yarngpt_voice_name("English", "Male"), "osagie")

    def test_generate_voice_note_produces_bytes_and_engine(self):
        sample_text = "Hello Chidimma! Welcome to FitNaija. Ahuike bu aku!"
        audio, engine = generate_voice_note(sample_text, "Female", "Igbo")
        self.assertIsInstance(audio, bytes)
        self.assertGreater(len(audio), 500)
        self.assertIsInstance(engine, str)


class TestLocalizedAgentsAndGemini(unittest.TestCase):
    def test_localized_nutrition_plan_yoruba(self):
        plan = NutritionAgent.get_default_nutrition_plan("Yoruba Cuisine", 1500, 3.0, language="Yoruba")
        meal_times = [m.meal_time for m in plan.meals]
        self.assertTrue(any("Oúnjẹ Àárọ̀" in m for m in meal_times))
        self.assertTrue(any("Oúnjẹ Ọ̀sán" in m for m in meal_times))
        self.assertTrue(any("Oúnjẹ Àlẹ́" in m for m in meal_times))
        self.assertTrue(any("Ẹ̀ṣẹ́ Ọwọ́" in r for r in plan.swallow_portion_rules))
        self.assertTrue(any("Dín epo kù" in r for r in plan.oil_and_cooking_rules))

    def test_localized_nutrition_plan_igbo(self):
        plan = NutritionAgent.get_default_nutrition_plan("Igbo Cuisine", 1400, 3.0, language="Igbo")
        meal_times = [m.meal_time for m in plan.meals]
        self.assertTrue(any("Nri Ụtụtụ" in m for m in meal_times))
        self.assertTrue(any("Nri Ehihie" in m for m in meal_times))
        self.assertTrue(any("Nri Abalị" in m for m in meal_times))
        self.assertTrue(any("Ọkpọ Aka" in r for r in plan.swallow_portion_rules))
        self.assertTrue(any("Ibelata mmanụ" in r for r in plan.oil_and_cooking_rules))

    def test_localized_nutrition_plan_hausa(self):
        plan = NutritionAgent.get_default_nutrition_plan("Hausa Cuisine", 1600, 3.2, language="Hausa")
        meal_times = [m.meal_time for m in plan.meals]
        self.assertTrue(any("Karin Kumallo" in m for m in meal_times))
        self.assertTrue(any("Abincin Rana" in m for m in meal_times))
        self.assertTrue(any("Abincin Dare" in m for m in meal_times))
        self.assertTrue(any("Dunkulen Hannu" in r for r in plan.swallow_portion_rules))
        self.assertTrue(any("Rage mai" in r for r in plan.oil_and_cooking_rules))

    def test_localized_fitness_plan_languages(self):
        yo_plan = FitnessAgent.get_default_fitness_plan("Beginner", "Yes", 30.0, language="Yoruba")
        self.assertTrue(any("Titẹ Odi" in e.name for e in yo_plan.exercises))
        self.assertTrue(any("fífò rárá" in p for p in yo_plan.joint_precautions))
        
        ig_plan = FitnessAgent.get_default_fitness_plan("Beginner", "Yes", 30.0, language="Igbo")
        self.assertTrue(any("Ikwado aka na Mgbidi" in e.name for e in ig_plan.exercises))
        self.assertTrue(any("Amụla elu" in p for p in ig_plan.joint_precautions))
        
        ha_plan = FitnessAgent.get_default_fitness_plan("Beginner", "Yes", 30.0, language="Hausa")
        self.assertTrue(any("Turawa jikin Bango" in e.name for e in ha_plan.exercises))
        self.assertTrue(any("Haramcin tsalle" in p for p in ha_plan.joint_precautions))

    def test_gemini_config_and_health_engine_provider(self):
        from src.core.config import get_gemini_model, DEFAULT_GEMINI_MODEL, get_yarngpt_api_key
        from src.agents.health_engine import HealthEngine
        
        self.assertEqual(DEFAULT_GEMINI_MODEL, "gemini-3.6-flash")
        self.assertEqual(get_gemini_model(), "gemini-3.6-flash")
        
        # Test Gemini provider initialization
        engine = HealthEngine(api_key="AIzaSyTestKey1234567890", provider="gemini")
        self.assertEqual(engine.provider, "gemini")
        self.assertEqual(engine.model, "gemini-3.6-flash")
        self.assertIsNone(engine.client)  # Direct REST, not OpenAI SDK client

        # Test YarnGPT key detection
        k = get_yarngpt_api_key()
        self.assertIsNotNone(k)
        self.assertTrue(k.startswith("sk_live_"))

    def test_extract_spoken_coach_script(self):
        from src.agents.health_engine import HealthEngine
        
        sample_md = (
            "# 1. Biometrics\nTarget calories: 1400 kcal\n\n"
            "# 2. Nutrition\nEat Ewedu\n\n"
            "# 3. Fitness\nWall pushups\n\n"
            "### 4. Ọ̀rọ̀ Ìfúnilórí-iyá ti Olùkọ́\n"
            "Ẹ ku àbọ̀, Faruq! Pẹ̀lú ìwọ̀n rẹ ti 88kg, oúnjẹ àmàlà ẹ̀ṣẹ́ ọwọ́ kan péré ni kí o jẹ lónìí. Dáàbò bo orúkún rẹ!"
        )
        extracted = HealthEngine._extract_spoken_coach_script(sample_md, fallback="Default text")
        self.assertIn("Faruq", extracted)
        self.assertIn("88kg", extracted)
        self.assertIn("àmàlà", extracted)

    def test_draft_exercise_visual_prompt(self):
        from src.utils.image_generator import draft_exercise_visual_prompt
        
        prompt = draft_exercise_visual_prompt(
            exercise_name="Wall Push-Ups",
            user_name="Faruq",
            gender="Male",
            age=30,
            weight_kg=88.0,
            joint_pain=True
        )
        self.assertIn("African male", prompt)
        self.assertIn("wall push-ups", prompt)
        self.assertIn("45-degree angle", prompt)
        self.assertIn("neutral", prompt)


    def test_male_default_voices(self):
        from src.utils.audio_generator import get_yarngpt_voice_name
        
        # Test that default voice is Male across all 4 languages
        self.assertEqual(get_yarngpt_voice_name("English"), "osagie")
        self.assertEqual(get_yarngpt_voice_name("Yoruba"), "tayo")
        self.assertEqual(get_yarngpt_voice_name("Igbo"), "jude")
        self.assertEqual(get_yarngpt_voice_name("Hausa"), "umar")

        # Test explicit Female voice
        self.assertEqual(get_yarngpt_voice_name("English", "Female"), "remi")
        self.assertEqual(get_yarngpt_voice_name("Yoruba", "Female"), "idera")
        self.assertEqual(get_yarngpt_voice_name("Igbo", "Female"), "chinenye")
        self.assertEqual(get_yarngpt_voice_name("Hausa", "Female"), "zainab")

    def test_voice_note_gemini_fallback(self):
        from src.utils.audio_generator import generate_voice_note
        from src.core.config import get_gemini_api_key
        
        # When YarnGPT is invalid, if Gemini key is available, should gracefully fallback
        gem_key = get_gemini_api_key()
        if gem_key:
            audio_bytes, engine_used = generate_voice_note(
                text="Ndewo Faruq, jisie ike na ahụike gị.",
                voice_gender="Male",
                language="Igbo",
                custom_api_key="invalid_test_key"
            )
            self.assertGreater(len(audio_bytes), 500)
            self.assertTrue(
                "Google Gemini Voice" in engine_used or "Nigerian Neural" in engine_used,
                f"Expected Gemini Voice or Neural fallback, got {engine_used}"
            )

    def test_sanitize_for_tts_prosody(self):
        from src.utils.audio_generator import sanitize_for_tts_prosody
        
        # Test markdown & brackets removal
        raw_text = "**Káàsán o**, Faruq! (Ìlera l'ọrọ) #1 priority. 6 pure water sachets."
        clean = sanitize_for_tts_prosody(raw_text, "Yoruba")
        self.assertNotIn("*", clean)
        self.assertNotIn("(", clean)
        self.assertNotIn(")", clean)
        self.assertNotIn("#", clean)
        # 6 should be converted to mẹ́fà in Yoruba
        self.assertIn("mẹ́fà", clean)
        self.assertNotIn(" 6 ", clean)

        # Test Igbo numbers
        clean_igbo = sanitize_for_tts_prosody("Ṅụọ 6 sachet mmiri na 1 nri.", "Igbo")
        self.assertIn("isii", clean_igbo)
        self.assertIn("otu", clean_igbo)

        # Test Hausa numbers
        clean_hausa = sanitize_for_tts_prosody("Sha 6 ruwan leda tare da 1 tuwo.", "Hausa")
        self.assertIn("shida", clean_hausa)
        self.assertIn("ɗaya", clean_hausa)

    def test_native_coach_linguist_agent_personas(self):
        from src.agents.health_engine import NativeCoachLinguistAgent

        # Test persona metadata across languages and genders
        yo_male = NativeCoachLinguistAgent.get_coach_persona_meta("Yoruba", "Male")
        self.assertEqual(yo_male["coach_name"], "Coach Tayo")
        self.assertIn("Kọ́ọ̀chì Àgbà", yo_male["title"])

        yo_female = NativeCoachLinguistAgent.get_coach_persona_meta("Yoruba", "Female")
        self.assertEqual(yo_female["coach_name"], "Coach Idera")

        ig_male = NativeCoachLinguistAgent.get_coach_persona_meta("Igbo", "Male")
        self.assertEqual(ig_male["coach_name"], "Coach Jude")

        ha_male = NativeCoachLinguistAgent.get_coach_persona_meta("Hausa", "Male")
        self.assertEqual(ha_male["coach_name"], "Coach Umar")

        en_male = NativeCoachLinguistAgent.get_coach_persona_meta("English", "Male")
        self.assertEqual(en_male["coach_name"], "Coach Osagie")

    def test_native_coach_linguist_agent_instructions(self):
        from src.agents.health_engine import NativeCoachLinguistAgent

        instructions = NativeCoachLinguistAgent.build_system_instructions(
            language="Yoruba",
            user_name="Faruq",
            gender="Male",
            water_sachets=6,
            culture="Yoruba Cuisine",
            joint_pain="Yes"
        )
        self.assertIn("Coach Tayo", instructions)
        self.assertIn("Faruq", instructions)
        self.assertIn("Ìlera l ọrọ", instructions)
        self.assertIn("ìwọ̀n ẹ̀ṣẹ́ ọwọ́ kan", instructions)


class TestExercisePhysiologyAndEquipment(unittest.TestCase):
    """Unit tests for clinical exercise physiology, 4 equipment modalities, and periodization."""

    def test_calculate_heart_rate_zones(self):
        zones = calculate_heart_rate_zones(30)
        # Tanaka: 208 - 0.7 * 30 = 187
        self.assertEqual(zones["hr_max_tanaka"], 187.0)
        # Fox: 220 - 30 = 190
        self.assertEqual(zones["hr_max_fox"], 190)
        self.assertEqual(zones["hr_max"], 187)
        # Zone 2: 60% of 187 (112.2 -> 112) to 70% of 187 (130.9 -> 131)
        self.assertEqual(zones["zone2_low"], 112)
        self.assertEqual(zones["zone2_high"], 131)
        self.assertIn("112 - 131 bpm", zones["zone2_fatmax"])
        self.assertIn("lipid oxidation", zones["clinical_cue"])

        # Age boundaries
        with self.assertRaises(ValueError):
            calculate_heart_rate_zones(5)
        with self.assertRaises(ValueError):
            calculate_heart_rate_zones(130)

    def test_calculate_workout_met_burn(self):
        # 88kg person, 3.8 METs, 30 min -> 3.8 * 88 * 0.5 = 167 kcal
        burn = calculate_workout_met_burn(88.0, 3.8, 30)
        self.assertEqual(burn, 167)

        # 70kg person, 5.0 METs, 45 min -> 5.0 * 70 * 0.75 = 262.5 -> 262 or 263
        burn_active = calculate_workout_met_burn(70.0, 5.0, 45)
        self.assertIn(burn_active, (262, 263))

        # Edge cases
        self.assertEqual(calculate_workout_met_burn(0, 3.0, 30), 0)
        self.assertEqual(calculate_workout_met_burn(80, 0, 30), 0)

    def test_equipment_tier_home_zero(self):
        plan = FitnessAgent.get_default_fitness_plan(
            fit_level="Beginner (Sedentary)",
            joint_pain="Yes",
            bmi=31.2,
            language="English",
            equipment_tier=FitnessAgent.TIER_HOME_ZERO,
            age=30,
            weight_kg=88.0
        )
        self.assertEqual(plan.equipment_tier, FitnessAgent.TIER_HOME_ZERO)
        self.assertIn("112 - 131 bpm", plan.target_heart_rate_zone)
        self.assertGreater(plan.est_calories_burned_per_session, 100)
        self.assertTrue(any("Wall Push-Ups" in e.name for e in plan.exercises))
        self.assertTrue(any("Chair Squats" in e.name for e in plan.exercises))
        self.assertEqual(len(plan.weekly_schedule), 7)

    def test_equipment_tier_home_improvised(self):
        plan = FitnessAgent.get_default_fitness_plan(
            fit_level="Beginner (Sedentary)",
            joint_pain="Yes",
            bmi=31.2,
            language="English",
            equipment_tier=FitnessAgent.TIER_HOME_IMPROVISED,
            age=35,
            weight_kg=85.0
        )
        self.assertEqual(plan.equipment_tier, FitnessAgent.TIER_HOME_IMPROVISED)
        # Check authentic Nigerian domestic adaptations
        has_bottle = any("1.5L" in e.equipment_needed or "Bottle" in e.equipment_needed for e in plan.exercises)
        has_keg = any("Keg" in e.equipment_needed or "4L" in e.equipment_needed or "5L" in e.equipment_needed for e in plan.exercises)
        has_towel = any("Towel" in e.equipment_needed or "Tile" in e.equipment_needed for e in plan.exercises)
        self.assertTrue(has_bottle)
        self.assertTrue(has_keg)
        self.assertTrue(has_towel)

    def test_equipment_tier_gym(self):
        plan = FitnessAgent.get_default_fitness_plan(
            fit_level="Moderate Walker",
            joint_pain="Yes",
            bmi=27.0,
            language="English",
            equipment_tier=FitnessAgent.TIER_GYM,
            age=40,
            weight_kg=78.0
        )
        self.assertEqual(plan.equipment_tier, FitnessAgent.TIER_GYM)
        self.assertTrue(any("Machine" in e.equipment_needed or "Cable" in e.equipment_needed or "Bike" in e.equipment_needed for e in plan.exercises))

    def test_equipment_tier_outdoor(self):
        plan = FitnessAgent.get_default_fitness_plan(
            fit_level="Moderate Walker",
            joint_pain="Yes",
            bmi=26.0,
            language="English",
            equipment_tier=FitnessAgent.TIER_OUTDOOR,
            age=28,
            weight_kg=72.0
        )
        self.assertEqual(plan.equipment_tier, FitnessAgent.TIER_OUTDOOR)
        self.assertTrue(any("Bench" in e.equipment_needed or "Road" in e.equipment_needed or "Shoes" in e.equipment_needed for e in plan.exercises))

    def test_weekly_periodization_structure(self):
        periodization = FitnessAgent.generate_weekly_periodization(
            fit_level="Beginner",
            equipment_tier=FitnessAgent.TIER_HOME_ZERO,
            has_joint_pain=True,
            language="English"
        )
        self.assertEqual(len(periodization), 7)
        for day in periodization:
            self.assertIn("day", day)
            self.assertIn("focus", day)
            self.assertIn("duration", day)
            self.assertIn("intensity", day)
            self.assertIn("modality", day)

    def test_multilingual_equipment_adaptation(self):
        yo_plan = FitnessAgent.get_default_fitness_plan(
            fit_level="Beginner",
            joint_pain="Yes",
            bmi=30.0,
            language="Yoruba",
            equipment_tier=FitnessAgent.TIER_HOME_IMPROVISED
        )
        self.assertTrue(any("Gọgọrọ Omi" in e.name or "Kẹẹgi Omi" in e.name for e in yo_plan.exercises))
        # Yoruba days
        self.assertIn("Ọjọ́ Ajé", yo_plan.weekly_schedule[0]["day"])

        ig_plan = FitnessAgent.get_default_fitness_plan(
            fit_level="Beginner",
            joint_pain="Yes",
            bmi=30.0,
            language="Igbo",
            equipment_tier=FitnessAgent.TIER_HOME_IMPROVISED
        )
        self.assertTrue(any("Karama Mmiri" in e.name or "Keg Mmiri" in e.name for e in ig_plan.exercises))
        self.assertIn("Mọnde", ig_plan.weekly_schedule[0]["day"])

        ha_plan = FitnessAgent.get_default_fitness_plan(
            fit_level="Beginner",
            joint_pain="Yes",
            bmi=30.0,
            language="Hausa",
            equipment_tier=FitnessAgent.TIER_HOME_IMPROVISED
        )
        self.assertTrue(any("Robar Ruwa" in e.name or "Jarkar Ruwa" in e.name for e in ha_plan.exercises))
        self.assertIn("Litinin", ha_plan.weekly_schedule[0]["day"])

    def test_pdf_generation_with_exercise_physiology(self):
        bio = {
            "user_name": "Faruq",
            "bmi": 31.2,
            "bmi_category": "Obese (Class I)",
            "target_calories": 1500,
            "bmr": 1600,
            "water_target_liters": 3.0,
            "equipment_tier": "Home (Low-Cost / Domestic Improvised: Water bottles, kegs, chair)",
            "target_heart_rate_zone": "112 - 131 bpm (Zone 2 FatMax)"
        }
        meta = {
            "culture": "Yoruba",
            "equipment_tier": "Home (Low-Cost / Domestic Improvised: Water bottles, kegs, chair)",
            "target_heart_rate_zone": "112 - 131 bpm (Zone 2 FatMax)",
            "est_calories_burned_per_session": 167
        }
        pdf_buf = build_pdf("# Complete Health Plan\n\n- Safe home exercises", biometrics=bio, user_metadata=meta, user_name="Faruq")
        pdf_bytes = pdf_buf.getvalue()
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


class TestDailyCoachMotivationMultiAgent(unittest.TestCase):
    """Unit tests for the 3-agent Daily Coach Motivation pipeline."""

    def test_motivation_prompt_architect_agent(self):
        from src.agents.health_engine import MotivationPromptArchitectAgent

        # Yoruba prompt architecture
        yo_data = MotivationPromptArchitectAgent.architect_daily_motivation_prompt(
            user_name="Faruq",
            gender="Male",
            weight_kg=88.0,
            goal="Lose Fat & Weight Safely",
            culture="Yoruba Cuisine",
            target_calories=1550,
            water_sachets=6,
            equipment_tier="Home (Zero Equipment / Pure Bodyweight)",
            joint_pain="Yes",
            language="Yoruba"
        )
        self.assertEqual(yo_data["coach_name"], "Coach Tayo")
        self.assertIn("Faruq", yo_data["user_task"])
        self.assertIn("88kg", yo_data["user_task"])
        self.assertIn("1550", yo_data["user_task"])
        self.assertIn("6 sachets", yo_data["user_task"])
        self.assertIn("Yoruba", yo_data["user_task"])
        self.assertIn("Kọ́ọ̀chì Àgbà Yorùbá", yo_data["system_prompt"])

        # Hausa prompt architecture
        ha_data = MotivationPromptArchitectAgent.architect_daily_motivation_prompt(
            user_name="Amina",
            gender="Female",
            weight_kg=72.0,
            goal="Weight Loss",
            culture="Hausa/Fulani Cuisine",
            target_calories=1400,
            water_sachets=5,
            equipment_tier="Home (Low-Cost / Domestic Improvised: Water bottles, kegs, chair)",
            joint_pain="No",
            language="Hausa"
        )
        self.assertEqual(ha_data["coach_name"], "Coach Zainab")
        self.assertIn("Amina", ha_data["user_task"])
        self.assertIn("72kg", ha_data["user_task"])

    def test_native_coach_linguist_agent_defaults(self):
        from src.agents.health_engine import NativeCoachLinguistAgent

        # Yoruba default
        yo_motivation = NativeCoachLinguistAgent.get_default_daily_motivation(
            user_name="Faruq",
            language="Yoruba",
            water_sachets=6,
            equipment_tier="Home Bodyweight",
            culture="Yoruba"
        )
        self.assertIn("Faruq", yo_motivation)
        self.assertIn("Ìlera l'ọrọ", yo_motivation)
        self.assertIn("ẹ̀ṣẹ́ ọwọ́ kan", yo_motivation)
        self.assertIn("sáàkìṣì omi 6", yo_motivation)
        self.assertIn("má ṣe fò sókè", yo_motivation)

        # Igbo default
        ig_motivation = NativeCoachLinguistAgent.get_default_daily_motivation(
            user_name="Emeka",
            language="Igbo",
            water_sachets=7,
            equipment_tier="Home Workout",
            culture="Igbo"
        )
        self.assertIn("Emeka", ig_motivation)
        self.assertIn("Ahụike bụ akụ", ig_motivation)
        self.assertIn("ọkpọ aka", ig_motivation)
        self.assertIn("sachet mmiri 7", ig_motivation)

        # Hausa default
        ha_motivation = NativeCoachLinguistAgent.get_default_daily_motivation(
            user_name="Musa",
            language="Hausa",
            water_sachets=5,
            equipment_tier="Home Workout",
            culture="Hausa"
        )
        self.assertIn("Musa", ha_motivation)
        self.assertIn("Lafiya ita ce jari", ha_motivation)
        self.assertIn("dunkulen hannu ɗaya", ha_motivation)
        self.assertIn("ruwan leda 5", ha_motivation)

    def test_native_coach_linguist_agent_generate_daily_motivation(self):
        from src.agents.health_engine import NativeCoachLinguistAgent
        from unittest.mock import MagicMock

        mock_engine = MagicMock()
        mock_engine._call_llm.return_value = "Káàsán o, Faruq! Ẹ ku ifarada. Ìlera l'ọrọ o! Mo ti wo gbogbo àkọsílẹ̀ rẹ dáadáa. Ẹ jẹ́ kí a bẹ̀rẹ̀ lónìí, ara á yá!"

        architect_data = {
            "system_prompt": "You are Coach Tayo",
            "user_task": "Give motivation",
            "target_language": "Yoruba",
            "client_name": "Faruq",
            "water_sachets": 6,
            "equipment_tier": "Home Workout",
            "culture": "Yoruba"
        }
        res = NativeCoachLinguistAgent.generate_daily_motivation(mock_engine, architect_data)
        self.assertIn("Coach Tayo", architect_data["system_prompt"])
        self.assertIn("Faruq", res)
        self.assertIn("Ìlera l'ọrọ", res)

    def test_audio_director_agent_produce_coach_audio(self):
        from src.utils.audio_generator import AudioDirectorAgent
        from unittest.mock import patch

        with patch("src.utils.audio_generator.generate_voice_note") as mock_gen:
            mock_gen.return_value = (b"RIFF\x00\x00\x00\x00WAVEfmt ", "YarnGPT AI Voice (Tayo)")
            result = AudioDirectorAgent.produce_coach_audio(
                text="Ẹ ku àbọ̀ Faruq! Mu sáàkìṣì omi 6 lónìí.",
                language="Yoruba",
                voice_gender="Male",
                preferred_engine="yarngpt"
            )
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["engine_used"], "YarnGPT AI Voice (Tayo)")
            self.assertIn("mẹ́fà", result["sanitized_script"])
            self.assertGreater(result["word_count"], 4)

    def test_health_engine_deep_briefing_and_multi_agent_trace(self):
        from src.agents.health_engine import HealthEngine
        from unittest.mock import patch

        with patch.object(HealthEngine, "_call_llm") as mock_call:
            mock_call.return_value = "Káàsán o, Faruq! Ẹ ku ifarada. Ìlera l'ọrọ o! Ẹ jẹ́ kí a bẹ̀rẹ̀ lónìí pẹlu iṣẹ takuntakun ati omi mimu."
            engine = HealthEngine(api_key="mock_groq_key_12345", provider="groq")
            
            script, trace = engine.generate_daily_coach_motivation(
                user_name="Faruq",
                gender="Male",
                weight_kg=88.0,
                goal="Weight Loss",
                culture="Yoruba",
                target_calories=1500,
                water_sachets=6,
                equipment_tier="Home Workout",
                joint_pain="Yes",
                language="Yoruba"
            )
            self.assertIn("Faruq", script)
            self.assertIsNotNone(trace)
            self.assertEqual(trace["target_language"], "Yoruba")
            self.assertEqual(trace["agent_1_prompt_architect"]["name"], "MotivationPromptArchitectAgent")
            self.assertEqual(trace["agent_2_native_linguist"]["name"], "NativeCoachLinguistAgent")
            self.assertEqual(trace["agent_3_audio_director"]["name"], "AudioDirectorAgent")

    def test_fitnaija_plan_multi_agent_trace_serialization(self):
        from src.schemas.models import FitNaijaPlan, BiometricsProfile, NutritionPlan, FitnessPlan

        bio = BiometricsProfile(
            bmi=28.5,
            bmi_category="Overweight",
            bmr=1700.0,
            tdee=2300.0,
            target_calories=1800,
            daily_deficit=500,
            water_target_liters=3.0,
            water_sachets_50cl=6,
            min_healthy_weight_kg=60.0,
            max_healthy_weight_kg=75.0,
            weight_kg=88.0,
            height_cm=175.0,
            user_name="Faruq",
            gender="Male",
            age=30,
            goal="Weight Loss",
            activity_level="Beginner"
        )
        plan = FitNaijaPlan(
            plan_id="FN-TEST1234",
            user_name="Faruq",
            language="Yoruba",
            cultural_cuisine="Yoruba",
            budget_tier="Open Market",
            biometrics=bio,
            nutrition=NutritionPlan(cuisine_name="Yoruba", daily_calorie_target=1800, water_liters=3.0, meals=[]),
            fitness=FitnessPlan(fitness_level="Beginner", mobility_level="Full", has_joint_pain=True, target_weekly_frequency="3 days", exercises=[]),
            coach_motivation="Ìlera l'ọrọ o!",
            full_plan_markdown="# Plan",
            multi_agent_trace={
                "pipeline": "FitNaija+ Daily Coach Motivation Multi-Agent Engine",
                "agent_1_prompt_architect": {"status": "completed"},
                "agent_2_native_linguist": {"status": "completed"},
                "agent_3_audio_director": {"status": "ready"}
            }
        )
        plan_json = plan.model_dump_json()
        self.assertIn("multi_agent_trace", plan_json)


if __name__ == "__main__":
    unittest.main()



