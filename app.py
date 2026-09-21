import os
import io
import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Page Configuration
st.set_page_config(
    page_title="FitNaija+ AI Engine",
    page_icon="🌿",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E4620; margin-bottom: 0px; }
    .sub-title { font-size: 1.05rem; color: #4A5568; margin-bottom: 25px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2E7D32; color: white; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌿 FitNaija+ AI Health Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Culturally aligned African nutrition and joint-safe fitness recommendations.</p>', unsafe_allow_html=True)

# API Key Retrieval
api_key = st.secrets.get("GROQ_API_KEY", None) or os.environ.get("GROQ_API_KEY", None)

if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
    if not api_key:
        st.info("💡 Please provide a Groq API key in the sidebar or Streamlit Secrets to begin.")
        st.stop()

client = Groq(api_key=api_key)

# Input Form
with st.form("fitnaija_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Biometrics")
        age = st.number_input("Age", min_value=16, max_value=90, value=32)
        gender = st.selectbox("Biological Sex", ["Female", "Male"])
        weight = st.number_input("Current Weight (kg)", min_value=40.0, max_value=220.0, value=89.0, step=0.5)
        height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=165.0, step=0.5)
        goal = st.selectbox("Primary Goal", ["Safe Weight Loss (Caloric Deficit)", "Weight Maintenance & Fitness", "Cardiovascular & Joint Health"])

    with col2:
        st.subheader("2. Local Nutrition")
        culture = st.selectbox(
            "Cultural Food Preference",
            [
                "Yoruba Cuisine (Amala, Ewedu, Efo Riro, Gbegiri, Moimoi)",
                "Hausa / Northern Cuisine (Tuwon Shinkafa, Miyan Kuka, Zogale, Acha)",
                "Igbo / South-East Cuisine (Ofe Nsala, Bitterleaf Soup, Ukwa, Okra)",
                "South-South / Niger-Delta (Banga, Fisherman Soup, Owo)",
                "General Urban Nigerian (Beans Porridge, Boiled Plantain, Grilled Fish)"
            ]
        )
        budget = st.selectbox("Budget & Market Access", ["Local Open Market Staples (Low Cost)", "Moderate / Flexible Household Budget"])
        meals_per_day = st.radio("Daily Meal Routine", ["3 Meals (Breakfast, Lunch, Dinner)", "2 Meals + 1 Healthy Snack"], horizontal=True)

    with col3:
        st.subheader("3. Mobility & Language")
        fit_level = st.selectbox("Current Fitness Level", ["Beginner (Sedentary / Little Activity)", "Light Walker", "Moderately Active"])
        joint_discomfort = st.radio("Joint, Knee, or Lower Back Pain?", ["Yes (Protect Joints - No Jumping)", "No (Standard Bodyweight)"])
        output_lang = st.selectbox("Output Language", ["English", "Nigerian Pidgin", "Yorùbá", "Hausa"])

    submit_button = st.form_submit_button("Generate Personalized Plan 🚀")

# Scientific Calculations
height_m = height / 100.0
bmi = weight / (height_m ** 2)

if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

tdee = bmr * 1.2  # Sedentary multiplier
target_cal = int(tdee - 450) if "Loss" in goal else int(tdee)

def generate_pdf(plan_content):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#1E4620"), spaceAfter=12)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8)
    
    story = [
        Paragraph("FitNaija+ Personalized Health Plan", title_style),
        Paragraph(f"<b>Biometric Overview:</b> BMI: {bmi:.1f} | Caloric Target: ~{target_cal} kcal/day", body_style),
        Spacer(1, 10)
    ]
    
    for paragraph in plan_content.split("\n\n"):
        clean_p = paragraph.replace("*", "").replace("#", "").strip()
        if clean_p:
            story.append(Paragraph(clean_p.replace("\n", "<br/>"), body_style))
            story.append(Spacer(1, 4))
            
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

# Agent Execution
if submit_button:
    with st.spinner("FitNaija+ multi-agent engine compiling your cultural health roadmap..."):
        system_instruction = f"""
        You are the clinical AI brain of FitNaija+, an African preventative health engine.
        Language to output: {output_lang}.
        User Metrics:
        - BMI: {bmi:.1f} ({'Obese' if bmi >= 30 else 'Overweight' if bmi >= 25 else 'Normal'})
        - Daily Target: ~{target_cal} kcal/day.
        - Cultural Diet Archetype: {culture}
        - Budget: {budget}
        - Fitness Level: {fit_level}
        - Joint Discomfort: {joint_discomfort}

        Generate a clear, respectful, and clinically safe recommendation containing:
        1. 📊 BIOMETRIC TARGET & HYDRATION: Summarize calories, portion control rule (e.g., fist rule for swallows, palm rule for lean protein), and water intake.
        2. 🍲 LOCAL NUTRITION REGIMEN: Detail exact dishes matching {culture}. Crucially specify how to prepare them safely (e.g., drastic reduction of palm/groundnut oil, boiling instead of frying, bulking soups with un-oiled vegetable leaves like Ewedu or Kuka).
        3. 🚶 JOINT-SAFE EXERCISE PRESCRIPTION: 3 safe physical movements for home. If joint discomfort is YES, absolutely prohibit running, lunges, and jumping; prescribe seated leg extensions, wall push-ups, or brisk flat-surface walking.
        4. 💡 CULTURAL COACHING & MINDSET: Encouraging advice written naturally in {output_lang}.
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Generate my complete plan in {output_lang}."}
                ],
                temperature=0.3
            )
            
            plan_text = response.choices[0].message.content

            # Visual Display
            st.success("Plan successfully generated!")
            
            col_res1, col_res2 = st.columns([2, 1])
            
            with col_res1:
                st.markdown(plan_text)
                
                # Download PDF
                pdf_data = generate_pdf(plan_text)
                st.download_button(
                    label="📥 Download Plan as Official PDF",
                    data=pdf_data,
                    file_name="FitNaija_Health_Plan.pdf",
                    mime="application/pdf"
                )

            with col_res2:
                st.markdown("### 🏃 Form & Technique Guides")
                st.info("Demonstrations for low-impact, joint-safe movements:")
                st.image("https://media.giphy.com/media/l3q2wnlw4AbnzNvE8/giphy.gif", caption="Joint-Safe Wall Push-ups")
                st.image("https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif", caption="Low-Impact Chair Squats")
                st.image("https://media.giphy.com/media/3o6Zt6ML6BklcajjsA/giphy.gif", caption="March-in-Place Cardio")

        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
