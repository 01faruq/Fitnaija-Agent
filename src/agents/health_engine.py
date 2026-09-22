"""Health Engine orchestrator for FitNaija+.

Coordinates biometrics, nutrition rules, joint-safe movement prescriptions,
and invokes either Groq or Google Gemini to generate culturally authentic
health plans in English, Yoruba, Igbo, and Hausa.
"""

import uuid
import datetime
import requests
from typing import Dict, Any, Optional, Tuple
from openai import OpenAI

from src.core.calculator import compute_biometrics_profile
from src.core.config import (
    GROQ_BASE_URL,
    get_groq_model,
    get_gemini_model,
    get_gemini_api_key,
    get_groq_api_key,
    sanitize_secret,
)
from src.schemas.models import (
    BiometricsProfile,
    FitNaijaPlan,
    NutritionPlan,
    FitnessPlan,
)
from src.agents.nutrition_agent import NutritionAgent
from src.agents.fitness_agent import FitnessAgent


class MotivationPromptArchitectAgent:
    """Agent 1 in the Daily Coach Motivation multi-agent pipeline.
    
    Synthesizes the client's complete biometric dataset, nutritional targets,
    cultural cuisine, joint condition, and chosen workout equipment modality into
    an expertly tailored prompt for the native cultural coach linguist model.
    """

    @classmethod
    def architect_daily_motivation_prompt(
        cls,
        user_name: str,
        gender: str,
        weight_kg: float,
        goal: str,
        culture: str,
        target_calories: int,
        water_sachets: int,
        equipment_tier: str,
        joint_pain: str,
        language: str,
    ) -> Dict[str, Any]:
        """Architects the tailored prompt and instructions for the Native Coach Linguist Agent."""
        persona = NativeCoachLinguistAgent.get_coach_persona_meta(language, gender)
        instructions = NativeCoachLinguistAgent.build_system_instructions(
            language=language,
            user_name=user_name,
            gender=gender,
            water_sachets=water_sachets,
            culture=culture,
            joint_pain=joint_pain,
            equipment_tier=equipment_tier
        )

        user_task = (
            f"{persona['coach_name']}, deliver today's inspiring, personalized daily voice motivation for {user_name} "
            f"(Current weight: {int(weight_kg)}kg, Goal: {goal}, Daily caloric target: ~{target_calories} kcal). "
            f"Explicitly encourage them on today's food discipline for {culture}, drinking {water_sachets} sachets of pure water, "
            f"and safe training with {equipment_tier} with zero knee joint strain. Speak completely in natural spoken {language}."
        )

        return {
            "coach_name": persona["coach_name"],
            "coach_title": persona["title"],
            "target_language": language,
            "system_prompt": instructions,
            "user_task": user_task,
            "client_name": user_name,
            "equipment_tier": equipment_tier,
            "water_sachets": water_sachets,
            "culture": culture,
            "target_calories": target_calories,
            "weight_kg": weight_kg,
            "goal": goal,
        }


