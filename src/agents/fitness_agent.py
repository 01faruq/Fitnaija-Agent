"""Fitness Agent for FitNaija+.

Specializes in clinical Exercise Physiology prescriptions tailored to joint health,
biomechanical protection (knees, lumbar spine, hips), equipment environment, and BMI:
- 4 Equipment Modalities:
  1. Home (Zero Equipment / Pure Bodyweight)
  2. Home (Low-Cost / Domestic Improvised: 1.5L water bottles, 4L/5L kegs, floor tile towel gliders, dining chair)
  3. Gym / Fitness Center (Full equipment & low-impact machines)
  4. Outdoor / Neighborhood (Estate walking loops, park benches, street curbs)
- Cardiorespiratory Targets: Tanaka Zone 2 FatMax Heart Rate & RPE Borg CR10 Scale.
- Caloric Expenditure: Compendium of Physical Activities METs calculation.
- Periodization: 7-Day structured microcycle.
- Biomechanical Joint Protection: Strict contraindications against high-impact ballistic movements.
"""

from typing import Dict, List, Any
from src.schemas.models import ExerciseItem, FitnessPlan
from src.core.calculator import calculate_heart_rate_zones, calculate_workout_met_burn


class FitnessAgent:
    """Agent prescribing evidence-based clinical exercise physiology and joint-safe routines."""

    TIER_HOME_ZERO = "Home (Zero Equipment / Pure Bodyweight)"
    TIER_HOME_IMPROVISED = "Home (Low-Cost / Domestic Improvised: Water bottles, kegs, chair)"
    TIER_GYM = "Gym / Fitness Center (Full equipment)"
    TIER_OUTDOOR = "Outdoor / Neighborhood (Walking loops & park benches)"

    EQUIPMENT_TIERS = [
        TIER_HOME_ZERO,
        TIER_HOME_IMPROVISED,
        TIER_GYM,
        TIER_OUTDOOR,
    ]

    # Explicit movement contraindications for joint preservation
    CONTRAINDICATIONS_JOINT_PAIN: List[str] = [
        "STRICTLY FORBID Jumping Exercises: No jumping jacks, burpees, jump squats, or skipping rope.",
        "STRICTLY FORBID Deep Squats: Do not bend knees past 90 degrees or perform unassisted deep squats.",
        "STRICTLY FORBID High-Impact Running: Avoid running or jogging on hard asphalt or concrete pavements.",
        "STRICTLY FORBID Forward Shear Lunges: Avoid lunges that drive the patella past the toes."
    ]

    CONTRAINDICATIONS_STANDARD: List[str] = [
        "Avoid sudden maximal loading without prior dynamic joint warming.",
        "Maintain a neutral spine during all hip hinge and flexion movements.",
        "Discontinue any movement immediately if sharp joint pain or pinching occurs."
    ]

    @classmethod
    def should_enforce_joint_protection(cls, joint_pain_input: str, bmi: float) -> bool:
        """Determine whether strict joint-preservation protocols must be enforced.
        
        Enforced if user reports pain OR if BMI >= 28.0 (biomechanical joint load threshold).
        """
        has_pain = "yes" in str(joint_pain_input).lower() or "protect" in str(joint_pain_input).lower()
        is_elevated_bmi = bmi >= 28.0
        return has_pain or is_elevated_bmi

    @classmethod
    def generate_fitness_prompt(
        cls,
        fit_level: str,
        joint_pain: str,
        bmi: float,
        language: str = "English",
        equipment_tier: str = TIER_HOME_ZERO,
        age: int = 30
    ) -> str:
        """Construct clinical exercise physiology prescription prompt for the AI model."""
        enforce_protection = cls.should_enforce_joint_protection(joint_pain, bmi)
        hr_info = calculate_heart_rate_zones(age)

        if enforce_protection:
            precautions_text = "\n".join(f"- {c}" for c in cls.CONTRAINDICATIONS_JOINT_PAIN)
            joint_directive = "MANDATORY CLINICAL JOINT PROTECTION: 0 lbs ballistic impact, chair depth stops, zero shear."
        else:
            precautions_text = "\n".join(f"- {c}" for c in cls.CONTRAINDICATIONS_STANDARD)
            joint_directive = "STANDARD PROGRESSION: Controlled bodyweight mechanics, progressive range of motion."

        return f"""
        EXERCISE PHYSIOLOGY & JOINT-MOBILITY DIRECTIVE:
        - Workout Modality & Equipment: {equipment_tier}
        - Reported Fitness Level: {fit_level}
        - Joint Pain Status: {joint_pain}
        - User BMI: {bmi:.1f}
        - Client Age: {age} years
        - Cardiorespiratory Target: Zone 2 FatMax = {hr_info['zone2_fatmax']} (Tanaka HRmax: {hr_info['hr_max']} bpm)
        - Target Exertion: RPE 4-6 on Borg CR10 Scale (Talk Test: able to converse in full sentences without gasping)
        - Joint Protection Protocol Active: {'YES (Strict Contraindications Enforced)' if enforce_protection else 'NO'}
        - Target Language: {language}

        BIOMECHANICAL DIRECTIVE:
        {joint_directive}

        SAFETY WARNINGS & CONTRAINDICATIONS:
        {precautions_text}

        EQUIPMENT-SPECIFIC ADVICE FOR {equipment_tier.upper()}:
        - If Home Zero Equipment: Emphasize Wall Push-Ups, Chair Squats (Sit-to-Stands), flat floor glute bridges, and tempo control (3-sec eccentric lowering).
        - If Home Improvised Equipment: Guide the user on using two 1.5L water bottles (~1.5kg each) for lateral raises/presses, 4L/5L water kegs for goblet sit-to-stands/deadlifts, and smooth tile towel slides for hamstring curls without knee shear.
        - If Gym: Prioritize guided cable rows, seated chest press, horizontal leg press, and recumbent bike/elliptical.
        - If Outdoor: Emphasize estate road flat walking, park bench sit-to-stands, and curb heel raises.
        """

    @classmethod
    def generate_weekly_periodization(
        cls,
        fit_level: str,
        equipment_tier: str,
        has_joint_pain: bool,
        language: str = "English"
    ) -> List[Dict[str, str]]:
        """Generate a 7-day periodized training microcycle adhering to Exercise Physiology principles."""
        lang_lower = str(language).lower()

        if "yoruba" in lang_lower:
            days = ["Ọjọ́ Ajé (Mọ́ndè)", "Ọjọ́ Ìṣẹ́gun (Túsìdè)", "Ọjọ́ Rú (Wẹ́sìdè)", "Ọjọ́bọ̀ (Tọ́sìdè)", "Ọjọ́ Ẹtì (Fúráìdè)", "Ọjọ́ Àbámẹ́ta (Sátidé)", "Ọjọ́ Àìkú (Sọ́ndè)"]
            f_upper = "Agbára Ara Òkè & Ìdúró Gbañgba"
            f_z2 = "Rírìn Ìwọ̀n Zone 2 (Ṣíṣun Ọ̀rá)"
            f_lower = "Agbára Ẹsẹ̀ & Oríkun Láìsí Ìrora"
            f_rec = "Ìsinmi Alágbára & Ìnàra Ẹran Ara"
            f_full = "Eré Ìdárayá Gbogbo Ara Pẹ̀lú Ohun Èlò"
            f_aerobic = "Rírìn Ọjọ́ Àbámẹ́ta Láti Kó Ìṣísẹ̀ Jọ"
            f_rest = "Ìsinmi Pátápátá & Ìmúbọ̀sípò Ẹran Ara"
        elif "igbo" in lang_lower:
            days = ["Mọnde", "Tuzdee", "Wenezdee", "Tọọzdee", "Fraịdee", "Satọdee", "Sọnde"]
            f_upper = "Ike Akụkụ Ahụ Elu & Nkwụsi Ike"
            f_z2 = "Ije Ije Zone 2 (Ịgba Abụba Ọkụ)"
            f_lower = "Ike Akụkụ Ahụ Okpuru na Nkwonkwo Ikpere"
            f_rec = "Izu Ike Dị Nsọ & Ịgbatị Ahụ"
            f_full = "Mgbatị Ahụ Zuru Ezu na Ngwá Ọrụ"
            f_aerobic = "Ije Ije Ọgwụgwụ Izu Maka Ọtụtụ Nzọụkwụ"
            f_rest = "Izu Ike Zuru Ezu na Nri Dị Mma"
        elif "hausa" in lang_lower:
            days = ["Litinin", "Talata", "Laraba", "Alhamis", "Jumma'a", "Asabar", "Lahadi"]
            f_upper = "Ƙarfin Sashen Sama da Gyaran Tsayi"
            f_z2 = "Tafiyar Zone 2 don Ƙona Kitse"
            f_lower = "Ƙarfin Ƙafafu da Kare Gwiwoyi"
            f_rec = "Hutu Mai Amfani da Miƙa Jiki"
            f_full = "Motsa Jiki na Gaba Ɗaya da Kayan Aiki"
            f_aerobic = "Doguwar Tafiyar Ƙarshen Mako don Ƙara Taki"
            f_rest = "Cikakken Hutu don Farfado da Ƙarfi"
        else:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            f_upper = "Upper Body Strength & Posture Alignment"
            f_z2 = "Zone 2 FatMax Cardiovascular Walk"
            f_lower = "Lower Body Biomechanics & Joint Mobility"
            f_rec = "Active Recovery & Joint Decompression"
            f_full = "Full-Body Functional Strength Circuit"
            f_aerobic = "Aerobic Step Accumulation Long Walk"
            f_rest = "Complete Rest, Cellular Recovery & Hydration"

        # Durations & RPE based on fitness level
        dur_str = "20-25 mins" if "beginner" in fit_level.lower() else "30-35 mins"
        dur_walk = "30 mins" if "beginner" in fit_level.lower() else "45 mins"

        return [
            {
                "day": days[0],
                "focus": f_upper,
                "duration": dur_str,
                "intensity": "RPE 4-5 (Moderate - Talk Test: Full sentences)",
                "modality": "Resistance & Joint Stabilization"
            },
            {
                "day": days[1],
                "focus": f_z2,
                "duration": dur_walk,
                "intensity": "Zone 2 Heart Rate (RPE 4-5 / Gentle sweat, no gasping)",
                "modality": "Aerobic Lipolysis & Mitochondrial Conditioning"
            },
            {
                "day": days[2],
                "focus": f_lower,
                "duration": dur_str,
                "intensity": "RPE 5-6 (Controlled tempo, zero knee shear)",
                "modality": "Closed-Kinetic-Chain Hip & Quad Strength"
            },
            {
                "day": days[3],
                "focus": f_rec,
                "duration": "15-20 mins",
                "intensity": "RPE 2-3 (Gentle, restorative)",
                "modality": "Thoracic Mobility, Pelvic Tilts & Hamstring Glides"
            },
            {
                "day": days[4],
                "focus": f_full,
                "duration": dur_str,
                "intensity": "RPE 5-6 (Sustained circuit pacing)",
                "modality": "Functional Multi-Joint Muscular Endurance"
            },
            {
                "day": days[5],
                "focus": f_aerobic,
                "duration": "35-50 mins",
                "intensity": "Zone 2 Target Heart Rate (RPE 4)",
                "modality": "Continuous Low-Impact Cadence & Caloric Expenditure"
            },
            {
                "day": days[6],
                "focus": f_rest,
                "duration": "All Day",
                "intensity": "RPE 1 (Zero exertion)",
                "modality": "Hydration, Muscle Protein Synthesis & Sleep"
            },
        ]

    @classmethod
    def get_default_fitness_plan(
        cls,
        fit_level: str,
        joint_pain: str,
        bmi: float,
        language: str = "English",
        equipment_tier: str = TIER_HOME_ZERO,
        age: int = 30,
        weight_kg: float = 80.0
    ) -> FitnessPlan:
        """Generate structured clinical fitness plan matching user profile, equipment, and language."""
        enforce_protection = cls.should_enforce_joint_protection(joint_pain, bmi)
        lang_lower = str(language).lower()
        eq_lower = str(equipment_tier).lower()

        hr_info = calculate_heart_rate_zones(age)
        target_hr_zone = f"{hr_info['zone2_fatmax']} (Tanaka Zone 2 FatMax)"

        # 1. Precautions Localization
        if "yoruba" in lang_lower:
            precautions_joint = [
                "Kò gbọ́dọ̀ sí fífò rárá: Má ṣe fo jumping jacks, burpees, tàbí skipping rope.",
                "Má ṣe tẹ orúkún ju ìwọ̀n 90 degrees lọ (deep squats).",
                "Má ṣe sáré lórí kọnkéré tàbí tìtì kòtòkòto láti dáàbò bo oríkèé ẹsẹ̀ rẹ.",
                "Dáwọ́ dúró lẹ́sẹ̀kẹsẹ̀ tí orúkún tàbí ẹ̀yìn bá ń dùn ọ́."
            ]
            precautions_std = [
                "Múra dáadáa kí o tó bẹ̀rẹ̀ eré ìdárayá.",
                "Dúró gbañgba kí ẹ̀yìn rẹ má baà tẹ̀.",
                "Dáwọ́ dúró tí o bá ní ìrora kankan."
            ]
            rpe_text = "Ìwọ̀n RPE 4-6 (Kíkankíkan Tí Ó Wà Láàárín - Agbára Láti Sọ̀rọ̀ Láìsí Èémí Sísọ)"
            bio_focus = "Dídáàbò bo orúkún àti ẹ̀yìn láìsí fífò tàbí kíkó ẹrù wúwo lé e lórí."
        elif "igbo" in lang_lower:
            precautions_joint = [
                "Amụla elu rárá: Enweghị jumping jacks ma ọ bụ ịwụ elu (skipping rope).",
                "Ehulatala ikpere karịa ogo iri itoolu (zero deep knee squats).",
                "Agbakwala ọsọ n'ala kọkrịịtị siri ike iji chebe ikpere gị.",
                "Kwụsị mmega ahụ ozugbo ma ọ bụrụ na nkwonkwo na-egbu gị mgbu."
            ]
            precautions_std = [
                "Kpoo ahụ ọkụ tupu i bido mmega ahụ.",
                "Guzo ọtọ ma kwụ ọtọ mgbe niile.",
                "Kwụsị ma ọ bụrụ na ị chọpụta mgbu ọ bụla."
            ]
            rpe_text = "Ọkwa RPE 4-6 (Mmega ahụ na-adịchaghị ike - Ikike ikwu okwu nke ọma)"
            bio_focus = "Nchebe pụrụ iche maka ikpere na azụ n'enweghị mwụli elu ma ọlị."
        elif "hausa" in lang_lower:
            precautions_joint = [
                "Haramcin tsalle: Kada a yi tsalle, burpees ko tsallake igiya.",
                "Kada a durƙusa da zurfi wanda zai matsa gwiwa fiye da kima.",
                "Guji gudu a kan kankare ko kwalta mai tauri.",
                "Tsaya nan take idan ka ji zafi ko ciwo a gwiwa ko baya."
            ]
            precautions_std = [
                "Ɗumama jiki kafin fara motsa jiki.",
                "Tsayar da baya a miƙe yayin kowane motsi.",
                "Tsaya idan ka ji wani zafi maras daɗi."
            ]
            rpe_text = "Ma'aunin RPE 4-6 (Motsa jiki matsakaici - Za ka iya magana ba tare da numfashi ya ɗauke ba)"
            bio_focus = "Kare gwiwoyi da kashin baya ta hanyar guje wa tsalle ko ɗaukar nauyi mai tsanani."
        else:
            precautions_joint = cls.CONTRAINDICATIONS_JOINT_PAIN
            precautions_std = cls.CONTRAINDICATIONS_STANDARD
            rpe_text = "RPE 4-6 / Moderate Exertion (Talk Test: Able to converse in full sentences without gasping)"
            bio_focus = "Patellofemoral and lumbar decompression with zero ballistic joint impact."

        precautions = precautions_joint if enforce_protection else precautions_std

        # 2. Exercise Selection by Equipment Tier & Joint Status
        # Check if Tier is Improvised / Low equipment
        if "improvised" in eq_lower or "bottle" in eq_lower or "keg" in eq_lower or "low" in eq_lower:
            tier_label = cls.TIER_HOME_IMPROVISED
            if enforce_protection:
                if "yoruba" in lang_lower:
                    n1 = "1.5L Water Bottle Shoulder Press (Gbigbe Gọgọrọ Omi 1.5L Soke)"
                    n2 = "Water Keg Chair Squats (Jijoko ati Dide pẹlu Kẹẹgi Omi 5L)"
                    n3 = "Tile Towel Hamstring Glides (Fífà Aṣọ Ìnuwọ́ lórí Táìlì)"
                    n4 = "Two-Hand Keg Supported Row (Gbigbe Kẹẹgi Omi pẹlu Atilẹyin Aga)"
                elif "igbo" in lang_lower:
                    n1 = "1.5L Water Bottle Shoulder Press (Ibulite Karama Mmiri 1.5L n'Elu)"
                    n2 = "Water Keg Chair Squats (Nnọdụ na Nkwụsị na Keg Mmiri 5L)"
                    n3 = "Tile Towel Hamstring Glides (Idọkpụ Akwa n'elu Taịlị)"
                    n4 = "Two-Hand Keg Supported Row (Ikwado n'Oche na Keg Mmiri)"
                elif "hausa" in lang_lower:
                    n1 = "1.5L Water Bottle Shoulder Press (Ɗaga Robar Ruwa ta 1.5L Sama)"
                    n2 = "Water Keg Chair Squats (Zama da Tashi da Jarkar Ruwa ta 5L)"
                    n3 = "Tile Towel Hamstring Glides (Jawo Tawul a kan Fale-falen Ƙasa)"
                    n4 = "Two-Hand Keg Supported Row (Turawa a kan Kujera da Jarkar Ruwa)"
                else:
                    n1 = "1.5L Water Bottle Neutral Overhead Press & Curls"
                    n2 = "4L/5L Water Keg Goblet Chair Sit-to-Stands"
                    n3 = "Smooth Ceramic Tile Towel Hamstring Glides"
                    n4 = "Two-Hand Water Keg Supported Rows (Chair Braced)"

                exercises = [
                    ExerciseItem(
                        name=n1,
                        target_area="Deltoids, Upper Chest, Biceps & Triceps",
                        reps_or_duration="3 sets of 10-12 repetitions",
                        instructions="Hold one filled 1.5L Eva/Nestle water bottle (~1.5kg) in each hand with palms facing inward. Press smoothly overhead without shrugging shoulders. Slowly lower over 3 seconds.",
                        joint_safety_notes="Neutral grip completely decompresses the subacromial space in the shoulder joint.",
                        equipment_needed="Two Filled 1.5L Water Bottles (~1.5kg each)",
                        met_value=3.2,
                        tempo_and_breathing="3-sec descent, 1-sec press. Inhale lowering, exhale pressing overhead."
                    ),
                    ExerciseItem(
                        name=n2,
                        target_area="Gluteus Maximus, Quadriceps & Hip Stabilizers",
                        reps_or_duration="3 sets of 8-10 repetitions (Rest 60s between sets)",
                        instructions="Hold a 4L or 5L water keg firmly against your chest with both hands. Stand an inch in front of a sturdy dining chair. Hinge hips back until glutes lightly tap the chair, then drive through heels to stand.",
                        joint_safety_notes="The chair provides a rigid 90-degree depth stop that stops patellar shear. Goblet holding counterbalances spine.",
                        equipment_needed="One 4L or 5L Water Keg + Sturdy Dining Chair",
                        met_value=4.0,
                        tempo_and_breathing="3-sec controlled descent to chair, 1-sec explosive stand. Inhale down, exhale up."
                    ),
                    ExerciseItem(
                        name=n3,
                        target_area="Hamstrings, Glute Bridge & Deep Core",
                        reps_or_duration="3 sets of 8-10 repetitions",
                        instructions="Lie flat on your back on a mat or rug with heels resting on a folded face towel on smooth ceramic tiles. Lift hips into bridge, slide heels outward smoothly 6-8 inches, then pull back in using hamstrings.",
                        joint_safety_notes="Zero ground reaction shock. Decompresses lower back and strengthens hamstrings without standing knee compression.",
                        equipment_needed="One Small Towel + Smooth Tile Floor",
                        met_value=3.6,
                        tempo_and_breathing="2-sec slide out, 2-sec curl in. Breathe steadily throughout."
                    ),
                    ExerciseItem(
                        name=n4,
                        target_area="Latissimus Dorsi, Rhomboids & Posterior Deltoids",
                        reps_or_duration="3 sets of 10 repetitions per side",
                        instructions="Place left hand and left knee on a sturdy dining chair for firm spinal support. Hold 4L/5L keg in right hand with neutral spine. Pull elbow straight back toward hip, squeeze shoulder blade, and lower slowly.",
                        joint_safety_notes="Bracing on the chair removes 80% of shear strain from the lumbar spine while strengthening postural muscles.",
                        equipment_needed="One 4L/5L Water Keg + Dining Chair",
                        met_value=3.5,
                        tempo_and_breathing="1-sec row pull, 2-sec lower. Inhale lowering, exhale pulling to hip."
                    ),
                ]
            else:
                exercises = [
                    ExerciseItem(
                        name="1.5L Water Bottle Lateral Raises & Overhead Press",
                        target_area="Deltoids & Rotator Cuff Stability",
                        reps_or_duration="3 sets of 12 repetitions",
                        instructions="Stand tall with core engaged. Raise water bottles out to sides to shoulder height, return, then press overhead.",
                        joint_safety_notes="Light domestic load prevents rotator cuff impingement.",
                        equipment_needed="Two 1.5L Water Bottles",
                        met_value=3.8,
                        tempo_and_breathing="2-sec raise, 2-sec lower. Exhale on effort."
                    ),
                    ExerciseItem(
                        name="5L Water Keg Romanian Deadlifts",
                        target_area="Hamstrings, Glutes & Spinal Erectors",
                        reps_or_duration="3 sets of 12 repetitions",
                        instructions="Hold 5L keg with both hands in front of thighs. Soft knee bend, push hips backward until hamstrings stretch, then squeeze glutes to stand.",
                        joint_safety_notes="Hips hinge back while spine remains completely neutral.",
                        equipment_needed="5L Water Keg",
                        met_value=4.5,
                        tempo_and_breathing="3-sec hinge back, 1-sec drive up. Inhale down, exhale stand."
                    ),
                    ExerciseItem(
                        name="Chair Dips & Push-Ups with Feet on Floor",
                        target_area="Triceps, Pectorals & Anterior Deltoids",
                        reps_or_duration="3 sets of 10-12 repetitions",
                        instructions="Place hands on edge of sturdy dining chair, legs extended forward. Lower hips straight down by bending elbows to 90 degrees, press up.",
                        joint_safety_notes="Keep hips close to the chair edge to prevent anterior shoulder capsule strain.",
                        equipment_needed="Sturdy Dining Chair",
                        met_value=4.2,
                        tempo_and_breathing="2-sec descent, 1-sec press. Exhale up."
                    ),
                    ExerciseItem(
                        name="Smooth Tile Towel Mountain Climbers",
                        target_area="Core, Hip Flexors & Low-Impact Aerobics",
                        reps_or_duration="3 sets of 30 seconds continuous",
                        instructions="In high plank position with feet on two towels on ceramic tiles, slide knees forward alternately without jumping.",
                        joint_safety_notes="Continuous glide eliminates foot impact and ankle shock.",
                        equipment_needed="Two Small Towels + Tile Floor",
                        met_value=5.0,
                        tempo_and_breathing="Smooth rhythmic sliding, controlled continuous breathing."
                    ),
                ]

        # Check if Tier is Gym / Fitness Center
        elif "gym" in eq_lower or "fitness center" in eq_lower:
            tier_label = cls.TIER_GYM
            if enforce_protection:
                exercises = [
                    ExerciseItem(
                        name="Seated Chest Press Machine (Joint-Guided)",
                        target_area="Pectorals, Anterior Deltoids & Triceps",
                        reps_or_duration="3 sets of 10-12 repetitions (Light-to-Moderate weight)",
                        instructions="Adjust seat height so handles align with mid-chest. Press outward with smooth control; return without letting weight stack slam.",
                        joint_safety_notes="Fixed machine track prevents shoulder rotator cuff shear and eliminates spinal axial load.",
                        equipment_needed="Seated Chest Press Machine",
                        met_value=3.5,
                        tempo_and_breathing="2-sec push, 3-sec return. Exhale pushing."
                    ),
                    ExerciseItem(
                        name="Horizontal Incline Leg Press (High Foot Placement)",
                        target_area="Gluteus Maximus, Hamstrings & Quads",
                        reps_or_duration="3 sets of 10-12 repetitions",
                        instructions="Position feet high and shoulder-width on footplate. Lower sled until knees bend to 90 degrees max; push through midfoot/heels.",
                        joint_safety_notes="High foot placement significantly reduces patellofemoral knee joint stress compared to barbell squats.",
                        equipment_needed="Horizontal or 45-Degree Leg Press Machine",
                        met_value=4.0,
                        tempo_and_breathing="3-sec descent, 1-sec press. Do not lock knees at top."
                    ),
                    ExerciseItem(
                        name="Seated Cable Rows with Neutral Grip",
                        target_area="Latissimus Dorsi, Rhomboids & Middle Trapezius",
                        reps_or_duration="3 sets of 10-12 repetitions",
                        instructions="Sit tall with chest braced or upright. Pull V-bar attachment toward lower abdomen, squeezing shoulder blades together.",
                        joint_safety_notes="Seated position locks the pelvis and protects lower back from rotational shear.",
                        equipment_needed="Cable Row Machine / Lat Pulldown",
                        met_value=3.8,
                        tempo_and_breathing="1-sec pull, 2-sec return. Inhale forward, exhale rowing."
                    ),
                    ExerciseItem(
                        name="Recumbent Stationary Bike (Zone 2 Cardio)",
                        target_area="Cardiovascular Conditioning & Quadriceps Endurance",
                        reps_or_duration="20-30 minutes at 60-70 RPM",
                        instructions="Maintain a smooth pedal cadence with back fully supported in recumbent bucket seat. Keep HR in Zone 2 FatMax range.",
                        joint_safety_notes="Zero impact on knees, hips, and ankles; backrest fully supports lumbar spine.",
                        equipment_needed="Recumbent Stationary Bike",
                        met_value=4.5,
                        tempo_and_breathing="Steady rhythmic pedaling, breathe in through nose and out through mouth."
                    ),
                ]
            else:
                exercises = [
                    ExerciseItem(
                        name="Cable Lat Pulldowns (Wide-to-Neutral Grip)",
                        target_area="Latissimus Dorsi & Biceps",
                        reps_or_duration="3 sets of 12 repetitions",
                        instructions="Sit secure with thigh pads. Pull bar down toward collarbone, squeeze lats, control the return.",
                        joint_safety_notes="Pulling to upper chest protects cervical spine and rotator cuff.",
                        equipment_needed="Lat Pulldown Machine",
                        met_value=4.5,
                        tempo_and_breathing="1-sec pull, 2-sec return. Exhale down."
                    ),
                    ExerciseItem(
                        name="Dumbbell Goblet Squats to Box/Bench",
                        target_area="Quads, Glutes & Core Stability",
                        reps_or_duration="3 sets of 10-12 repetitions",
                        instructions="Hold moderate dumbbell vertically at chest. Squat down until glutes tap bench, drive through heels.",
                        joint_safety_notes="Bench provides safe depth boundary to protect patellofemoral tracking.",
                        equipment_needed="Dumbbell + Bench",
                        met_value=5.0,
                        tempo_and_breathing="3-sec descent, 1-sec rise. Exhale driving up."
                    ),
                    ExerciseItem(
                        name="Incline Dumbbell Chest Press",
                        target_area="Upper Chest & Triceps",
                        reps_or_duration="3 sets of 10 repetitions",
                        instructions="Set bench to 30-degree incline. Press dumbbells up over chest with neutral-to-pronated grip.",
                        joint_safety_notes="30-degree incline minimizes anterior capsule shoulder impingement.",
                        equipment_needed="Incline Bench + Dumbbells",
                        met_value=4.2,
                        tempo_and_breathing="2-sec lower, 1-sec press. Exhale up."
                    ),
                    ExerciseItem(
                        name="Treadmill Incline Power Walk (Zone 2 Cardio)",
                        target_area="Cardiovascular Capacity & Posterior Chain",
                        reps_or_duration="25-30 minutes (Incline 6-8%, Speed 4.5-5.2 km/h)",
                        instructions="Walk briskly up incline with upright posture without holding handrails if balance permits.",
                        joint_safety_notes="Incline walking doubles caloric burn compared to flat running with zero impact shock on joints.",
                        equipment_needed="Incline Treadmill",
                        met_value=5.5,
                        tempo_and_breathing="Steady nasal breathing, full arm swing."
                    ),
                ]

        # Check if Tier is Outdoor / Neighborhood
        elif "outdoor" in eq_lower or "neighborhood" in eq_lower:
            tier_label = cls.TIER_OUTDOOR
            if enforce_protection:
                exercises = [
                    ExerciseItem(
                        name="Estate Road Flat Walking Loops",
                        target_area="Cardiorespiratory Conditioning & Leg Circulation",
                        reps_or_duration="25-30 minutes continuous (Zone 2 HR Target)",
                        instructions="Walk at a steady, rhythmic pace on flat estate roads or school grounds. Land softly heel-to-toe with natural arm swings.",
                        joint_safety_notes="Avoid uneven gravel or potholes. Cushioned walking shoes absorb ground reaction forces.",
                        equipment_needed="Supportive Walking Shoes",
                        met_value=3.8,
                        tempo_and_breathing="Continuous walking cadence, breathe rhythmically."
                    ),
                    ExerciseItem(
                        name="Park / Estate Bench Sit-to-Stands",
                        target_area="Quadriceps, Glutes & Core Stability",
                        reps_or_duration="3 sets of 10 repetitions",
                        instructions="Stand before a sturdy outdoor park or estate concrete bench. Hinge hips back until lightly seated, then press upright.",
                        joint_safety_notes="Bench stops excessive knee bend and protects patellar tendons.",
                        equipment_needed="Park / Estate Bench",
                        met_value=3.5,
                        tempo_and_breathing="3-sec sit down, 1-sec stand up. Exhale standing."
                    ),
                    ExerciseItem(
                        name="Perimeter Fence / Wall Push-Ups",
                        target_area="Pectorals, Anterior Deltoids & Core Plank",
                        reps_or_duration="3 sets of 10-12 repetitions",
                        instructions="Place hands at shoulder height against estate perimeter fence or wall. Keep body in rigid plank and push back smoothly.",
                        joint_safety_notes="Zero lumbar axial compression and minimal wrist strain.",
                        equipment_needed="Outdoor Wall or Fence",
                        met_value=3.0,
                        tempo_and_breathing="Inhale lowering, exhale pushing away."
                    ),
                    ExerciseItem(
                        name="Curb Heel Raises (Ankle & Calf Stability)",
                        target_area="Gastrocnemius, Soleus & Plantar Fascia",
                        reps_or_duration="3 sets of 15 repetitions",
                        instructions="Stand with balls of feet on street curb or step, holding tree or fence for balance. Raise heels high, pause, lower slowly.",
                        joint_safety_notes="Strengthens ankle stabilizers to prevent knee collapse (valgus).",
                        equipment_needed="Street Curb or Low Step",
                        met_value=3.0,
                        tempo_and_breathing="1-sec lift, 2-sec lower. Breathe smoothly."
                    ),
                ]
            else:
                exercises = [
                    ExerciseItem(
                        name="Outdoor Brisk Interval Walking & Gentle Incline Strides",
                        target_area="Aerobic Capacity & Metabolic Conditioning",
                        reps_or_duration="30-35 minutes (4 min brisk / 1 min faster stride)",
                        instructions="Utilize natural neighborhood gentle inclines for low-impact cardio surges.",
                        joint_safety_notes="Avoid hard sprint foot strikes on hard concrete.",
                        equipment_needed="Running Shoes",
                        met_value=5.0,
                        tempo_and_breathing="Deep diaphragmatic breathing."
                    ),
                    ExerciseItem(
                        name="Park Bench Incline Push-Ups & Tricep Dips",
                        target_area="Chest, Shoulders & Triceps",
                        reps_or_duration="3 sets of 12 repetitions",
                        instructions="Perform push-ups with hands on bench seat, followed by controlled tricep dips.",
                        joint_safety_notes="Elevated bench angle keeps shoulder joints happy.",
                        equipment_needed="Outdoor Bench",
                        met_value=4.2,
                        tempo_and_breathing="Exhale on press."
                    ),
                    ExerciseItem(
                        name="Outdoor Bodyweight Squats on Grass Lawn",
                        target_area="Glutes, Quads & Hamstrings",
                        reps_or_duration="3 sets of 12 repetitions",
                        instructions="Perform parallel air squats on a soft grass surface in an estate park or field.",
                        joint_safety_notes="Soft natural grass provides cushioning underfoot.",
                        equipment_needed="Grassy lawn or field",
                        met_value=4.8,
                        tempo_and_breathing="3-sec down, 1-sec up. Exhale rising."
                    ),
                    ExerciseItem(
                        name="Street Curb Toe Taps & Dynamic Hip Openers",
                        target_area="Cardio Agility & Hip Mobility",
                        reps_or_duration="3 sets of 45 seconds",
                        instructions="Alternately tap toes on street curb with light, rhythmic cadence.",
                        joint_safety_notes="Light forefoot tapping without jumping shock.",
                        equipment_needed="Street Curb",
                        met_value=4.5,
                        tempo_and_breathing="Steady rhythmic breathing."
                    ),
                ]

        # Default fallback: Home (Zero Equipment / Pure Bodyweight)
        else:
            tier_label = cls.TIER_HOME_ZERO
            if enforce_protection:
                if "yoruba" in lang_lower:
                    name_pushup = "Wall Push-Ups (Titẹ Odi Pẹlu Ọwọ)"
                    name_squat = "Chair Squats (Jijoko ati Dide lori Aga)"
                    name_leg = "Seated Knee Lifts (Gbigbe Orúkún Sókè lori Aga)"
                    name_walk = "Flat-Surface Brisk Walking (Ririn lori Ilẹ Tẹju)"
                elif "igbo" in lang_lower:
                    name_pushup = "Wall Push-Ups (Ikwado aka na Mgbidi)"
                    name_squat = "Chair Squats (Nnọdụ na Nkwụsị n'oche)"
                    name_leg = "Seated Knee Lifts (Ibulite Ikpere n'elu Oche)"
                    name_walk = "Flat-Surface Brisk Walking (Ije ije n'ala dị larịị)"
                elif "hausa" in lang_lower:
                    name_pushup = "Wall Push-Ups (Turawa jikin Bango)"
                    name_squat = "Chair Squats (Zama da Tashi a Kujera)"
                    name_leg = "Seated Knee Lifts (Ɗaga Gwiwa a Kujera)"
                    name_walk = "Flat-Surface Brisk Walking (Tafiya a ƙasa mai laushi)"
                else:
                    name_pushup = "Wall Push-Ups"
                    name_squat = "Chair Squats (Sit-to-Stands)"
                    name_leg = "Seated Knee Lifts / Leg Extensions"
                    name_walk = "Flat-Surface Brisk Walking"

                exercises = [
                    ExerciseItem(
                        name=name_pushup,
                        target_area="Chest, Shoulders, Triceps & Core Stability",
                        reps_or_duration="3 sets of 10-12 repetitions",
                        instructions="Stand an arm's length from a sturdy wall. Place palms flat at shoulder height. Inhale and slowly bend elbows until chest is close to the wall; exhale and push back smoothly.",
                        joint_safety_notes="Zero spinal axial load and minimal wrist strain. Ideal upper-body strengthening for joint preservation.",
                        equipment_needed="Flat Wall Space",
                        met_value=3.0,
                        tempo_and_breathing="3-sec descent, 1-sec pause, 1-sec press. Inhale lowering, exhale pressing back."
                    ),
                    ExerciseItem(
                        name=name_squat,
                        target_area="Quadriceps, Glutes & Hamstrings",
                        reps_or_duration="3 sets of 8-10 repetitions (Rest 60s between sets)",
                        instructions="Sit on the edge of a sturdy chair with feet flat, hip-width apart. Lean slightly forward, press through heels to stand upright without using hands if possible. Slowly lower hips back to chair.",
                        joint_safety_notes="The chair provides a definitive depth stop, preventing patellar overloading and hyper-flexion of vulnerable knees.",
                        equipment_needed="Sturdy Dining Chair",
                        met_value=3.5,
                        tempo_and_breathing="3-sec descent to chair, 1-sec pause, 1-sec drive through heels. Inhale down, exhale up."
                    ),
                    ExerciseItem(
                        name=name_leg,
                        target_area="Hip Flexors, Quadriceps & Lower Abdominals",
                        reps_or_duration="2 sets of 12 repetitions per leg",
                        instructions="Sit upright in a chair with hands resting on thighs. Slowly lift right knee towards chest, or straighten right leg outward; hold for 2 seconds at the top, then lower with control.",
                        joint_safety_notes="Completely eliminates ground impact and zero weight is transferred to joints while strengthening knee-supporting muscle groups.",
                        equipment_needed="Sturdy Chair",
                        met_value=2.8,
                        tempo_and_breathing="Hold 2-sec at peak, 2-sec lower. Exhale lifting knee, inhale lowering."
                    ),
                    ExerciseItem(
                        name=name_walk,
                        target_area="Cardiovascular Endurance, Fat Oxidation & Leg Circulation",
                        reps_or_duration="20-30 minutes continuous (or two 15-minute bouts)",
                        instructions="Walk at a pace where you can still speak in full sentences but feel mild exertion. Maintain upright posture with eyes forward and gentle arm swings.",
                        joint_safety_notes="Avoid unpaved, uneven roads or steep hills. Always wear supportive, cushioned footwear to absorb ground reaction forces.",
                        equipment_needed="Supportive Cushioned Shoes",
                        met_value=3.8,
                        tempo_and_breathing="Steady rhythmic breathing, full arm swing."
                    ),
                ]
            else:
                exercises = [
                    ExerciseItem(
                        name="Incline Countertop Push-Ups",
                        target_area="Upper Body & Core Strength",
                        reps_or_duration="3 sets of 12-15 repetitions",
                        instructions="Place hands shoulder-width apart on a sturdy kitchen counter or table. Maintain a rigid plank line and lower chest smoothly.",
                        joint_safety_notes="Controlled angle keeps shoulder joint capsules in an optimal biomechanical groove.",
                        equipment_needed="Kitchen Counter or Table",
                        met_value=3.8,
                        tempo_and_breathing="2-sec lower, 1-sec press. Exhale up."
                    ),
                    ExerciseItem(
                        name="Air Squats to Parallel",
                        target_area="Glutes, Hamstrings & Calves",
                        reps_or_duration="3 sets of 12 repetitions",
                        instructions="Stand tall with feet shoulder-width. Lower hips down and back until thighs are parallel to the floor, then drive through mid-foot to stand.",
                        joint_safety_notes="Keep knees tracking in line with toes; avoid collapsing knees inward (valgus).",
                        equipment_needed="None / Pure Bodyweight",
                        met_value=4.5,
                        tempo_and_breathing="3-sec descent, 1-sec rise. Exhale rising."
                    ),
                    ExerciseItem(
                        name="Glute Bridges",
                        target_area="Gluteus Maximus, Hamstrings & Lumbar Stabilization",
                        reps_or_duration="3 sets of 15 repetitions",
                        instructions="Lie on your back on a mat with knees bent and feet flat. Squeeze glutes and lift hips toward ceiling until thighs and torso align; pause for 2 seconds.",
                        joint_safety_notes="Strengthens the posterior chain to take pressure off the lower back without knee compression.",
                        equipment_needed="Floor Mat or Rug",
                        met_value=3.5,
                        tempo_and_breathing="1-sec lift, 2-sec hold at top, 2-sec lower. Exhale lifting."
                    ),
                    ExerciseItem(
                        name="Brisk Walking / Light Jogging Intervals",
                        target_area="Cardiorespiratory Capacity & Metabolic Rate",
                        reps_or_duration="30 minutes (Alternating 3 min brisk walk / 1 min light jog)",
                        instructions="Maintain cadence and controlled breathing on flat park trails or tracks.",
                        joint_safety_notes="Cushioned running shoes and flat surfaces minimize shin and ankle strain.",
                        equipment_needed="Running Shoes",
                        met_value=6.0,
                        tempo_and_breathing="Continuous controlled breathing."
                    ),
                ]

        # 3. Calculate Session Caloric Burn (average MET * weight * 30 min)
        avg_met = sum(ex.met_value for ex in exercises) / max(len(exercises), 1)
        est_session_calories = calculate_workout_met_burn(weight_kg, avg_met, 30)

        # 4. Step goal
        if enforce_protection:
            step_goal = 5000 if "beginner" in fit_level.lower() else 6500
        else:
            step_goal = 8000 if "active" in fit_level.lower() else 7000

        # 5. Periodized Weekly Microcycle
        weekly_schedule = cls.generate_weekly_periodization(
            fit_level=fit_level,
            equipment_tier=tier_label,
            has_joint_pain=enforce_protection,
            language=language
        )

        return FitnessPlan(
            mobility_level=fit_level,
            has_joint_pain=enforce_protection,
            equipment_tier=tier_label,
            target_heart_rate_zone=target_hr_zone,
            rpe_target=rpe_text,
            est_calories_burned_per_session=est_session_calories,
            joint_precautions=precautions,
            exercises=exercises,
            daily_step_goal=step_goal,
            weekly_schedule=weekly_schedule,
            biomechanical_focus=bio_focus
        )
