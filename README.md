# 🌿 FitNaija+ AI Preventative Health Engine

**FitNaija+** is an AI preventative health engine for Africans that calculates clinical biometrics and prescribes culturally localized African nutrition, portion architecture, and joint-safe mobility regimens.

---

## 🚀 Key Features

- **Clinical Biometrics Engine**: Computes BMI, WHO categorization, Basal Metabolic Rate (BMR via Mifflin-St Jeor), Total Daily Energy Expenditure (TDEE), safe caloric deficits, and tropical hydration targets (~35 ml/kg).
- **Multi-Provider AI Reasoning**: Switch seamlessly between **Groq** (`openai/gpt-oss-120b`, `llama-3.3-70b-versatile`) and **Google Gemini** (`gemini-2.5-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`) via Google AI Studio.
- **Authentic Nigerian Language Engineering**:
  - Culturally accurate, idiomatically rich generation in **Ìgbò** (*"Ahụike bụ akụ"*, *"iwu ọkpọ aka"*), **Yorùbá** (*"Ìlera l'ọrọ"*, *"ẹ̀ṣẹ́ ọwọ́ kan péré"*), and **Harshen Hausa** (*"Lafiya ita ce jari"*, *"dokar dunkulen hannu"*, *"ledar pure water"*).
  - No broken machine translations or absurd linguistic errors.
- **Offline Clinical Exercise Infographics**: Self-contained high-resolution medical fitness guides for Wall Push-ups, Chair Squats, and Flat-Ground Marching. Zero broken external Giphy URLs or CDN dependencies.
- **Spoken Coach Voice Notes**: 45-second audio briefings in authentic Nigerian cadence with native language scripts. Supports studio-grade **YarnGPT** neural voices (Saheedniyi/YarnGPT) and Neural Voice Studio fallback.
- **Regional African Nutrition Agent**:
  - Grounded in the **FAO/INFOODS West African Food Composition Table** across Yoruba, Hausa/Northern, Igbo/South-East, South-South, and General Urban Nigerian cuisines.
  - **The Swallow Fist Rule**: Strict 1-clenched-fist portion limits for high-carb swallows (Amala, Tuwo, Eba, Pounded Yam).
  - **The Protein Palm Rule**: Recommends palm-sized lean proteins (grilled fish, skinless chicken, boiled eggs, moimoi).
  - **Healthy Preparation Guides**: Drastically reducing palm and groundnut oil, boiling/grilling over frying, and bulking soups with un-oiled greens (Ewedu, Okra, Kuka, Zogale, Bitterleaf).
- **Joint-Safe Fitness Agent**:
  - Automatically enforces joint preservation for users with knee/back discomfort or BMI ≥ 28.
  - Strict contraindications against jumping and deep squats.
  - Prescribes zero-axial-load alternatives: Wall Push-ups, Chair Squats (Sit-to-Stands), Seated Leg Extensions, and Flat Walking.
- **Visual African Healthy Plate Model**: 50/25/25 visual architecture (50% un-oiled greens, 25% lean palm protein, 25% 1-fist swallow).
- **Actionable Hydration**: Translates daily liters into standard 50cl "pure water" sachets or bottles.
- **Bulletproof PDF Generator**: ReportLab generator with ASCII/Latin-1 sanitization to eliminate Unicode missing-glyph errors.
- **Mobile-Ready JSON**: Emits validated Pydantic schemas for consumption by mobile applications.

---

## 📂 Modular Architecture

```
Fitnaija-Agent/
├── pyproject.toml              # UV project & dependency management
├── uv.lock                     # Deterministic dependency lockfile
├── .env.example                # Secrets configuration template
├── app.py                      # Modern Streamlit UI presentation layer
├── main.py                     # CLI launcher
├── assets/
│   └── images/                 # Offline clinical exercise illustrations
│       ├── wall_pushups.jpg
│       ├── chair_squats.jpg
│       └── flat_marching.jpg
├── src/
│   ├── core/
│   │   ├── calculator.py       # Biometric formulas (BMI, Mifflin-St Jeor BMR, TDEE, Deficit)
│   │   └── config.py           # Safe secrets loading (Groq, Gemini, YarnGPT)
│   ├── data/
│   │   └── nigerian_foods.py   # FAO/INFOODS regional Nigerian food database
│   ├── schemas/
│   │   └── models.py           # Pydantic models (FitNaijaPlan, Biometrics, Nutrition, Fitness)
│   ├── agents/
│   │   ├── nutrition_agent.py  # Localized African food rules & portion guides
│   │   ├── fitness_agent.py    # Localized joint-safe exercise prescriptions
│   │   └── health_engine.py    # Multi-provider LLM orchestrator (Groq & Gemini)
│   └── utils/
│       ├── pdf_generator.py    # ReportLab PDF generator with ASCII sanitization
│       └── audio_generator.py  # Authentic Nigerian multilingual coach audio
└── tests/
    └── test_fitnaija.py        # Automated test suite (33 passing unit tests)
```

---

## 🛠️ Quickstart with `uv`

### 1. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your API key(s):
```env
# Groq API (Ultra-Fast) - https://console.groq.com/keys
GROQ_API_KEY=gsk_your_groq_api_key_here

# Google Gemini API (Free tier available) - https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# YarnGPT API (Optional, for studio-grade Nigerian voices) - https://yarngpt.ai
YARNGPT_API_KEY=
```

### 2. Run the App
Launch the Streamlit dashboard using `uv`:
```bash
uv run streamlit run app.py
```

Or use the CLI runner:
```bash
uv run python main.py
```

### 4. Run Automated Tests
```bash
uv run python -m unittest tests/test_fitnaija.py
```

---

## 📜 License
MIT License