class NativeCoachLinguistAgent:
    """Agent 2 in the Daily Coach Motivation multi-agent pipeline.
    
    Translates clinical health and nutrition parameters into authentic, colloquial,
    spoken coaching guidance tailored to each language (Yorùbá, Igbo, Hausa, Naija English).
    Eliminates robotic clinical jargon and formatted numbers so speech engines (YarnGPT,
    Gemini Voice Studio) deliver a warm, natural, and human coach audio experience.
    """

    @staticmethod
    def get_coach_persona_meta(language: str = "English", gender: str = "Male") -> Dict[str, str]:
        """Returns metadata for the active native language coach persona."""
        lang_lower = str(language).lower()
        is_male = "male" in str(gender).lower() and "female" not in str(gender).lower()

        if "yoruba" in lang_lower:
            return {
                "title": "Kọ́ọ̀chì Àgbà Yorùbá" if is_male else "Kọ́ọ̀chì Ìyá-wúrà Yorùbá",
                "coach_name": "Coach Tayo" if is_male else "Coach Idera",
                "role": "Yorùbá Cultural & Fitness Specialist",
                "tagline": "Ìlera l'ọrọ! Authentic spoken Yorùbá coaching tailored to your culture and joints.",
                "greeting": "Káàsán o",
            }
        elif "igbo" in lang_lower:
            return {
                "title": "Onye Nkuzi Ahụike Igbo",
                "coach_name": "Coach Jude" if is_male else "Coach Chinenye",
                "role": "Igbo Health & Movement Specialist",
                "tagline": "Ahụike bụ akụ! Inspiring Central Igbo wellness coaching and joint protection.",
                "greeting": "Nnọọ",
            }
        elif "hausa" in lang_lower:
            return {
                "title": "Kocin Motsa Jiki da Lafiya",
                "coach_name": "Coach Umar" if is_male else "Coach Zainab",
                "role": "Hausa Wellness & Nutritional Specialist",
                "tagline": "Lafiya ita ce jari! Respectful and practical Hausa health guidance.",
                "greeting": "Sannu",
            }
        else:
            return {
                "title": "Naija Performance Coach",
                "coach_name": "Coach Osagie" if is_male else "Coach Remi",
                "role": "Nigerian Clinical Fitness Specialist",
                "tagline": "Health is real wealth! Energetic Nigerian coaching for safe, permanent results.",
                "greeting": "Hello",
            }

    @staticmethod
    def build_system_instructions(
        language: str,
        user_name: str,
        gender: str,
        water_sachets: int,
        culture: str,
        joint_pain: str,
        equipment_tier: str = "Home (Zero Equipment / Pure Bodyweight)"
    ) -> str:
        """Build persona-specific system instructions for natural colloquial coaching."""
        lang_lower = str(language).lower()
        persona = NativeCoachLinguistAgent.get_coach_persona_meta(language, gender)

        if "yoruba" in lang_lower:
            return f"""You are {persona['title']} ({persona['coach_name']}), a caring, experienced native Nigerian health and fitness coach speaking directly to {user_name} in authentic, everyday spoken Yorùbá.

CRITICAL TONE & SPEECH RULES:
1. Speak like a real Nigerian human coach advising their brother/sister, NOT like a doctor reading an academic lab report.
2. DO NOT read raw decimals, negative signs, or English acronyms (NEVER say '88.0 kilogramu', 'sentimita', 'BMI', 'Obese Class I', or '-450 kalori').
3. Deliver genuine, caring personal advice covering:
   - Warm greeting: 'Káàsán o, {user_name}! Ẹ ku ifarada. Ìlera l ọrọ o!'
   - Health assessment: You reviewed their health profile and their path to getting fit and feeling light is clear.
   - Food guidance: Follow the 1-clenched-fist swallow rule ('ìwọ̀n ẹ̀ṣẹ́ ọwọ́ kan péré') for Amala or Eba, and load the plate with un-oiled ewédú or ilá.
   - Water: Drink {water_sachets} pure water sachets ('sáàkìṣì omi mẹ́fà' or appropriate count) daily to stay well hydrated and light.
   - Exercise & Joint safety: Zero jumping or running to protect knee joints ('kò gbọ́dọ̀ sí fífò sókè rárá'); do wall push-ups and chair squats.
   - Inspiring finish: 'Ẹ jẹ́ kí a bẹ̀rẹ̀ lónìí, ara á yá!'
4. Output format: Clean, continuous spoken Yorùbá ONLY (75 to 110 words). No markdown, no bullet points, no English words."""

        elif "igbo" in lang_lower:
            return f"""You are {persona['title']} ({persona['coach_name']}), an inspiring and warm Nigerian health and fitness coach speaking directly to {user_name} in authentic Central spoken Igbo.

CRITICAL TONE & SPEECH RULES:
1. Speak like an experienced, caring gym and health coach, NOT like a medical invoice.
2. DO NOT read raw numbers, decimals, or English medical terms (no 'BMI', no raw kilograms).
3. Deliver genuine, caring personal advice covering:
   - Warm greeting: 'Nnọọ {user_name}! Kedu ka ị mere taa. Ahụike bụ akụ na ụba!'
   - Health assessment: You reviewed their numbers and they are ready to shed weight safely.
   - Food guidance: The 1-fist swallow rule ('otu aka ọkpọ') for garri or semo, plus lots of vegetable soup with minimal cooking oil.
   - Water: Drink {water_sachets} sachets of pure water ('sachet mmiri isii') daily.
   - Exercise & Joint safety: Zero jumping to protect knees ('enweghị mwụli elu'); stick to wall push-ups and chair squats.
   - Inspiring finish: 'Nwee ndidi, anyị ga-enweta mmeri!'
4. Output format: Clean, continuous spoken Igbo ONLY (75 to 110 words). No markdown, no bullet points."""

        elif "hausa" in lang_lower:
            return f"""You are {persona['title']} ({persona['coach_name']}), a respectful, motivating Nigerian health and fitness coach speaking directly to {user_name} in authentic spoken Hausa.

CRITICAL TONE & SPEECH RULES:
1. Speak like a respectful, practical Nigerian health coach, NOT like a medical report.
2. DO NOT read raw numbers, decimals, or English abbreviations (no 'BMI', no decimals).
3. Deliver genuine, caring personal advice covering:
   - Respectful greeting: 'Sannu {user_name}, da fatan kana lafiya! Lafiya ita ce jari.'
   - Health assessment: You checked their details and their fitness journey starts now.
   - Food guidance: The 1-fist swallow rule ('dunkulen hannu ɗaya') for tuwo, and eat vegetable soup like miyan kuka or zogale with little oil.
   - Water: Drink {water_sachets} pure water sachets ('ruwan leda shida') daily.
   - Exercise & Joint safety: Zero jumping to protect knee joints ('babu tsalle'); use wall push-ups and chair squats.
   - Inspiring finish: 'Tare za mu cimma wannan buri, da yardar Allah!'
4. Output format: Clean, continuous spoken Hausa ONLY (75 to 110 words). No markdown, no bullet points."""

        else:
            return f"""You are {persona['title']} ({persona['coach_name']}), a dynamic, friendly Nigerian health and fitness coach speaking directly to {user_name} in authentic Nigerian English coach cadence.

CRITICAL TONE & SPEECH RULES:
1. Speak warmly and directly like a personal coach who has your back, energetic and authentic.
2. DO NOT read raw numbers or mechanical BMI formulas.
3. Deliver genuine personal advice covering:
   - Greeting: 'Hello {user_name}! Coach here. Health is your true wealth!'
   - Food: Strictly the 1-fist swallow rule for Amala, Tuwo, or Eba, and half your plate loaded with un-oiled greens.
   - Water: Drink {water_sachets} pure water sachets daily.
   - Exercise & Joint safety: Zero jumping to protect your knees and back; focus on wall push-ups and chair squats.
   - Inspiring finish: 'Stay consistent, celebrate every healthy step, and let's get it!'
4. Output format: Clean, continuous spoken sentences ONLY (75 to 110 words). No markdown, no bullet points."""

    @classmethod
    def generate_daily_motivation(
        cls,
        engine: Any,
        architect_data: Dict[str, Any]
    ) -> str:
        """Agent 2: Generates the authentic spoken daily coach motivation monologue."""
        system_prompt = architect_data["system_prompt"]
        user_task = architect_data["user_task"]
        language = architect_data.get("target_language", "English")

        try:
            res = engine._call_llm(instructions=system_prompt, user_prompt=user_task)
            clean_res = res.strip().replace("*", "").replace("#", "").replace('"', '')
            clean_lines = [l.strip() for l in clean_res.splitlines() if l.strip() and not l.strip().startswith(("#", "-", ">"))]
            clean_res = " ".join(clean_lines).strip()
            if len(clean_res.split()) >= 25:
                return clean_res
        except Exception:
            pass

        # Idiomatic native fallback if LLM is unreachable or quota limited
        return cls.get_default_daily_motivation(
            user_name=architect_data.get("client_name", "Friend"),
            language=language,
            water_sachets=architect_data.get("water_sachets", 6),
            equipment_tier=architect_data.get("equipment_tier", "Home Workout"),
            culture=architect_data.get("culture", "African")
        )

    @classmethod
    def get_default_daily_motivation(
        cls,
        user_name: str = "Friend",
        language: str = "English",
        water_sachets: int = 6,
        equipment_tier: str = "Home Workout",
        culture: str = "Nigerian"
    ) -> str:
        """Generate high-quality default daily motivation matching user cultural setting."""
        lang_lower = str(language).lower()

        if "yoruba" in lang_lower:
            return (
                f"Káàsán o, {user_name}! Ẹ ku ifarada. Ìlera l'ọrọ o! "
                f"Mo ti wo gbogbo àkọsílẹ̀ rẹ dáadáa. Lónìí, rántí ìlànà wa fún oúnjẹ: ìwọ̀n ẹ̀ṣẹ́ ọwọ́ kan péré ni kí o fi jẹ àmàlà tàbí ẹ̀bà rẹ, "
                f"pẹ̀lú ọbẹ̀ ewédú tàbí ilá tí kò ní epo púpọ̀. Mu sáàkìṣì omi {water_sachets} lónìí kí ara rẹ lè fúyẹ́. "
                f"Ní ti eré ìmárale, a gbọ́dọ̀ dáàbò bo orúkún rẹ: má ṣe fò sókè rárá, lo àwọn ohun èlò ilé rẹ pẹ̀lú agbara. "
                f"Ẹ jẹ́ kí a bẹ̀rẹ̀ lónìí, ara á yá!"
            )
        elif "igbo" in lang_lower:
            return (
                f"Nnọọ {user_name}! Kedu ka ị mere taa. Ahụike bụ akụ na ụba! "
                f"M lere anya na profaịlụ ahụike gị nke ọma. Maka nri taa, jiri iwu ọkpọ aka maka nri elo dịka garri ma ọ bụ semo, "
                f"wụsa ofe akwụkwọ nri na-enweghị mmanụ pụrụ iche. Ṅụọ sachet mmiri {water_sachets} taa ka ahụ gị dị jụụ. "
                f"Maka mmega ahụ taa, chebe ikpere gị: enweghị mwụli elu, jiri ngwá ọrụ ụlọ mee mgbatị ahụ n'oche na mgbidi. "
                f"Nwee ndidi, anyị ga-enweta mmeri!"
            )
        elif "hausa" in lang_lower:
            return (
                f"Sannu {user_name}, da fatan kana lafiya! Lafiya ita ce jari. "
                f"Na duba dukkan bayanan jikinka sosai. A bangaren abinci na yau, ka kiyaye dokar dunkulen hannu ɗaya don cin tuwo, "
                f"tare da miyan kuka ko zogale mai amfani ba tare da yawan man ja ba. Sha ruwan leda {water_sachets} a yau don samun isasshen ruwa. "
                f"Wajen motsa jiki, kare gwiwoyinka: babu tsalle, ka yi amfani da dabarun jingina da bango da kujera. "
                f"Tare za mu cimma wannan buri, da yardar Allah!"
            )
        else:
            return (
                f"Hello {user_name}! Coach Osagie here. Health is your true wealth! "
                f"Today is another opportunity to move closer to your goals. Stick strictly to the one-fist swallow rule, "
                f"and load half your plate with nutrient-dense, un-oiled traditional greens. "
                f"Drink your {water_sachets} pure water sachets today to maintain cellular hydration. "
                f"For today's {equipment_tier} session, protect your knees and back with zero jumping and controlled form. "
                f"Stay consistent, stay focused, and let's get it today!"
            )


