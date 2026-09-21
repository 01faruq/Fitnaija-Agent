import os
import io
import html
import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# UI Configuration
st.set_page_config(
    page_title="FitNaija+ AI Engine",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 2.1rem; font-weight: 700; color: #1E4620; margin-bottom: 2px; }
    .sub-title { font-size: 1.0rem; color: #4A5568; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.2em; background-color: #2E7D32; color: white; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌿 FitNaija+ AI Health Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Localized African clinical nutrition & joint-safe mobility engine.</p>', unsafe_allow_html=True)

# Secure API Key Retrieval
api_key = st.secrets.get("GROQ_API_KEY", None) or os.environ.get("GROQ_API_KEY", None)

if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
    if not api_key:
        st.info("💡 Please provide your Groq API key in the sidebar or Streamlit Secrets to begin.")
        st.stop()

# Initialize OpenAI client pointed at Groq
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Intake Form
with st.form("fitnaija_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Biometrics")
        age = st.number_input("Age", min_value=16, max_value=95, value=30)
        gender = st.selectbox("Biological Sex", ["Female", "Male"])
        weight = st.number_input("Current Weight (kg)", min_value=40.0, max_value=220.0, value=88.0, step=0.5)
        height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=168.0, step=0.5)
        goal = st.selectbox("Health Focus", ["Weight Loss (Caloric Deficit)", "Weight Maintenance", "Cardio Conditioning"])

    with col2:
        st.subheader("2. Regional Nutrition")
        culture = st.selectbox(
            "Cultural Food Profile",
            [
                "Yoruba Cuisine (Amala, Ewedu, Gbegiri, Efo Riro, Moimoi)",
                "Hausa / Northern Cuisine (Tuwon Shinkafa, Miyan Kuka, Zogale, Acha)",
                "Igbo / South-East Cuisine (Ofe Nsala, Bitterleaf Soup, Ukwa, Okra)",
                "South-South Cuisine (Banga, Fisherman Soup, Owo)",
                "General Urban Nigerian (Brown Beans, Boiled Plantain, Grilled Fish)"
            ]
        )
        budget = st.selectbox("Budget Archetype", ["Open Market Staples (Affordable)", "Flexible Grocery"])
        meals_per_day = st.radio("Routine", ["3 Standard Meals", "2 Meals + 1 Healthy Snack"], horizontal=True)

    with col3:
        st.subheader("3. Mobility & Language")
        fit_level = st.selectbox("Current Fitness Level", ["Beginner (Sedentary)", "Moderate Walker", "Active"])
        joint_pain = st.radio("Joint, Knee, or Back Pain?", ["Yes (Protect Knees/Back)", "No (Standard Bodyweight)"])
        output_lang = st.selectbox("Output Language", ["English", "Nigerian Pidgin", "Yoruba", "Hausa"])

    submit_button = st.form_submit_button("Generate Personalized Plan 🚀")

# Biometric & Caloric Math
height_m = height / 100.0
bmi = weight / (height_m ** 2)

if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

tdee = bmr * 1.2
target_cal = int(tdee - 450) if "Loss" in goal else int(tdee)

# Bulletproof PDF Generator (Sanitizes markdown tags and symbols)
def build_pdf(raw_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#1E4620"), spaceAfter=10
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8
    )
    
    story = [
        Paragraph("FitNaija+ Personalized Health & Nutrition Plan", title_style),
        Paragraph(f"<b>Biometric Profile:</b> BMI: {bmi:.1f} | Daily Caloric Target: ~{target_cal} kcal", body_style),
        Spacer(1, 10)
    ]
    
    # Clean text to prevent ReportLab XML parser errors
    for block in raw_text.split("\n\n"):
        clean = block.replace("**", "").replace("###", "").replace("##", "").replace("#", "").strip()
        if clean:
            safe_text = html.escape(clean).replace("\n", "<br/>")
            story.append(Paragraph(safe_text, body_style))
            story.append(Spacer(1, 4))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# Execution Pipeline
if submit_button:
    with st.spinner("FitNaija+ agent analyzing biometrics & local nutrition profile..."):
        instructions = f"""
        You are the clinical AI brain of FitNaija+, an African preventative health engine.
        Target Language: {output_lang}.
        User Profile:
        - BMI: {bmi:.1f} ({'Obese' if bmi >= 30 else 'Overweight' if bmi >= 25 else 'Normal'})
        - Daily Target: ~{target_cal} kcal/day.
        - Cultural Cuisine: {culture}
        - Budget: {budget}
        - Fitness Level: {fit_level}
        - Joint Discomfort: {joint_pain}

        Structure your advice into four clear sections:
        1. BIOMETRIC TARGET & HYDRATION: Summarize calories, palm/fist portion control for swallows, and water goals.
        2. LOCAL NUTRITION REGIMEN: Detail breakfast, lunch, and dinner using authentic dishes from {culture}. Crucially specify how to prepare them safely (drastically cutting palm/groundnut oil, boiling/grilling over frying, bulking soups with un-oiled vegetable leaves like Ewedu, Okra, or Kuka).
        3. JOINT-SAFE EXERCISE PRESCRIPTION: 3 low-impact exercises matching their mobility. If joint issues exist, strictly forbid jumping and deep squats; recommend seated leg raises, wall push-ups, and flat walking.
        4. COACH'S MOTIVATION: An encouraging closing written naturally in {output_lang}.
        """

        try:
            # Responses API call on Groq
            response = client.responses.create(
                model="openai/gpt-oss-120b",
                instructions=instructions,
                input=f"Generate the comprehensive plan in {output_lang}."
            )
            
            # Universal text extractor (handles SDK variations and nested objects)
            plan_text = ""
            if hasattr(response, "output_text") and response.output_text:
                plan_text = response.output_text
            elif hasattr(response, "output") and response.output:
                for item in response.output:
                    if hasattr(item, "content"):
                        for block in item.content:
                            if hasattr(block, "text"):
                                plan_text += block.text if isinstance(block.text, str) else getattr(block.text, "value", str(block.text))
            
            if not plan_text:
                plan_text = str(response)

            st.success("Plan generated successfully!")
            
            col_res1, col_res2 = st.columns([2, 1])
            
            with col_res1:
                st.markdown(plan_text)
                
                # PDF Download
                pdf_data = build_pdf(plan_text)
                st.download_button(
                    label="📥 Download Plan as Official PDF",
                    data=pdf_data,
                    file_name="FitNaija_Health_Plan.pdf",
                    mime="application/pdf"
                )

            with col_res2:
                st.markdown("### 🏃 Visual Movement Guides")
                st.info("Demonstrations for low-impact, joint-safe movements:")
                st.image("https://media.giphy.com/media/l3q2wnlw4AbnzNvE8/giphy.gif", caption="Joint-Safe Wall Push-ups")
                st.image("https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif", caption="Low-Impact Chair Squats")
                st.image("https://media.giphy.com/media/3o6Zt6ML6BklcajjsA/giphy.gif", caption="March-in-Place Cardio")

        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
