import os
import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(page_title="FitNaija+ AI Engine", page_icon="🌿")
st.title("🌿 FitNaija+ AI Health Engine")
st.caption("Culturally aligned nutrition and joint-safe fitness recommendations.")

# Read key from secrets or input
groq_key = st.secrets.get("GROQ_API_KEY", "") or st.sidebar.text_input("Groq API Key", type="password")

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", 18, 100, 30)
    gender = st.selectbox("Gender", ["Female", "Male"])
    weight = st.number_input("Weight (kg)", 40, 200, 85)
    height = st.number_input("Height (cm)", 120, 220, 168)
with col2:
    culture = st.selectbox("Diet Preference", ["Yoruba Cuisine", "Hausa/Northern Cuisine", "General Nigerian / English"])
    budget = st.selectbox("Budget Tier", ["Market Staples (Low Cost)", "Flexible"])
    fit_level = st.selectbox("Fitness Level", ["Absolute Beginner", "Light Walker", "Active"])
    joint_pain = st.radio("Joint/Knee Discomfort?", ["Yes (Protect Joints)", "No"])
    language = st.selectbox("Language", ["English", "Yoruba", "Hausa"])

if st.button("Generate Localized Plan 🚀", type="primary"):
    if not groq_key:
        st.error("Please provide a Groq API Key.")
    else:
        with st.spinner("Agent analyzing biometrics & local diet..."):
            client = Groq(api_key=groq_key)
            bmr = (10 * weight + 6.25 * height - 5 * age + 5) if gender == "Male" else (10 * weight + 6.25 * height - 5 * age - 161)
            target_cal = int(bmr * 1.2 - 400)

            prompt = f"""
            You are FitNaija+, an expert African nutrition and joint-safe fitness system.
            Target Language: {language}
            Target Calories: ~{target_cal} kcal/day.
            Cultural Diet: {culture}. Budget: {budget}.
            Fitness Level: {fit_level}. Joint Issues: {joint_pain}.

            Provide:
            1. Biometric Target Summary (calories/hydration)
            2. Meal Plan (Breakfast, Lunch, Dinner with local portion sizes like fist-sized amala/tuwo, reduced oil)
            3. 3 Safe Exercises matching physical condition
            4. Coach Encouragement in {language}
            """
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            plan = resp.choices[0].message.content
            st.markdown(plan)

            # PDF generation
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "FitNaija+ Health Plan", ln=True, align="C")
            pdf.ln(5)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 7, plan.encode('latin-1', 'replace').decode('latin-1'))
            pdf.output("plan.pdf")

            with open("plan.pdf", "rb") as f:
                st.download_button("📥 Download PDF Plan", f, file_name="FitNaija_Plan.pdf")