class HealthEngine:
    """Core orchestrator connecting agents, clinical logic, and AI generation (Groq & Gemini)."""

    def __init__(
        self,
        api_key: str,
        provider: str = "groq",
        base_url: str = GROQ_BASE_URL,
        model: Optional[str] = None
    ):
        clean_key = sanitize_secret(api_key)
        if not clean_key:
            raise ValueError("A valid API key must be provided to initialize HealthEngine.")
        self.api_key = clean_key
        self.base_url = base_url
        self.provider = str(provider).lower().strip()

        # Auto-detect provider if user provides Gemini key directly
        if self.provider == "gemini" or clean_key.startswith("AIza") or clean_key.startswith("AQ.") or "gemini" in str(model).lower():
            self.provider = "gemini"
            self.model = sanitize_secret(model) or get_gemini_model()
            self.client = None
            self.active_engine_name = f"Google Gemini ({self.model})"
        else:
            self.provider = "groq"
            self.model = sanitize_secret(model) or get_groq_model()
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            self.active_engine_name = f"Groq ({self.model})"
        self.last_multi_agent_trace: Optional[Dict[str, Any]] = None

    def _call_gemini(self, instructions: str, user_prompt: str) -> str:
        """Call Google Gemini REST API directly with system instruction."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {
                "parts": [{"text": instructions}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096
            }
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=40.0)
        if resp.status_code in (400, 401, 403):
            err_data = resp.json() if resp.text else {}
            msg = err_data.get("error", {}).get("message", resp.text)
            raise ValueError(f"Google Gemini API error ({resp.status_code}): {msg}")
        resp.raise_for_status()

        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            text_chunks = [p.get("text", "") for p in parts if "text" in p]
            result = "".join(text_chunks).strip()
            if result:
                return result

        raise RuntimeError(f"Empty content returned by Google Gemini: {data}")

    def _call_llm(self, instructions: str, user_prompt: str) -> str:
        """Route generation to primary engine with seamless automatic failover between Groq and Google Gemini."""
        if self.provider == "gemini":
            try:
                result = self._call_gemini(instructions, user_prompt)
                self.active_engine_name = f"Google Gemini ({self.model})"
                return result
            except Exception as gem_err:
                groq_key = get_groq_api_key()
                if groq_key:
                    try:
                        groq_client = OpenAI(api_key=groq_key, base_url=GROQ_BASE_URL)
                        chat_resp = groq_client.chat.completions.create(
                            model=get_groq_model(),
                            messages=[
                                {"role": "system", "content": instructions},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.4
                        )
                        if chat_resp.choices and chat_resp.choices[0].message.content:
                            self.active_engine_name = f"Groq (Failover: {get_groq_model()})"
                            return chat_resp.choices[0].message.content.strip()
                    except Exception:
                        pass
                raise RuntimeError(f"Google Gemini generation failed: {gem_err}")

        plan_text = ""
        last_error = None

        # 1. Primary approach: client.responses.create (matches existing user workflow)
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=user_prompt
            )
            if hasattr(response, "output_text") and response.output_text:
                plan_text = response.output_text
            elif hasattr(response, "output") and response.output:
                for item in response.output:
                    if getattr(item, "type", "") == "reasoning":
                        continue
                    if hasattr(item, "content"):
                        for block in item.content:
                            if getattr(block, "type", "") == "reasoning_text":
                                continue
                            if hasattr(block, "text"):
                                plan_text += block.text if isinstance(block.text, str) else getattr(block.text, "value", str(block.text))
            if not plan_text:
                plan_text = str(response)
            if plan_text and len(plan_text.strip()) > 20:
                self.active_engine_name = f"Groq ({self.model})"
                return plan_text.strip()
        except Exception as e:
            last_error = e

        # 2. Resilient fallback: client.chat.completions.create
        try:
            chat_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4
            )
            if chat_response.choices and chat_response.choices[0].message.content:
                self.active_engine_name = f"Groq ({self.model})"
                return chat_response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e

        # 3. Automatic failover to Google Gemini
        gemini_key = get_gemini_api_key()
        if gemini_key:
            try:
                gem_model = get_gemini_model()
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{gem_model}:generateContent?key={gemini_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "system_instruction": {"parts": [{"text": instructions}]},
                    "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096}
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=40.0)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        text_chunks = [p.get("text", "") for p in parts if "text" in p]
                        result = "".join(text_chunks).strip()
                        if result:
                            self.active_engine_name = f"Google Gemini (Failover: {gem_model})"
                            return result
            except Exception:
                pass

        if plan_text:
            self.active_engine_name = f"Groq ({self.model})"
            return plan_text.strip()
        raise RuntimeError(f"Both responses and chat completions failed on Groq ({last_error}). Gemini fallback was also unavailable.")

    @staticmethod
    def _extract_spoken_coach_script(plan_markdown: str, fallback: str) -> str:
        """Extract bespoke Section 4 (Coach's Motivation / Spoken Summary) from the AI plan."""
        if not plan_markdown:
            return fallback

        lines = plan_markdown.splitlines()
        found_section_4 = False
        extracted_lines = []

        markers = ["4.", "okwu agba ume", "ọ̀rọ̀ ìfúnilórí", "jin daɗi", "coach's motivation", "audio recommendation", "spoken audio", "itọsona"]

        for line in lines:
            line_clean = line.strip().lower()
            if not found_section_4:
                if any(m in line_clean for m in markers) and ("#" in line or "4" in line):
                    found_section_4 = True
                    continue
            else:
                if line.strip().startswith("#") and any(f"{i}." in line.lower() for i in range(5, 9)):
                    break
                clean_l = line.replace("*", "").replace("#", "").replace("-", "").strip()
                if clean_l and not clean_l.startswith(">"):
                    extracted_lines.append(clean_l)

        if extracted_lines:
            combined = " ".join(extracted_lines)
            if len(combined) > 40:
                return combined

        return motivation_text or ""

    def synthesize_deep_coach_briefing(
        self,
        user_name: str,
        age: int,
        gender: str,
        weight_kg: float,
        height_cm: float,
        goal: str,
        culture: str,
        fit_level: str,
        joint_pain: str,
        output_lang: str,
        biometrics: BiometricsProfile,
        equipment_tier: str = "Home (Zero Equipment / Pure Bodyweight)",
    ) -> str:
        """Dedicated Multi-Agent Native Coach Speech Synthesizer.
        
        Orchestrates:
        1. MotivationPromptArchitectAgent: Crafts customized prompt and instructions.
        2. NativeCoachLinguistAgent: Generates genuine colloquial daily motivation in the target language.
        3. Populates self.last_multi_agent_trace with the multi-agent execution pipeline trace.
        """
        water_sachets = getattr(biometrics, "water_sachets_50cl", max(5, int(round(biometrics.water_target_liters / 0.5))))

        architect_data = MotivationPromptArchitectAgent.architect_daily_motivation_prompt(
            user_name=user_name,
            gender=gender,
            weight_kg=weight_kg,
            goal=goal,
            culture=culture,
            target_calories=biometrics.target_calories,
            water_sachets=water_sachets,
            equipment_tier=equipment_tier,
            joint_pain=joint_pain,
            language=output_lang
        )

        spoken_script = NativeCoachLinguistAgent.generate_daily_motivation(
            engine=self,
            architect_data=architect_data
        )

        # Record full multi-agent execution trace
        self.last_multi_agent_trace = {
            "pipeline": "FitNaija+ Daily Coach Motivation Multi-Agent Engine",
            "timestamp": datetime.datetime.now().isoformat(),
            "target_language": output_lang,
            "coach_persona": NativeCoachLinguistAgent.get_coach_persona_meta(output_lang, gender),
            "agent_1_prompt_architect": {
                "name": "MotivationPromptArchitectAgent",
                "role": "Biometric & Cultural Prompt Architect",
                "status": "completed",
                "user_task": architect_data["user_task"],
                "target_calories": biometrics.target_calories,
                "water_sachets": water_sachets,
                "equipment_tier": equipment_tier,
                "weight_kg": weight_kg,
                "goal": goal,
            },
            "agent_2_native_linguist": {
                "name": "NativeCoachLinguistAgent",
                "role": f"Native {output_lang} Cultural Coach",
                "coach_name": architect_data["coach_name"],
                "status": "completed",
                "generated_script": spoken_script,
                "word_count": len(spoken_script.split()),
            },
            "agent_3_audio_director": {
                "name": "AudioDirectorAgent",
                "role": "Acoustic Prosody & Audio Synthesis Director",
                "status": "ready",
                "supported_engines": ["YarnGPT (saheedniyi)", "Google Gemini Voice Studio", "Edge TTS Nigerian Neural"],
            }
        }

        return spoken_script

    def generate_daily_coach_motivation(
        self,
        user_name: str,
        gender: str,
        weight_kg: float,
        goal: str,
        culture: str,
        target_calories: int,
        water_sachets: int,
        equipment_tier: str,
        joint_pain: str,
        language: str,
    ) -> Tuple[str, Dict[str, Any]]:
        """Dedicated method for regenerating today's coach motivation on-the-fly."""
        architect_data = MotivationPromptArchitectAgent.architect_daily_motivation_prompt(
            user_name=user_name,
            gender=gender,
            weight_kg=weight_kg,
            goal=goal,
            culture=culture,
            target_calories=target_calories,
            water_sachets=water_sachets,
            equipment_tier=equipment_tier,
            joint_pain=joint_pain,
            language=language
        )

        spoken_script = NativeCoachLinguistAgent.generate_daily_motivation(
            engine=self,
            architect_data=architect_data
        )

        trace = {
            "pipeline": "FitNaija+ Daily Coach Motivation Multi-Agent Engine",
            "timestamp": datetime.datetime.now().isoformat(),
            "target_language": language,
            "coach_persona": NativeCoachLinguistAgent.get_coach_persona_meta(language, gender),
            "agent_1_prompt_architect": {
                "name": "MotivationPromptArchitectAgent",
                "role": "Biometric & Cultural Prompt Architect",
                "status": "completed",
                "user_task": architect_data["user_task"],
                "target_calories": target_calories,
                "water_sachets": water_sachets,
                "equipment_tier": equipment_tier,
                "weight_kg": weight_kg,
                "goal": goal,
            },
            "agent_2_native_linguist": {
                "name": "NativeCoachLinguistAgent",
                "role": f"Native {language} Cultural Coach",
                "coach_name": architect_data["coach_name"],
                "status": "completed",
                "generated_script": spoken_script,
                "word_count": len(spoken_script.split()),
            },
            "agent_3_audio_director": {
                "name": "AudioDirectorAgent",
                "role": "Acoustic Prosody & Audio Synthesis Director",
                "status": "ready",
                "supported_engines": ["YarnGPT (saheedniyi)", "Google Gemini Voice Studio", "Edge TTS Nigerian Neural"],
            }
        }
        self.last_multi_agent_trace = trace
        return spoken_script, trace

    def generate_plan(
        self,
        age: int,
        gender: str,
        weight_kg: float,
        height_cm: float,
        goal: str,
        culture: str,
        budget: str,
        fit_level: str,
        joint_pain: str,
        output_lang: str = "English",
        user_name: str = "Faruq",
        equipment_tier: str = "Home (Zero Equipment / Pure Bodyweight)"
    ) -> FitNaijaPlan:
        """Generate a complete, culturally localized FitNaija+ health and nutrition plan."""
        # 1. Biometric calculations
        bio_dict = compute_biometrics_profile(
            age=age,
            gender=gender,
            weight_kg=weight_kg,
            height_cm=height_cm,
            goal=goal,
            activity_level=fit_level,
            user_name=user_name
        )
        biometrics = BiometricsProfile(**bio_dict)
        water_sachets = getattr(biometrics, "water_sachets_50cl", max(5, int(round(biometrics.water_target_liters / 0.5))))

        # 2. Domain agent directives
        nutrition_directive = NutritionAgent.generate_nutrition_prompt(
            cuisine_selection=culture,
            budget_tier=budget,
            target_calories=biometrics.target_calories,
            water_target_liters=biometrics.water_target_liters,
            language=output_lang
        )

        fitness_directive = FitnessAgent.generate_fitness_prompt(
            fit_level=fit_level,
            joint_pain=joint_pain,
            bmi=biometrics.bmi,
            language=output_lang,
            equipment_tier=equipment_tier,
            age=age
        )

        # 3. Native Linguistic Directives for Yoruba, Igbo, Hausa, or English
        lang_lower = str(output_lang).lower()
        if "igbo" in lang_lower:
            lang_directive = f"""
CRITICAL LINGUISTIC DIRECTIVE FOR IGBO (ASỤSỤ IGBO):
- The entire response MUST be written 100% in authentic, idiomatic Asụsụ Igbo.
- Address the client respectfully with their name: 'Nnọọ {user_name}! Ndewo rịenne. Ahụike bụ akụ!'
- DO NOT mix English phrases. Every section heading and explanation must be in Igbo:
  * 1. 🎯 EBUMNUCHE BIOMETRIC NA MMIRI Ọ́ÑỤ́ÑỤ: Target of ~{biometrics.target_calories} kcal/day, sachet pure water {water_sachets}, and swallow fist rule: 'iwu ọkpọ aka maka nri elo (Amala, Akpụ): were naanị otu ọkpọ aka gị'.
  * 2. 🍲 USORO NRI ỌDỊNALA NKE AHỤIKE: Nri ụtụtụ, Nri ehihie, Nri abalị. Preparing soups with zero/minimal oil (Ofe Nsala, Okra na-enweghị mmanụ nkwụ), reducing bouillon/salt, using iru/ogiri/azụ kpọrọ nkụ.
  * 3. 🏃 MMEGHARỊ AHỤ DỊ NCHEKWA MGBATỊ IKPERE NA AZỤ: Amụla elu rárá (zero jumping). Mee Wall push-ups (ikwado aka na mgbidi), chair squats (nnọdụ na nkwụsị n'oche), na ije ije dị nwayọọ.
  * 4. 💬 OKWU AGBA UME NKE ONYE NDUZI: Warm coach motivation addressing {user_name} with 'Ahụike bụ akụ! Nwayọọ nwayọọ ka e ji arị ugwu. Jisie ike!'
"""
            motivation_text = f"Nnọọ {user_name}! Ahụike bụ akụ. Nwayọọ nwayọọ ka e ji arị ugwu. Jisie ike!"
        elif "yoruba" in lang_lower:
            lang_directive = f"""
CRITICAL LINGUISTIC DIRECTIVE FOR YORUBA (ÈDÈ YORÙBÁ):
- The entire response MUST be written 100% in authentic, idiomatic Èdè Yorùbá.
- Address the client warmly: 'Ẹ ku àbọ̀, {user_name}! Ìlera l'ọrọ!'
- DO NOT mix English phrases. Every section heading and explanation must be in Yoruba:
  * 1. 🎯 ÀFOJÚSÙN ÌLERA ÀTI OMI MÍMU: Target of ~{biometrics.target_calories} kcal/day, omi sachet {water_sachets} (pure water), and swallow fist rule: 'ìwọ̀n ẹ̀ṣẹ́ ọwọ́ kan péré fún oúnjẹ òkèlè bíi àmàlà tàbí ẹ̀bà'.
  * 2. 🍲 ÈTÒ OÒNJẸ ÌBÍLẸ̀ FÚN ÌLERA: Oúnjẹ àárọ̀, Oúnjẹ ọ̀sán, Oúnjẹ àlẹ́. Preparing Èwèdù and Ọbẹ̀ Ilá without heavy oil, cutting palm oil to 1 tablespoon per pot, using iru and crayfish.
  * 3. 🏃 ERÉ ÌDÁRAYÁ TÍ KÒ LÈ PA ORÚKÚN LÁRA: Kò gbọ́dọ̀ sí fífò sókè rárá (zero jumping). Wall push-ups (titẹ odi pẹlu ọwọ), chair squats (jijoko ati dide lori aga), and ririn lori ilẹ tẹju.
  * 4. 💬 Ọ̀RỌ̀ ÌFÚNILÓRÍ-IYÁ TI OLÙKỌ́: Warm coach motivation addressing {user_name} with 'Ìlera l'ọrọ! Ìlọsíwájú kékeré lójúmọ́ ló ń mú àṣeyọrí wá. Ẹ ku ifarada!'
"""
            motivation_text = f"Ẹ ku àbọ̀, {user_name}! Ìlera l'ọrọ. Ìlọsíwájú kékeré lójúmọ́ ló ń mú àṣeyọrí wá. Ẹ ku ifarada!"
        elif "hausa" in lang_lower:
            lang_directive = f"""
CRITICAL LINGUISTIC DIRECTIVE FOR HAUSA (HARSHEN HAUSA):
- The entire response MUST be written 100% in authentic, idiomatic Harshen Hausa.
- Address the client warmly: 'Sannu, {user_name}! Lafiya ita ce jari!'
- DO NOT mix English phrases. Every section heading and explanation must be in Hausa:
  * 1. 🎯 MANUFOFIN LAFIYA DA SHAN RUWA: Target of ~{biometrics.target_calories} kcal/day, ledar pure water {water_sachets} (never say buhu), and swallow fist rule: 'dokar dunkulen hannu ɗaya don tuwon shinkafa ko masara'.
  * 2. 🍲 TSARIN ABINCIN GARGAJIYA MAI GINA JIKI: Karin kumallo, Abincin rana, Abincin dare. Miyan Kuka and Miyan Zogale prepared with baobab/moringa leaves, dawadawa, dry fish, without heavy groundnut oil or palm oil.
  * 3. 🏃 MOTSA JIKI MAI LAFIYA GA GABOBI: Haramcin tsalle (zero jumping). Wall push-ups (turawa jikin bango), chair squats (zama da tashi a kujera), and tafiya a ƙasa mai laushi.
  * 4. 💬 JIN DAƊI DA ƘWARIN GWIWA DAGA KOCH: Warm coach motivation addressing {user_name} with 'Lafiya ita ce jari! Kowane ƙaramin mataki yana da amfani. Allah Ya ba da lafiya!'
"""
            motivation_text = f"Sannu, {user_name}! Lafiya ita ce jari. Kowane ƙaramin mataki yana da amfani. Allah Ya ba da lafiya!"
        else:
            lang_directive = f"""
CRITICAL LINGUISTIC DIRECTIVE FOR ENGLISH:
- Write in clear, empathetic, culturally grounded clinical English with African nutritional and anatomical terms.
"""
            motivation_text = f"Stay consistent, {user_name}! Small, intentional changes to your local meals and daily movement will transform your health. One day at a time, you've got this!"

        system_instructions = f"""
You are the clinical AI brain of FitNaija+, an African preventative health engine.
Target Language: {output_lang}.

{lang_directive}

USER CLINICAL PROFILE:
- Client Name: {user_name}
- Age: {age} | Biological Sex: {gender}
- BMI: {biometrics.bmi:.1f} ({biometrics.bmi_category})
- Basal Metabolic Rate (BMR): {biometrics.bmr:.0f} kcal
- Total Daily Energy Expenditure (TDEE): {biometrics.tdee:.0f} kcal
- Recommended Daily Caloric Target: ~{biometrics.target_calories} kcal/day (Deficit: {biometrics.daily_deficit} kcal/day)
- Daily Hydration Target: {biometrics.water_target_liters} Liters (~{water_sachets} sachets of 50cl pure water)
- Cultural Cuisine Profile: {culture}
- Budget Archetype: {budget}
- Fitness Level: {fit_level}
- Joint Pain / Discomfort: {joint_pain}

{nutrition_directive}

{fitness_directive}

OUTPUT INSTRUCTIONS:
Structure your response into four clearly demarcated clinical sections entirely in {output_lang}:
1. Biometric Target & Hydration (Target calories, sachet count, swallow fist rule).
2. Localized Nutrition Regimen (Breakfast, Lunch, Dinner, cooking rules, low-oil preparation).
3. Joint-Safe Exercise Prescription (Zero jumping, wall push-ups, chair squats, brisk flat walking).
4. Coach's Motivation & Spoken Audio Recommendation:
A dedicated, spoken 45-second coach summary written entirely in natural spoken {output_lang} addressing {user_name} personally. It MUST explicitly state their exact weight ({weight_kg}kg), goal ({goal}), daily target of ~{biometrics.target_calories} kcal, {water_sachets} sachets of pure water, the 1-fist swallow limit for {culture}, un-oiled greens, and joint-safe instructions (wall push-ups, chair squats, zero jumping).
"""

        user_prompt = f"Generate the comprehensive, personalized African preventative health plan for {user_name} completely in {output_lang}."

        # 4. Call AI Model (Groq or Gemini)
        plan_markdown = self._call_llm(
            instructions=system_instructions,
            user_prompt=user_prompt
        )

        # 5. Generate structured domain plans localized to target language
        nutrition_plan = NutritionAgent.get_default_nutrition_plan(
            cuisine_selection=culture,
            target_calories=biometrics.target_calories,
            water_liters=biometrics.water_target_liters,
            language=output_lang
        )

        fitness_plan = FitnessAgent.get_default_fitness_plan(
            fit_level=fit_level,
            joint_pain=joint_pain,
            bmi=biometrics.bmi,
            language=output_lang,
            equipment_tier=equipment_tier,
            age=age,
            weight_kg=weight_kg
        )

        # 6. Deep Coach Briefing Synthesis (dedicated pass ensuring thorough, non-generic spoken monologue)
        deep_spoken_briefing = self.synthesize_deep_coach_briefing(
            user_name=user_name,
            age=age,
            gender=gender,
            weight_kg=weight_kg,
            height_cm=height_cm,
            goal=goal,
            culture=culture,
            fit_level=fit_level,
            joint_pain=joint_pain,
            output_lang=output_lang,
            biometrics=biometrics,
            equipment_tier=equipment_tier
        )

        spoken_script = deep_spoken_briefing or self._extract_spoken_coach_script(plan_markdown, motivation_text)

        return FitNaijaPlan(
            plan_id=f"FN-{uuid.uuid4().hex[:8].upper()}",
            user_name=user_name,
            language=output_lang,
            cultural_cuisine=culture,
            budget_tier=budget,
            biometrics=biometrics,
            nutrition=nutrition_plan,
            fitness=fitness_plan,
            coach_motivation=spoken_script,
            full_plan_markdown=plan_markdown,
            ai_engine_used=getattr(self, "active_engine_name", self.model),
            multi_agent_trace=getattr(self, "last_multi_agent_trace", None)
        )
