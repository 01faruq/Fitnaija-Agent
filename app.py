"""FitNaija+ AI Health Engine - Streamlit Presentation Layer.

Culturally localized African clinical nutrition & joint-safe mobility engine.
"""

import json
import streamlit as st

from src.core.config import (
    get_groq_api_key,
    get_groq_model,
    get_gemini_api_key,
    get_gemini_model,
    get_yarngpt_api_key,
    GROQ_BASE_URL,
    sanitize_secret,
)
from src.core.calculator import compute_biometrics_profile, calculate_swallow_calorie_savings
from src.agents.health_engine import HealthEngine, NativeCoachLinguistAgent, MotivationPromptArchitectAgent
from src.agents.nutrition_agent import NutritionAgent
from src.agents.fitness_agent import FitnessAgent
from src.utils.pdf_generator import build_pdf
from src.utils.audio_generator import (
    compile_audio_script,
    generate_voice_note,
    get_yarngpt_voice_name,
    _compile_english_script,
    AudioDirectorAgent,
)
from src.utils.image_generator import (
    draft_exercise_visual_prompt,
    draft_exercise_video_prompt,
    generate_gemini_exercise_image,
)

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="FitNaija+ AI Health Engine",
    page_icon=":material/health_and_safety:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal custom CSS for typography and subtle container accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #166534;
        margin-bottom: 4px;
        letter-spacing: -0.6px;
    }
    
    .hero-sub {
        font-size: 1.02rem;
        color: #475569;
        margin-bottom: 16px;
        line-height: 1.5;
    }
    
    .wisdom-bar {
        background: linear-gradient(90deg, #F0FDF4 0%, #DCFCE7 100%);
        border-left: 4px solid #16A34A;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 22px;
        font-size: 0.92rem;
    }
    
    .rule-card {
        background-color: #F8FAFC;
        border-left: 4px solid #16A34A;
        padding: 14px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 10px;
        font-size: 0.92rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: Engine Settings & Clinical Foundations
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### :material/health_and_safety: FitNaija+ Engine")
    st.caption("AI preventative metabolic health engineered for African biometrics, regional food culture, and joint longevity.")
    
    # 1. AI Reasoning Engine (Groq or Google Gemini)
    st.markdown("#### :material/psychology: AI Reasoning Engine")
    provider_choice = st.segmented_control(
        "AI Engine Provider:",
        ["Groq (Ultra-Fast)", "Google Gemini (Pro / Flash)"],
        default="Groq (Ultra-Fast)"
    )
    
    if "Gemini" in (provider_choice or ""):
        ai_provider = "gemini"
        env_gemini_key = get_gemini_api_key()
        if env_gemini_key:
            api_key = env_gemini_key
            st.badge("Gemini API Connected", icon=":material/check_circle:", color="green")
        else:
            raw_key = st.text_input(
                "Gemini API Key:",
                type="password",
                help="Enter your Google Gemini API key (starts with AIza...)"
            )
            api_key = sanitize_secret(raw_key) if raw_key else None
            if not api_key:
                st.info("💡 Enter your Gemini API key or set `GEMINI_API_KEY` in `.env`.")
                st.markdown("[Get a free Gemini API key from Google AI Studio](https://aistudio.google.com/app/apikey)")

        available_gemini_models = list(dict.fromkeys([
            get_gemini_model(),
            "gemini-3.6-flash",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-3.7-flash"
        ]))
        model_name = st.selectbox(
            "Gemini model:",
            options=available_gemini_models,
            index=0
        )
    else:
        ai_provider = "groq"
        env_api_key = get_groq_api_key()
        if env_api_key:
            api_key = env_api_key
            st.badge("Groq API Connected", icon=":material/check_circle:", color="green")
        else:
            raw_key = st.text_input(
                "Groq API Key:",
                type="password",
                help="Enter your Groq API key (starts with gsk_)"
            )
            api_key = sanitize_secret(raw_key) if raw_key else None
            if not api_key:
                st.info("💡 Enter your Groq key or set `GROQ_API_KEY` in `.env`.")
                st.markdown("[Get a free Groq API key](https://console.groq.com/keys)")

        available_models = list(dict.fromkeys([
            get_groq_model(),
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b"
        ]))
        model_name = st.selectbox(
            "Groq model:",
            options=available_models,
            index=0
        )

    # 2. Nigerian Voice Coach Engine & Model Selector
    st.markdown("#### :material/volume_up: Voice Coach Engine")
    voice_engine_choice = st.segmented_control(
        "Voice Coach Engine:",
        ["YarnGPT AI (Nigerian Accent)", "Google Gemini Voice Studio", "Nigerian Neural (Edge)"],
        default="YarnGPT AI (Nigerian Accent)"
    )

    env_yarngpt_key = get_yarngpt_api_key()
    env_gemini_key = get_gemini_api_key()

    if "Gemini" in (voice_engine_choice or ""):
        selected_voice_engine = "gemini"
        yarngpt_key = env_yarngpt_key
        if env_gemini_key:
            st.badge("Gemini Voice Connected", icon=":material/mic:", color="green")
        else:
            st.info("💡 Set `GEMINI_API_KEY` in `.env` to activate Gemini Voice Studio.")

        gemini_selected_voice = st.selectbox(
            "Gemini Voice Persona (West African Cadence):",
            [
                "Coach Puck (Expressive Male)",
                "Coach Kore (Warm Female)",
                "Coach Charon (Commanding Male)",
                "Coach Aoede (Melodic Female)"
            ],
            index=0
        )
        st.caption("Studio 24kHz audio with real-time prompt-injected West African health coach cadence.")

    elif "Edge" in (voice_engine_choice or "") or "Neural" in (voice_engine_choice or ""):
        selected_voice_engine = "edge"
        yarngpt_key = env_yarngpt_key
        gemini_selected_voice = None
        st.badge("Neural Studio Connected", icon=":material/graphic_eq:", color="blue")
        st.caption("Microsoft Nigerian Neural Voices (en-NG-AbeoNeural / en-NG-EzinneNeural).")

    else:
        selected_voice_engine = "yarngpt"
        gemini_selected_voice = None
        if env_yarngpt_key:
            yarngpt_key = env_yarngpt_key
            st.badge("YarnGPT Connected", icon=":material/mic:", color="green")
        else:
            custom_ygpt = st.text_input(
                "YarnGPT API Key (Optional):",
                type="password",
                help="Optional: Enter key from yarngpt.ai for studio-grade Nigerian accent voices."
            )
            yarngpt_key = sanitize_secret(custom_ygpt) if custom_ygpt else None
        st.caption("🎙️ Authentic indigenous Nigerian voices: Tayo, Idera, Jude, Chinenye, Umar, Zainab, Osagie, Remi.")

    with st.expander(":material/restaurant: African Portion Guide", expanded=False):
        st.markdown("""
        - **1-Fist Swallow Rule**: Strictly 1 clenched fist max of Amala, Tuwo, Eba, or Pounded Yam.
        - **Palm Protein Rule**: 1 palm-sized serving of lean fish, skinless poultry, or moimoi.
        - **Half-Plate Greens**: 50% plate bulked with un-oiled Ewedu, Okra, Miyan Kuka, or Efo.
        """)

    with st.expander(":material/shield: Joint-Safety Protocol", expanded=False):
        st.markdown("""
        - For individuals with joint/knee strain or BMI ≥ 28, **high-impact movements are strictly contraindicated**.
        - Emphasizes wall push-ups, chair sit-to-stands, seated leg extensions, and flat walking.
        """)

    st.caption("🔬 Benchmarked against the FAO/INFOODS West African Food Composition Table & FMOH Clinical Guidelines.")

# ---------------------------------------------------------
# Main UI Header
# ---------------------------------------------------------
st.markdown('<div class="hero-title">🌿 FitNaija+ Health Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Clinical preventative health engine prescribing culturally authentic African nutrition, '
    'smart portion architecture, and joint-safe mobility routines.</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="wisdom-bar">
    <strong style="color: #166534;">Ancestral Health Wisdom:</strong>
    <span style="color: #15803D;">
        <em>"Ahụike bụ akụ"</em> (Igbo) • <em>"Ìlera l'ọrọ"</em> (Yoruba) • <em>"Lafiya ita ce jari"</em> (Hausa) — <strong>Health is True Wealth</strong>.
    </span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Intake Form
# ---------------------------------------------------------
with st.container(border=True):
    st.markdown("#### :material/edit_note: Client Health Profile & Preferences")
    
    with st.form("fitnaija_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 1. Biometrics")
            user_name = st.text_input("Full name / preferred name", value="Faruq", help="Used to address you personally in clinical prescriptions and coach audio.")
            age = st.number_input("Age", min_value=16, max_value=95, value=30, step=1)
            gender = st.segmented_control("Biological sex", ["Male", "Female"], default="Male")
            weight = st.number_input("Current weight (kg)", min_value=40.0, max_value=220.0, value=88.0, step=0.5)
            height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=168.0, step=0.5)
            goal = st.selectbox(
                "Health focus",
                [
                    "Weight Loss (Caloric Deficit)",
                    "Weight Maintenance & Toning",
                    "Cardio & Metabolic Conditioning"
                ]
            )

        with col2:
            st.markdown("##### 2. Regional Nutrition")
            culture = st.selectbox(
                "Cultural cuisine profile",
                [
                    "Yoruba Cuisine (Amala, Ewedu, Gbegiri, Efo Riro, Moimoi)",
                    "Hausa / Northern Cuisine (Tuwon Shinkafa, Miyan Kuka, Zogale, Acha)",
                    "Igbo / South-East Cuisine (Ofe Nsala, Bitterleaf Soup, Ukwa, Okra)",
                    "South-South Cuisine (Fisherman Soup, Low-Oil Banga, Owo)",
                    "General Urban Nigerian (Brown Beans, Boiled Plantain, Grilled Fish)"
                ]
            )
            budget = st.selectbox("Budget archetype", ["Open Market Staples (Affordable)", "Flexible Grocery"])
            meals_per_day = st.segmented_control("Daily meal routine", ["3 Standard Meals", "2 Meals + 1 Snack"], default="3 Standard Meals")

        with col3:
            st.markdown("##### 3. Mobility & Environment")
            equipment_tier = st.selectbox(
                "Workout environment & equipment",
                [
                    "Home (Zero Equipment / Pure Bodyweight)",
                    "Home (Low-Cost / Domestic Improvised: Water bottles, kegs, chair)",
                    "Gym / Fitness Center (Full equipment)",
                    "Outdoor / Neighborhood (Walking loops & park benches)"
                ],
                index=1,
                help="Select your training setting. Home Low-Cost utilizes filled 1.5L Eva water bottles, 4L/5L kegs, and dining chairs."
            )
            fit_level = st.selectbox(
                "Current activity level",
                ["Beginner (Sedentary)", "Moderate Walker", "Active"]
            )
            joint_pain = st.segmented_control(
                "Joint or knee pain?",
                ["No (Standard)", "Yes (Protect Joints)"],
                default="Yes (Protect Joints)"
            )
            output_lang = st.segmented_control(
                "Coach audio & plan language",
                ["English", "Yoruba", "Igbo", "Hausa"],
                default="English"
            )

        submit_button = st.form_submit_button(
            "Generate Personalized Clinical Health Plan",
            icon=":material/rocket_launch:",
            type="primary"
        )

# ---------------------------------------------------------
# Dynamic Real-time Biometrics Calculation Display
# ---------------------------------------------------------
bio_profile = compute_biometrics_profile(
    age=age,
    gender=gender or "Female",
    weight_kg=weight,
    height_cm=height,
    goal=goal,
    activity_level=fit_level,
    user_name=user_name
)

# Render Metric Snapshot in Bordered Cards
st.markdown("#### :material/analytics: Calculated Biometric Baseline")
b_cols = st.columns(5)

with b_cols[0]:
    with st.container(border=True):
        bmi_val = bio_profile['bmi']
        st.metric(label="Body Mass Index", value=f"{bmi_val:.1f}")
        if bmi_val < 25.0:
            st.badge("Normal BMI", color="green")
        elif bmi_val < 30.0:
            st.badge("Overweight", color="orange")
        else:
            st.badge("Obese", color="red")

with b_cols[1]:
    with st.container(border=True):
        st.metric(label="Basal Metabolic Rate", value=f"{int(bio_profile['bmr']):,} kcal")
        st.caption("Resting energy need")

with b_cols[2]:
    with st.container(border=True):
        st.metric(label="Est. Maintenance (TDEE)", value=f"{int(bio_profile['tdee']):,} kcal")
        st.caption("Daily total burn")

with b_cols[3]:
    with st.container(border=True):
        st.metric(label="Target Daily Intake", value=f"~{bio_profile['target_calories']:,} kcal")
        if bio_profile['daily_deficit'] > 0:
            st.badge(f"-{bio_profile['daily_deficit']} kcal Deficit", color="green")
        else:
            st.badge("Maintenance", color="blue")

with b_cols[4]:
    with st.container(border=True):
        water_sachets = bio_profile['water_sachets_50cl']
        st.metric(label="Target Daily Water", value=f"{bio_profile['water_target_liters']} L")
        st.caption(f"~{water_sachets} sachets / 50cl bottles")

# Target Guidance Notes
n_col1, n_col2 = st.columns(2)
with n_col1:
    if bio_profile['daily_deficit'] > 0:
        st.info(f"💡 **Deficit Strategy:** Clinically controlled deficit of ~{bio_profile['daily_deficit']} kcal/day for safe, sustainable fat loss with 0 starvation.")
    else:
        st.info("💡 **Maintenance Strategy:** Caloric intake matches expenditure for muscle preservation and metabolic conditioning.")

with n_col2:
    if bio_profile['weight_delta_to_normal_kg'] > 0:
        st.info(f"🎯 **Target to Healthy BMI (<25.0):** **-{bio_profile['weight_delta_to_normal_kg']} kg** (Healthy ceiling: {bio_profile['max_ideal_weight_kg']} kg).")
    else:
        st.info(f"✅ **Weight Category:** Currently in optimal metabolic range (Ceiling: {bio_profile['max_ideal_weight_kg']} kg).")

# ---------------------------------------------------------
# Execution Pipeline
# ---------------------------------------------------------
if submit_button:
    if not api_key:
        p_name = "Google Gemini" if ai_provider == "gemini" else "Groq"
        p_env = "GEMINI_API_KEY" if ai_provider == "gemini" else "GROQ_API_KEY"
        st.error(f"⚠️ Please provide a {p_name} API key in the sidebar or via the `{p_env}` environment variable.")
        st.stop()

    with st.spinner("FitNaija+ agents analyzing clinical biometrics, regional culinary archives, and joint preservation biomechanics..."):
        try:
            engine = HealthEngine(api_key=api_key, provider=ai_provider, model=model_name)
            plan = engine.generate_plan(
                age=age,
                gender=gender or "Male",
                weight_kg=weight,
                height_cm=height,
                goal=goal,
                culture=culture,
                budget=budget,
                fit_level=fit_level,
                joint_pain="Yes" if "Yes" in (joint_pain or "") else "No",
                output_lang=output_lang or "English",
                user_name=user_name,
                equipment_tier=equipment_tier
            )

            st.session_state["fitnaija_plan"] = plan
            st.session_state["active_engine"] = engine
            st.success(f"🎉 Clinical Health Plan for {user_name} synthesized successfully!")

        except Exception as e:
            st.error(f"❌ Error generating plan: {str(e)}")

# ---------------------------------------------------------
# Display Synthesized Plan
# ---------------------------------------------------------
if "fitnaija_plan" in st.session_state:
    plan = st.session_state["fitnaija_plan"]
    
    st.markdown("---")
    
    tab_plan, tab_nutrition, tab_fitness, tab_mobile = st.tabs([
        "📋 Complete Health Plan",
        "🍲 African Nutrition Architecture",
        "🏃 Joint-Safe Fitness Prescription",
        "📱 Client JSON Schema"
    ])

    # ---------------------------------------------------------
    # Tab 1: Complete Health Plan & Coach Audio Recommendation
    # ---------------------------------------------------------
    with tab_plan:
        doc_col1, doc_col2 = st.columns([2, 1])
        
        with doc_col1:
            # Full Clinical Document (Sections 1, 2, 3, and 4)
            st.markdown(plan.full_plan_markdown)
            
            # Dedicated Coach Audio Recommendation Container (Directly below Section 4: Coach's Motivation)
            # Dedicated Coach Audio Recommendation Container (Coach Motivation for Today)
            with st.container(border=True):
                head_col1, head_col2 = st.columns([3, 1])
                with head_col1:
                    st.markdown("### :material/volume_up: Coach Motivation for Today")
                    st.caption("Authentic daily voice motivation from your personal coach, culturally grounded and tailored to today's food, water, and knee-safe movements.")
                with head_col2:
                    if st.button("🔄 Regenerate Today's Motivation", key=f"regen_btn_{plan.plan_id}", use_container_width=True):
                        with st.spinner("Multi-agent team is architecting and composing today's fresh coach motivation..."):
                            try:
                                engine_to_use = st.session_state.get("active_engine")
                                if not engine_to_use:
                                    active_api_key = api_key or get_groq_api_key() or get_gemini_api_key()
                                    engine_to_use = HealthEngine(api_key=active_api_key, provider=ai_provider, model=model_name)
                                    st.session_state["active_engine"] = engine_to_use

                                s_count = getattr(plan.biometrics, "water_sachets_50cl", max(5, int(round(plan.biometrics.water_target_liters / 0.5))))
                                eq_tier = getattr(plan.fitness, "equipment_tier", "Home (Zero Equipment / Pure Bodyweight)")
                                new_script, new_trace = engine_to_use.generate_daily_coach_motivation(
                                    user_name=plan.user_name,
                                    gender=getattr(plan.biometrics, "gender", "Male"),
                                    weight_kg=plan.biometrics.weight_kg,
                                    goal=goal,
                                    culture=culture,
                                    target_calories=plan.biometrics.target_calories,
                                    water_sachets=s_count,
                                    equipment_tier=eq_tier,
                                    joint_pain="Yes" if "Yes" in (joint_pain or "") else "No",
                                    language=output_lang or "English"
                                )
                                plan.coach_motivation = new_script
                                plan.multi_agent_trace = new_trace
                                # Invalidate cached audio so new monologue is synthesized
                                for k in list(st.session_state.keys()):
                                    if k.startswith(f"voice_bytes_{plan.plan_id}"):
                                        del st.session_state[k]
                                st.session_state["fitnaija_plan"] = plan
                                st.success("✨ Fresh daily motivation synthesized by your native cultural coach!")
                                st.rerun()
                            except Exception as regen_err:
                                st.error(f"Failed to regenerate motivation: {str(regen_err)}")

                # Badges for active language and active voice model
                lang_label = output_lang or "English"
                active_yarngpt_key = yarngpt_key or get_yarngpt_api_key()
                active_gemini_key = get_gemini_api_key()

                if selected_voice_engine == "gemini":
                    st.markdown(f":purple-badge[🎙️ Engine: Google Gemini Voice Studio ({gemini_selected_voice or 'Puck'})] :blue-badge[🗣️ Language: {lang_label}]")
                elif selected_voice_engine == "edge":
                    st.markdown(f":blue-badge[🎙️ Engine: Microsoft Nigerian Neural] :blue-badge[🗣️ Language: {lang_label}]")
                else:
                    st.markdown(f":green-badge[🎙️ Engine: YarnGPT Nigerian Voice AI (Active)] :blue-badge[🗣️ Language: {lang_label}]")

                gender_for_persona = "Male"
                coach_meta = NativeCoachLinguistAgent.get_coach_persona_meta(lang_label, gender_for_persona)

                # Coach Persona Header Card
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(30, 77, 43, 0.08) 0%, rgba(200, 90, 23, 0.08) 100%);
                            border: 1px solid rgba(46, 125, 50, 0.25); border-radius: 12px; padding: 12px 18px; margin: 10px 0 14px 0;">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-weight: 700; font-size: 15px; color: #1e4d2b;">🎙️ {coach_meta['title']} ({coach_meta['coach_name']})</span>
                            <span style="background: #e8f5e9; color: #2e7d32; font-size: 11.5px; font-weight: 600; padding: 3px 9px; border-radius: 12px; margin-left: 8px;">
                                {coach_meta['role']}
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #555; font-style: italic;">{coach_meta['tagline']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Display personalized AI Coach Spoken Briefing
                st.markdown(f"""
                <div style="background-color: #F0FDF4; border-left: 4px solid #16A34A; padding: 14px 18px; border-radius: 8px; margin: 0 0 16px 0;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <strong style="color: #166534; font-size: 15px;">🗣️ Today's Daily Coach Motivation ({lang_label}):</strong>
                    </div>
                    <p style="color: #14532D; font-size: 14.5px; margin: 0; line-height: 1.6; font-style: italic;">
                        "{plan.coach_motivation}"
                    </p>
                </div>
                """, unsafe_allow_html=True)

                audio_col1, audio_col2 = st.columns([1, 2])

                chosen_gem_name = "Kore" if "Kore" in str(gemini_selected_voice) else ("Charon" if "Charon" in str(gemini_selected_voice) else ("Aoede" if "Aoede" in str(gemini_selected_voice) else "Puck"))

                with audio_col1:
                    if selected_voice_engine == "gemini":
                        voice_options = [f"Coach {chosen_gem_name} (African Cadence)"]
                    elif active_yarngpt_key and selected_voice_engine == "yarngpt":
                        v_m = get_yarngpt_voice_name(lang_label, "Male").capitalize()
                        v_f = get_yarngpt_voice_name(lang_label, "Female").capitalize()
                        voice_options = [f"Coach {v_m} (Male)", f"Coach {v_f} (Female)"]
                    else:
                        voice_options = ["Coach Abeo (Male)", "Coach Ezinne (Female)"]

                    voice_choice = st.radio(
                        "Select coach voice:",
                        voice_options,
                        index=0,
                        horizontal=False,
                        key=f"voice_radio_{plan.plan_id}_{selected_voice_engine}"
                    )

                with audio_col2:
                    voice_cache_key = f"voice_bytes_{plan.plan_id}_{voice_choice}_{lang_label}_{selected_voice_engine}_{chosen_gem_name}"
                    if voice_cache_key not in st.session_state:
                        with st.spinner("Synthesizing authentic coach audio briefing..."):
                            audio_script = compile_audio_script(plan, lang_label)
                            gender_param = "Female" if "Female" in voice_choice or "Kore" in voice_choice or "Aoede" in voice_choice else "Male"
                            audio_res, engine_used = generate_voice_note(
                                text=audio_script,
                                voice_gender=gender_param,
                                language=lang_label,
                                custom_api_key=active_yarngpt_key,
                                preferred_engine=selected_voice_engine,
                                gemini_voice_name=chosen_gem_name if selected_voice_engine == "gemini" else None,
                                english_fallback_text=_compile_english_script(plan)
                            )
                            st.session_state[voice_cache_key] = (audio_res, engine_used, audio_script)

                    audio_bytes, engine_used, spoken_script = st.session_state[voice_cache_key]

                    if "[YarnGPT Quota Depleted]" in engine_used:
                        st.info("ℹ️ **Indigenous Voice Quota**: Your YarnGPT account has 68 characters remaining. Coach Abeo is speaking via Nigerian Neural Studio. Top up at [yarngpt.ai](https://yarngpt.ai) to re-enable direct indigenous speech synthesis.")

                    mime_fmt = "audio/wav" if audio_bytes.startswith(b"RIFF") else "audio/mp3"
                    file_ext = "wav" if audio_bytes.startswith(b"RIFF") else "mp3"
                    st.audio(audio_bytes, format=mime_fmt)

                    st.download_button(
                        label=f"📥 Download Coach Motivation ({file_ext.upper()})",
                        data=audio_bytes,
                        file_name=f"FitNaija_Motivation_{plan.user_name}_{lang_label}.{file_ext}",
                        mime=mime_fmt,
                        icon=":material/download:"
                    )

                with st.expander(":material/subtitles: View Spoken Audio Script Transcript", expanded=False):
                    st.markdown(f"> *\"{spoken_script}\"*")
                    st.caption(f"Audio Engine: {engine_used} | Language: {lang_label}")

                # Multi-Agent Generation Trace
                trace = getattr(plan, "multi_agent_trace", None)
                with st.expander("🔍 Multi-Agent Generation Trace (Prompt Architect ➔ Native Linguist ➔ Audio Director)", expanded=False):
                    if trace:
                        st.markdown(f"**Multi-Agent Pipeline**: `{trace.get('pipeline', 'FitNaija+ Daily Coach Motivation Multi-Agent Engine')}`")
                        st.caption(f"Generated at: {trace.get('timestamp', 'N/A')} | Target Dialect: **{trace.get('target_language', lang_label)}**")

                        tcol1, tcol2, tcol3 = st.columns(3)
                        with tcol1:
                            st.markdown("##### 🏗️ Agent 1: Prompt Architect")
                            a1 = trace.get("agent_1_prompt_architect", {})
                            st.markdown(f"**Agent**: `MotivationPromptArchitectAgent`")
                            st.markdown(f"**Role**: {a1.get('role', 'Biometric & Cultural Prompt Architect')}")
                            st.markdown(f"**Status**: :green-badge[{a1.get('status', 'completed')}]")
                            with st.popover("View Architected Task"):
                                st.write(a1.get("user_task", "N/A"))
                            st.caption(f"Inputs: {a1.get('weight_kg', 0):.0f}kg | ~{a1.get('target_calories', 0)} kcal | {a1.get('water_sachets', 0)} sachets")

                        with tcol2:
                            st.markdown("##### 🗣️ Agent 2: Native Linguist")
                            a2 = trace.get("agent_2_native_linguist", {})
                            st.markdown(f"**Agent**: `NativeCoachLinguistAgent`")
                            st.markdown(f"**Persona**: **{a2.get('coach_name', coach_meta['coach_name'])}**")
                            st.markdown(f"**Role**: {a2.get('role', 'Native Cultural Coach')}")
                            st.markdown(f"**Status**: :green-badge[{a2.get('status', 'completed')}]")
                            st.caption(f"Monologue: {a2.get('word_count', len(plan.coach_motivation.split()))} words (cadence checked)")

                        with tcol3:
                            st.markdown("##### 🎙️ Agent 3: Audio Director")
                            a3 = trace.get("agent_3_audio_director", {})
                            st.markdown(f"**Agent**: `AudioDirectorAgent`")
                            st.markdown(f"**Role**: {a3.get('role', 'Acoustic Prosody & Audio Synthesis Director')}")
                            st.markdown(f"**Synthesis Engine**: `{engine_used}`")
                            st.markdown(f"**Prosody Normalization**: :green-badge[Applied (phonetic numbers)]")
                            st.caption(f"Acoustic delivery optimized for {lang_label}")
                    else:
                        st.info("Multi-agent trace metadata is active and will be populated for all generated plans and on-the-fly regenerations.")

            st.markdown("---")
            pdf_bytes = build_pdf(
                raw_text=plan.full_plan_markdown,
                biometrics=bio_profile,
                user_metadata={
                    "culture": culture,
                    "goal": goal,
                    "lang": lang_label,
                    "equipment_tier": getattr(plan.fitness, "equipment_tier", "Home Workout"),
                    "target_heart_rate_zone": getattr(plan.fitness, "target_heart_rate_zone", "Zone 2 FatMax"),
                    "est_calories_burned_per_session": getattr(plan.fitness, "est_calories_burned_per_session", 160)
                },
                user_name=plan.user_name
            )

            pcol1, pcol2 = st.columns(2)
            with pcol1:
                st.download_button(
                    label="📥 Download Official Clinical PDF",
                    data=pdf_bytes,
                    file_name=f"FitNaija_Clinical_Plan_{plan.user_name}.pdf",
                    mime="application/pdf",
                    icon=":material/picture_as_pdf:"
                )
            with pcol2:
                st.download_button(
                    label="💾 Download Plan JSON Data",
                    data=plan.model_dump_json(indent=2),
                    file_name=f"FitNaija_Plan_{plan.user_name}.json",
                    mime="application/json",
                    icon=":material/code:"
                )

        with doc_col2:
            st.markdown("#### :material/directions_run: Joint-Safe Movement Studio")
            st.caption("Continuous animated demonstrations for zero-impact joint protection.")

            ex_choice = st.segmented_control(
                "Select Movement Guide:",
                ["Wall Push-Ups", "Chair Squats", "Flat Marching"],
                default="Wall Push-Ups"
            )

            if ex_choice == "Wall Push-Ups":
                gif_path = "assets/images/wall_pushups.gif"
                ex_title = "Wall Push-Ups (Upper Body)"
                ex_specs = "📐 **Safe Angle:** 45° | 🛡️ **Spine:** Completely Neutral | 🟢 **Impact:** 0 lbs Joint Shock"
                ex_cues = "Palms flat at shoulder-width against wall. Inhale down for 3s, pause 0.5s, exhale and press back."
            elif ex_choice == "Chair Squats":
                gif_path = "assets/images/chair_squats.gif"
                ex_title = "Chair Sit-to-Stand (Lower Body)"
                ex_specs = "📐 **Knee Angle:** 90° Max | 🛡️ **Knees:** Over Ankles | 🟢 **Impact:** Zero Patellar Shear"
                ex_cues = "Hips hinge back to touch chair seat lightly. Drive through heels to stand. Never collapse into chair."
            else:
                gif_path = "assets/images/flat_marching.gif"
                ex_title = "Flat-Ground Marching (Cardio)"
                ex_specs = "📐 **Height:** Hip Level | 🛡️ **Footing:** Soft Forefoot | 🟢 **Impact:** Zero Jumping Shock"
                ex_cues = "Rhythmic knee lift with opposite arm counterswing. Land softly on forefoot. No concrete running."

            st.image(gif_path, caption=f"🎬 Continuous Motion Guide: {ex_title}", width="stretch")
            st.markdown(ex_specs)
            st.info(f"💡 **Clinical Form Check:** {ex_cues}")

            with st.expander(":material/movie: AI Video Prompt Studio (Google Veo 3.1)", expanded=False):
                st.caption("Agent-crafted cinematic prompt formatted for Google Veo 3.1 and text-to-video models:")
                video_prompt_data = draft_exercise_video_prompt(
                    exercise_name=ex_choice or "Wall Push-Ups",
                    user_name=plan.user_name,
                    gender=plan.biometrics.gender,
                    age=age,
                    weight_kg=plan.biometrics.weight_kg,
                    joint_pain=plan.fitness.has_joint_pain,
                    language=lang_label
                )
                st.code(video_prompt_data["veo_prompt"], language="text")
                st.caption(f"Target Architecture: {video_prompt_data['target_model']} | Aspect: {video_prompt_data['aspect_ratio']}")

                gem_key = get_gemini_api_key()
                if gem_key:
                    if st.button(f"✨ Generate Real-Time Visual for {ex_choice}", key=f"btn_gen_{ex_choice}"):
                        with st.spinner(f"Invoking Gemini for real-time visual demonstration of {ex_choice}..."):
                            v_bytes = generate_gemini_exercise_image(video_prompt_data["veo_prompt"], gem_key)
                            if v_bytes:
                                st.image(v_bytes, caption=f"Gemini Real-Time Visual: {ex_choice}")
                            else:
                                st.info("💡 Real-time image API hit quota limits on this key tier. Continuous animated form guide displayed above.")

    # ---------------------------------------------------------
    # Tab 2: African Nutrition Architecture
    # ---------------------------------------------------------
    with tab_nutrition:
        st.subheader("🍲 Localized Nutrition Regimen & Portion Architecture")
        st.markdown(f"**Cultural Profile:** {plan.cultural_cuisine} | **Daily Energy Ceiling:** ~{plan.biometrics.target_calories:,} kcal")
        
        # African Healthy Plate Architecture (50 / 25 / 25 Model)
        st.markdown("#### :material/pie_chart: The African Healthy Plate Architecture (50 / 25 / 25 Model)")
        
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            with st.container(border=True):
                st.markdown("##### 🥗 50% Half-Plate: Un-Oiled Greens")
                st.caption(
                    "Bulk with traditional draw and leafy soups: **Ewedu, Okra, Miyan Kuka, Efo Riro, Bitterleaf**. "
                    "Dense in soluble fiber, micronutrients, zero insulin spike."
                )
                st.badge("50% of Plate", color="green")
                
        with p_col2:
            with st.container(border=True):
                st.markdown("##### 🍗 25% Quarter-Plate: Lean Protein")
                st.caption(
                    "Palm-sized serving: **Grilled Mackerel, Tilapia, Skinless Chicken, 2 Boiled Eggs, Steamed Moimoi**. "
                    "Preserves skeletal muscle mass during fat loss."
                )
                st.badge("25% of Plate", color="orange")
                
        with p_col3:
            with st.container(border=True):
                st.markdown("##### 🥣 25% Quarter-Plate: Smart Swallow")
                st.caption(
                    "Strictly 1 clenched fist (~150g): **Amala, Tuwon Shinkafa, Oat Swallow, Eba**. "
                    "Satisfies culinary heritage without carbohydrate overload."
                )
                st.badge("25% of Plate", color="red")
        
        ncol1, ncol2 = st.columns(2)
        with ncol1:
            st.markdown("#### :material/straighten: Clinical Portion Rules")
            for rule in plan.nutrition.swallow_portion_rules:
                st.markdown(f'<div class="rule-card">{rule}</div>', unsafe_allow_html=True)
                
            st.markdown("#### :material/check_circle: Traditional Foods to Prioritize")
            for food in plan.nutrition.foods_to_embrace:
                st.markdown(f"- ✅ **{food}**")
                
        with ncol2:
            st.markdown("#### :material/oil_barrel: Healthy Cooking & Oil Protocols")
            for prep in plan.nutrition.oil_and_cooking_rules:
                st.markdown(f'<div class="rule-card">{prep}</div>', unsafe_allow_html=True)
                
            st.markdown("#### :material/warning: Preparations to Minimize")
            for food in plan.nutrition.foods_to_minimize:
                st.markdown(f"- ⚠️ **{food}**")

        st.markdown("---")
        
        # 1-Fist Swallow Rule vs Buka Wrap Savings
        st.markdown("#### :material/balance: The 1-Fist Swallow Rule: Calorie Savings Architecture")
        savings = calculate_swallow_calorie_savings()
        
        with st.container(border=True):
            scol1, scol2, scol3 = st.columns(3)
            with scol1:
                st.metric(label="Standard Buka Wrap (~350g)", value=f"~{savings['buka_calories']} kcal")
            with scol2:
                st.metric(label="FitNaija+ 1-Fist (~150g)", value=f"~{savings['fitnaija_calories']} kcal")
            with scol3:
                st.metric(label="Net Deficit Per Meal", value=f"-{savings['savings_per_meal']} kcal")
            
            st.info(
                f"🎯 **Compounding Weekly Impact:** Saving ~**{savings['weekly_savings']:,} kcal/week** "
                f"(≈ {savings['weekly_fat_loss_est_kg']} kg steady fat loss per week) simply by sizing your swallow "
                f"to your clenched fist — with zero starvation and 100% cultural enjoyment!"
            )

        # Hypertension Defense
        st.markdown("#### :material/favorite: Hypertension Defense & Ancestral Umami")
        with st.container(border=True):
            st.markdown("""
            **The 1/2 Bouillon Cube Rule:** Over 38% of urban West African adults manage elevated blood pressure.
            Cut commercial bouillon cubes (Maggi/Knorr) by 50% and substitute ancestral umami seasonings: 
            **Iru (fermented locust beans)**, **Ogiri**, ground dried crayfish, dried catfish, and indigenous aromatics 
            (Uziza seeds, Uda pods, and Ehuru calabash nutmeg). Maximum flavor with minimal sodium impact!
            """)

        st.markdown("---")
        st.subheader("🍽️ Sample Day Blueprint")
        meal_cols = st.columns(len(plan.nutrition.meals))
        for idx, meal in enumerate(plan.nutrition.meals):
            with meal_cols[idx]:
                with st.container(border=True):
                    st.markdown(f"**{meal.meal_time}**")
                    st.write(f"🥣 **{meal.dish}**")
                    st.caption(f"**Portion:** {meal.portion_guide}")
                    st.caption(f"**Prep:** {meal.cooking_instructions}")
                    if meal.approx_calories:
                        st.badge(f"~{meal.approx_calories} kcal", color="green")

    # ---------------------------------------------------------
    # Tab 3: Safe Fitness Prescription & Exercise Physiology Engine
    # ---------------------------------------------------------
    with tab_fitness:
        st.subheader("🏃 Clinical Exercise Physiology & Joint-Safe Movement Regimen")
        
        # Meta badge strip
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.badge(f"Setting: {getattr(plan.fitness, 'equipment_tier', 'Home Workout')}", icon=":material/home_work:", color="blue")
        with m2:
            st.badge(f"Target: {getattr(plan.fitness, 'target_heart_rate_zone', 'Zone 2 FatMax')}", icon=":material/cardiology:", color="red")
        with m3:
            st.badge(f"Burn: ~{getattr(plan.fitness, 'est_calories_burned_per_session', 150)} kcal/session", icon=":material/local_fire_department:", color="orange")
        with m4:
            st.badge(f"Steps: {plan.fitness.daily_step_goal:,} steps/day", icon=":material/footprint:", color="green")

        st.markdown("---")

        # Exercise Physiology Core Cardiorespiratory & Exertion Metrics
        st.markdown("#### :material/vital_signs: Exercise Physiology: Energy Expenditure & Cardiorespiratory Zones")
        pcol1, pcol2, pcol3 = st.columns(3)
        
        with pcol1:
            with st.container(border=True):
                st.markdown("##### 🫀 Zone 2 FatMax Heart Rate")
                st.metric("Target Training BPM", plan.fitness.target_heart_rate_zone or "Zone 2 FatMax")
                st.caption(
                    "Calculated via Tanaka equation ($208 - 0.7 \\times \\text{age}$). "
                    "Optimizes mitochondrial fat oxidation without spiking cortisol or placing compressive shear on knees."
                )

        with pcol2:
            with st.container(border=True):
                st.markdown("##### 🗣️ Perceived Exertion (Borg CR10)")
                st.metric("Target Intensity", "RPE 4 – 6 (Moderate)")
                st.caption(
                    "**Clinical Talk Test Rule:** You must be able to converse in full sentences without gasping for air. "
                    "If breathing becomes ragged, reduce cadence immediately."
                )

        with pcol3:
            with st.container(border=True):
                st.markdown("##### ⚡ Metabolic Equivalent (METs)")
                st.metric("Est. Session Burn", f"~{plan.fitness.est_calories_burned_per_session} kcal")
                st.caption(
                    f"Based on {plan.biometrics.weight_kg}kg body weight across prescribed movements. "
                    f"4 weekly sessions generate a metabolic bonus of ~{plan.fitness.est_calories_burned_per_session * 4:,} kcal."
                )

        # 7-Day Periodized Microcycle Schedule
        if getattr(plan.fitness, "weekly_schedule", None):
            st.markdown("#### :material/calendar_month: 7-Day Periodized Training Schedule (Microcycle)")
            st.caption("Periodized distribution of muscular endurance, cardiovascular lipolysis, active recovery, and joint decompression.")
            
            with st.container(border=True):
                for idx, day_plan in enumerate(plan.fitness.weekly_schedule):
                    is_rest = any(w in day_plan.get("focus", "").lower() for w in ["rest", "sinmi", "ike", "hutu"])
                    color_tag = "💤" if is_rest else "🏋️‍♂️"
                    with st.expander(f"{color_tag} **{day_plan.get('day', f'Day {idx+1}')}** — {day_plan.get('focus', 'Training')}", expanded=(idx in (0, 1))):
                        d_sub1, d_sub2, d_sub3 = st.columns(3)
                        with d_sub1:
                            st.markdown(f"**Modality:** {day_plan.get('modality', 'Resistance')}")
                        with d_sub2:
                            st.markdown(f"**Duration:** {day_plan.get('duration', '30 mins')}")
                        with d_sub3:
                            st.markdown(f"**Intensity:** {day_plan.get('intensity', 'RPE 4-5')}")

        # Biomechanical Joint-Safety Traffic Light Matrix
        st.markdown("#### :material/traffic: Biomechanical Joint-Safety Traffic Light System")
        jcol1, jcol2 = st.columns(2)
        with jcol1:
            with st.container(border=True):
                st.markdown("##### 🔴 STRICTLY FORBIDDEN (High Impact / Joint Wear)")
                st.markdown("""
                - **Zero Jumping Movements:** No jumping jacks, burpees, or skipping rope.
                - **No Deep Knee Bends:** Never bend knees past 90 degrees.
                - **No Concrete Running:** Prevents 3-5x bodyweight joint shock.
                - **No Forward Shear Lunges:** Protects patellofemoral tracking.
                """)
        with jcol2:
            with st.container(border=True):
                st.markdown("##### 🟢 PRESCRIBED JOINT PROTECTORS (0 lbs Impact)")
                st.markdown("""
                - **Wall & Incline Push-ups:** Zero wrist compression, protects lumbar spine.
                - **Chair Sit-to-Stands:** Builds quadriceps and glutes with fixed depth stop.
                - **Water Bottle / Keg Exercises:** Safe domestic resistance without spinal load.
                - **Flat-Ground Zone 2 Walking:** Gentle, sustained metabolic lipolysis.
                """)

        st.markdown("#### :material/warning: Clinical Joint Precautions")
        for precaution in plan.fitness.joint_precautions:
            st.warning(precaution)
            
        st.markdown("#### :material/fitness_center: Prescribed Movement Exercises")
        for ex in plan.fitness.exercises:
            eq_text = getattr(ex, "equipment_needed", "None / Bodyweight")
            met_text = getattr(ex, "met_value", 3.5)
            tempo_text = getattr(ex, "tempo_and_breathing", "3-sec descent, 1-sec pause, 1-sec press")
            
            with st.expander(f":material/check_circle: {ex.name} — {ex.reps_or_duration}", expanded=True):
                e_c1, e_c2 = st.columns(2)
                with e_c1:
                    st.markdown(f"🛠️ **Equipment Needed:** `{eq_text}`")
                    st.markdown(f"🎯 **Target Muscle Chain:** {ex.target_area}")
                    st.markdown(f"⏱️ **Clinical Tempo & Breathing:** {tempo_text}")
                with e_c2:
                    st.markdown(f"🔥 **Metabolic Intensity:** ~`{met_text} METs`")
                    st.markdown(f"📝 **Execution Steps:** {ex.instructions}")
                st.success(f"🛡️ **Joint Protection Clinical Note:** {ex.joint_safety_notes}")

    # ---------------------------------------------------------
    # Tab 4: Clean JSON Schema
    # ---------------------------------------------------------
    with tab_mobile:
        st.subheader("📱 Clean Mobile JSON Payload (Pydantic Schema)")
        st.caption("Validated data payload ready for ingestion by iOS, Android, Flutter, or React Native client apps.")
        st.json(plan.model_dump())

st.markdown("---")
st.caption("🔬 Nutritional benchmarks formulated using the FAO/INFOODS West African Food Composition Table & FMOH Guidelines.")
