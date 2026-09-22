"""Nutrition Agent for FitNaija+.

Contains deep domain knowledge of regional African cuisines, clinical portion control,
and healthy traditional cooking modifications for preventative health:
- Yoruba, Hausa/Northern, Igbo/South-East, South-South, and Urban Nigerian cuisines.
- Portion rules: The clenched fist rule for swallows, palm rule for lean proteins.
- Preparation guides: Cutting palm/groundnut oil, boiling over frying, bulking with un-oiled greens.
"""

from typing import Dict, List, Any
from src.schemas.models import MealItem, NutritionPlan
from src.data.nigerian_foods import (
    format_food_ground_truth_for_prompt,
    WAFCT_CITATION,
    NUTRITIONAL_BENCHMARK_CITATION,
)


class NutritionAgent:
    """Agent specializing in localized African nutrition and portion architecture."""

    # Culinary database mapping regions to staple ingredients and clinical modifications
    CUISINE_PROFILES: Dict[str, Dict[str, Any]] = {
        "Yoruba": {
            "staples": ["Amala (Yam Flour)", "Ewedu", "Gbegiri", "Efo Riro", "Moimoi", "Boiled Unripe Plantain", "Grilled Mackerel"],
            "swallows": ["Amala (Ishe)", "Eba (Yellow/White Garri)", "Pounded Yam (Iyan - Occasional)"],
            "healthy_soups": ["Ewedu (completely oil-free with iru & crayfish)", "Gbegiri (stewed brown bean broth, low oil)", "Efo Riro (vegetables bulked with tatashe and smoked fish, 1 tbsp oil max)"],
            "oil_reduction_guide": "Prepare Ewedu 100% oil-free with locust beans (iru) and ground crayfish. Limit red palm oil in Efo Riro to at most 1 tablespoon for an entire pot.",
            "boiling_vs_frying": "Replace fried plantain (Dodo) with boiled unripe or semi-ripe plantain. Steam Moimoi with eggs and fish rather than deep-frying Akara."
        },
        "Hausa": {
            "staples": ["Tuwon Shinkafa", "Miyan Kuka", "Miyan Zogale (Moringa)", "Acha (Fonio)", "Masa (Fermented Rice)", "Danwake", "Suya (Lean, Grilled)"],
            "swallows": ["Tuwon Shinkafa", "Tuwon Masara (Corn)", "Tuwon Acha"],
            "healthy_soups": ["Miyan Kuka (Baobab leaf powder packed with calcium/fiber, oil-free)", "Miyan Zogale (Moringa leaves steamed with smoked fish)", "Miyan Kubewa (Okra soup)"],
            "oil_reduction_guide": "Avoid adding groundnut paste or groundnut oil to Miyan Kuka. Use baobab leaf powder and dried ground catfish for rich, creamy consistency.",
            "boiling_vs_frying": "Choose whole grain Acha porridge or boiled sweet potato over fried masa. Grill lean beef or chicken suya without brushing with saturated oils."
        },
        "Igbo": {
            "staples": ["Ofe Nsala (White Soup)", "Ofe Onugbu (Bitterleaf)", "Ukwa (African Breadfruit)", "Ofe Okra", "Ofe Owerri", "Smoked Catfish", "Boiled Cocoyam"],
            "swallows": ["Oat Swallow", "Utara Akpu (Cassava Fufu - controlled)", "Garri (Eba)"],
            "healthy_soups": ["Ofe Nsala (Zero palm oil soup flavored with uziza and uda seeds)", "Ofe Okra (Freshly sliced okra bulked with scent leaves and dried prawns)", "Ofe Onugbu (Well-washed bitterleaf with minimal oil)"],
            "oil_reduction_guide": "Prioritize Ofe Nsala—it is an authentic Nigerian white soup that requires ZERO palm oil. Season with medicinal spices (Uziza, Uda, Cameroon pepper).",
            "boiling_vs_frying": "Prepare Ukwa as a soft, comforting porridge with dry fish rather than frying. Boil fresh fish instead of deep-frying."
        },
        "South-South": {
            "staples": ["Fisherman Soup", "Banga Soup (Low Oil)", "Owo Soup", "Roasted Plantain (Bole)", "River Fresh Fish", "Periwinkle", "Crab"],
            "swallows": ["Starch (limited)", "Garri", "Pounded Yam (small portion)"],
            "healthy_soups": ["Fisherman Soup (seafood broth with fresh fish, prawns, scent leaves, zero oil)", "Banga Soup (skimmed of top layer oil)", "Native Soup with waterleaves"],
            "oil_reduction_guide": "Fisherman soup is naturally virtually oil-free and loaded with omega-3s. If consuming Banga soup, skim the floating oil off the surface and limit soup volume.",
            "boiling_vs_frying": "Enjoy Bole (charcoal-roasted plantain) paired with grilled fish and fresh vegetable salsa instead of oily palm sauces."
        },
        "General Urban": {
            "staples": ["Brown Beans Porridge", "Boiled Plantain", "Grilled Tilapia / Mackerel", "Oat Swallow", "Steamed Cabbage Stew", "Boiled Eggs"],
            "swallows": ["Oatmeal swallow", "Lafun", "Garri"],
            "healthy_soups": ["Vegetable Soup (Efo / Spinach with diced pepper sauce)", "Plain Okra Soup with grilled fish"],
            "oil_reduction_guide": "Cook stew by oven-roasting or boiling peppers and tomatoes before blending, adding only 1 teaspoon of olive or vegetable oil.",
            "boiling_vs_frying": "Steam or boil sweet potatoes, yams, and beans. Avoid deep-fried proteins like fried turkey or fried stew meats."
        }
    }

    # Universal clinical portion and preparation rules
    PORTION_RULES: List[str] = [
        "1 Clenched Fist Rule: Never exceed 1 clenched fist size (~150g-180g) for heavy swallows (Amala, Tuwon Shinkafa, Eba, Pounded Yam).",
        "1 Palm Rule for Proteins: Every meal should contain a palm-sized portion of lean protein (grilled fish, skinless chicken, 2 boiled eggs, or moimoi).",
        "Half-Plate Rule for Greens: Fill at least 50% of your plate with un-oiled vegetable soups or greens (Ewedu, Okra, Kuka, Zogale, or Efo).",
        "Hydration Pre-load: Drink 1 full glass of water (300-400ml) 15 minutes before every meal to promote satiety and digestion."
    ]

    PREPARATION_GUIDES: List[str] = [
        "Oil Sparing: Drastically reduce palm oil and groundnut oil to a maximum of 1 tablespoon for an entire family pot (or 1 teaspoon per portion).",
        "Boil/Grill over Fry: Strictly avoid deep-frying; grill or air-fry fish and chicken; boil plantain rather than frying Dodo.",
        "Un-Oiled Greens Bulking: Bulk soups with zero-oil draws like Ewedu, shredded Okra, or Miyan Kuka to provide fiber and volume.",
        "Natural Sodium Substitutes: Cut bouillon cubes (Maggi/Knorr) in half; amplify flavor using Iru (locust beans), Ogiri, ground crayfish, Uziza seeds, and garlic."
    ]

    @classmethod
    def get_cuisine_key(cls, cuisine_selection: str) -> str:
        """Map user selection string to cuisine profile key."""
        cuisine_sel = cuisine_selection.lower()
        if "yoruba" in cuisine_sel:
            return "Yoruba"
        elif "hausa" in cuisine_sel or "north" in cuisine_sel:
            return "Hausa"
        elif "igbo" in cuisine_sel or "east" in cuisine_sel:
            return "Igbo"
        elif "south-south" in cuisine_sel or "banga" in cuisine_sel:
            return "South-South"
        else:
            return "General Urban"

    @classmethod
    def generate_nutrition_prompt(
        cls,
        cuisine_selection: str,
        budget_tier: str,
        target_calories: int,
        water_target_liters: float,
        language: str = "English"
    ) -> str:
        """Construct detailed clinical nutrition instructions for the AI model."""
        cuisine_key = cls.get_cuisine_key(cuisine_selection)
        profile = cls.CUISINE_PROFILES.get(cuisine_key, cls.CUISINE_PROFILES["General Urban"])
        ground_truth_context = format_food_ground_truth_for_prompt(cuisine_selection)

        return f"""
        NUTRITION CLINICAL DIRECTIVE:
        - Target Calorie Ceiling: ~{target_calories} kcal/day
        - Daily Hydration Target: {water_target_liters} Liters
        - Cultural Cuisine Focus: {cuisine_selection} ({cuisine_key} culinary heritage)
        - Budget Archetype: {budget_tier}
        - Target Language: {language}
        - Clinical Reference Standard: {WAFCT_CITATION}

        {ground_truth_context}

        MANDATORY AFRICAN PORTION & PREPARATION PROTOCOLS:
        1. THE SWALLOW FIST RULE: Swallows like {', '.join(profile['swallows'])} MUST be limited strictly to 1 clenched fist size (~150g cooked).
        2. THE PROTEIN PALM RULE: Recommend palm-sized lean proteins (~120g, e.g. boiled/grilled fish, skinless poultry, moimoi, or eggs).
        3. OIL RESTRICTION: {profile['oil_reduction_guide']} Limit oil strictly to 1-2 teaspoons per portion or 1 tablespoon per family pot.
        4. COOKING METHODOLOGY: {profile['boiling_vs_frying']}
        5. SOUP BULKING: Feature authentic soups like {', '.join(profile['healthy_soups'])}, showing how to prepare them cleanly without heavy oil layers.
        6. FLAVOR WITHOUT CHEMICAL SODIUM: Advocate using locust beans (iru/dawadawa), ground crayfish, and traditional herbs over heavy bouillon seasoning.
        """


    @classmethod
    def get_default_nutrition_plan(
        cls,
        cuisine_selection: str,
        target_calories: int,
        water_liters: float,
        language: str = "English"
    ) -> NutritionPlan:
        """Provide structured nutrition plan matching user culture and language."""
        cuisine_key = cls.get_cuisine_key(cuisine_selection)
        profile = cls.CUISINE_PROFILES.get(cuisine_key, cls.CUISINE_PROFILES["General Urban"])
        lang_lower = str(language).lower()

        # Localized meal timing labels
        if "yoruba" in lang_lower:
            m_breakfast, m_lunch, m_dinner = "Oúnjẹ Àárọ̀ (Breakfast)", "Oúnjẹ Ọ̀sán (Lunch)", "Oúnjẹ Àlẹ́ (Dinner)"
            portion_rules = [
                "Ìwọ̀n Ẹ̀ṣẹ́ Ọwọ́ Kan: Má ṣe jẹ oúnjẹ òkèlè (Àmàlà, Tuwo, Ẹ̀bà) tí ó ju ẹ̀ṣẹ́ ọwọ́ rẹ kan lọ (~150g).",
                "Ìwọ̀n Àtẹ́lẹwọ́ fún Protein: Ẹja tàbí ẹran tí kò lárá tó ìwọ̀n àtẹ́lẹwọ́ rẹ.",
                "Àbọ̀ Àwo fún Ewébẹ̀: Kún 50% àwo rẹ pẹ̀lú Èwèdù tàbí Ọbẹ̀ Ilá tí kò ní epo púpọ̀.",
                "Omi Mímu: Mu ife omi kan ní ìṣẹ́jú mẹ́ẹ̀ẹ́dógún kí o tó jẹun."
            ]
            prep_rules = [
                "Dín epo kù: Ṣíbí kan péré fún gbogbo ìkòkò ọbẹ̀.",
                "Sise dípò Dídín: Se oúnjẹ tàbí kí o yan ẹja/ẹran dípò dídín.",
                "Ewébẹ̀ láìsí epo: Se Èwèdù àti Ọbẹ̀ Ilá pẹ̀lú irú àti edé láìfi epo sí i.",
                "Dín iyọ̀ àti maggi kù: Lo irú àti edé fún adùn àbínibí."
            ]
        elif "igbo" in lang_lower:
            m_breakfast, m_lunch, m_dinner = "Nri Ụtụtụ (Breakfast)", "Nri Ehihie (Lunch)", "Nri Abalị (Dinner)"
            portion_rules = [
                "Iwu Ọkpọ Aka: Ejila nri elo (Amala, Akpụ, Eba) karịrị otu ọkpọ aka gị (~150g).",
                "Iwu Ọbụ Aka maka Protein: Azụ ma ọ bụ anụ ruru nha ọbụ aka gị.",
                "Ọkara Efere maka Akwụkwọ Nri: Wụsa 50% efere gị ofe na-enweghị mmanụ dịka Ofe Nsala ma ọ bụ Okra.",
                "Mmiri Ọñụñụ: Ñụọ iko mmiri tupu i rie nri ọ bụla."
            ]
            prep_rules = [
                "Ibelata mmanụ: Otu ngaji mmanụ nri maka ofe dum.",
                "Isi nri n'ọkụ kama ighe eghe: Sie ma ọ bụ yuo azụ/anụ n'ọkụ.",
                "Ofe na-enweghị mmanụ: Ofe Nsala na Okra na-enweghị mmanụ nkwụ dị ukwuu.",
                "Ibelata maggi na nnu: Jiri ogiri, iru, na azụ kpọrọ nkụ maka ezigbo ụtọ."
            ]
        elif "hausa" in lang_lower:
            m_breakfast, m_lunch, m_dinner = "Karin Kumallo (Breakfast)", "Abincin Rana (Lunch)", "Abincin Dare (Dinner)"
            portion_rules = [
                "Dokar Dunkulen Hannu: Kada tuwon shinkafa ko masara ya wuce dunkulen hannunka ɗaya (~150g).",
                "Dokar Tafin Hannu: Kifi ko nama mai girman tafin hannu.",
                "Rabin Faranti na Ganye: Cika 50% na farantinka da Miyan Kuka ko Miyan Zogale maras mai.",
                "Shan Ruwa: Sha kofi ɗaya na ruwa kafin kowane abinci."
            ]
            prep_rules = [
                "Rage mai: Cokali ɗaya kacal na mai a kowace tukunyar miya.",
                "Dafawa maimakon soyawa: Dafa ko gasa kifi/nama maimakon soya shi.",
                "Ganye ba tare da mai ba: Miyan Kuka da Miyan Zogale tare da daddawa.",
                "Rage gishiri da maggi: Yi amfani da daddawa da busasshen kifi don ɗanɗano."
            ]
        else:
            m_breakfast, m_lunch, m_dinner = "Breakfast", "Lunch", "Dinner"
            portion_rules = cls.PORTION_RULES
            prep_rules = cls.PREPARATION_GUIDES

        # Create structured sample meals based on culture
        if cuisine_key == "Yoruba":
            meals = [
                MealItem(
                    meal_time=m_breakfast,
                    dish="Moimoi Elemi Meje with Boiled Egg",
                    portion_guide="1 medium wrap of steamed Moimoi + 1 boiled egg",
                    cooking_instructions="Steam with onions, tatase, and crayfish. Add zero vegetable oil to batter.",
                    approx_calories=int(target_calories * 0.25)
                ),
                MealItem(
                    meal_time=m_lunch,
                    dish="Amala with Oil-Free Ewedu, Gbegiri & Grilled Mackerel",
                    portion_guide="1 clenched fist of Amala (150g) + 1 palm of grilled fish + generous Ewedu",
                    cooking_instructions="Prepare Ewedu 100% oil-free with iru (locust beans) and crayfish. Gbegiri cooked light.",
                    approx_calories=int(target_calories * 0.40)
                ),
                MealItem(
                    meal_time=m_dinner,
                    dish="Boiled Unripe Plantain & Light Efo Riro",
                    portion_guide="1 small boiled unripe plantain (sliced) + half plate vegetable soup",
                    cooking_instructions="Cook Efo with only 1 teaspoon palm oil, smoked panla fish, and peppers.",
                    approx_calories=int(target_calories * 0.35)
                )
            ]
        elif cuisine_key == "Hausa":
            meals = [
                MealItem(
                    meal_time=m_breakfast,
                    dish="Acha (Fonio) Porridge with Boiled Eggs",
                    portion_guide="1 small bowl cooked Acha + 2 boiled eggs",
                    cooking_instructions="Boil Acha with fresh ginger, cloves, and minimal milk; no refined sugar.",
                    approx_calories=int(target_calories * 0.25)
                ),
                MealItem(
                    meal_time=m_lunch,
                    dish="Tuwon Shinkafa with Oil-Free Miyan Kuka & Lean Beef",
                    portion_guide="1 clenched fist of Tuwon Shinkafa (brown rice preferred) + palm-sized lean beef",
                    cooking_instructions="Miyan Kuka prepared with baobab leaf powder, dried catfish, dawadawa, no groundnut oil.",
                    approx_calories=int(target_calories * 0.40)
                ),
                MealItem(
                    meal_time=m_dinner,
                    dish="Miyan Zogale (Moringa Soup) with Steamed Fish",
                    portion_guide="1 bowl of vegetable-heavy moringa soup + palm of steamed tilapia",
                    cooking_instructions="Steam moringa leaves in tomato-pepper broth with crayfish; no heavy groundnut paste.",
                    approx_calories=int(target_calories * 0.35)
                )
            ]
        elif cuisine_key == "Igbo":
            meals = [
                MealItem(
                    meal_time=m_breakfast,
                    dish="Ukwa (African Breadfruit Porridge) with Dry Fish",
                    portion_guide="1 medium bowl of Ukwa porridge + shredded dry fish",
                    cooking_instructions="Boil soft with potash substitute/potassium, uziza seeds, dry fish, and no palm oil.",
                    approx_calories=int(target_calories * 0.30)
                ),
                MealItem(
                    meal_time=m_lunch,
                    dish="Ofe Nsala (Authentic White Soup) with Oat Swallow",
                    portion_guide="1 clenched fist of Oat Swallow + 1 large fresh catfish steak in Nsala broth",
                    cooking_instructions="Authentic white soup: ZERO palm oil. Season with uziza, uda, and pepper; thicken lightly.",
                    approx_calories=int(target_calories * 0.40)
                ),
                MealItem(
                    meal_time=m_dinner,
                    dish="Ofe Okra with Fresh Prawns & Snails",
                    portion_guide="Large bowl of chunky sliced okra soup + lean seafood",
                    cooking_instructions="Quick-boil okra in seafood stock with scent leaves and dry crayfish; no palm oil added.",
                    approx_calories=int(target_calories * 0.30)
                )
            ]
        elif cuisine_key == "South-South":
            meals = [
                MealItem(
                    meal_time=m_breakfast,
                    dish="Boiled Plantain & Garden Egg Sauce",
                    portion_guide="1 medium boiled plantain + 1 cup garden egg sauce with smoked fish",
                    cooking_instructions="Crush boiled garden eggs into pepper stock with 1 tsp oil, smoked fish, and scent leaves.",
                    approx_calories=int(target_calories * 0.28)
                ),
                MealItem(
                    meal_time=m_lunch,
                    dish="Fisherman Soup with Light Swallow",
                    portion_guide="1 small fist of swallow + rich bowl of fresh fish, periwinkle, and crab in herbal broth",
                    cooking_instructions="Simmer fresh seafood in native herbs, peppers, and scent leaves. Zero oil required.",
                    approx_calories=int(target_calories * 0.42)
                ),
                MealItem(
                    meal_time=m_dinner,
                    dish="Grilled Catfish / Tilapia with Steamed Native Watergreens",
                    portion_guide="1 whole palm-sized grilled fish + large side of steamed greens",
                    cooking_instructions="Season fish with Cameroon pepper, ginger, and garlic; grill over open grates.",
                    approx_calories=int(target_calories * 0.30)
                )
            ]
        else:
            meals = [
                MealItem(
                    meal_time=m_breakfast,
                    dish="Brown Beans Porridge with Steamed Fish",
                    portion_guide="1 small plate brown beans + palm of steamed or grilled fish",
                    cooking_instructions="Boil beans with onions and peppers; limit oil to 1 teaspoon for flavor.",
                    approx_calories=int(target_calories * 0.30)
                ),
                MealItem(
                    meal_time=m_lunch,
                    dish="Oat Swallow with Fresh Okra & Grilled Mackerel",
                    portion_guide="1 clenched fist of Oat swallow + palm of grilled fish + hearty okra",
                    cooking_instructions="Prepare okra with crayfish, iru, and peppers; zero bleached vegetable oil.",
                    approx_calories=int(target_calories * 0.40)
                ),
                MealItem(
                    meal_time=m_dinner,
                    dish="Vegetable Medley with Grilled Chicken Breast",
                    portion_guide="1 palm skinless grilled chicken + generous sautéed cabbage/spinach",
                    cooking_instructions="Stir-steam greens with garlic and ginger; avoid frying in oil.",
                    approx_calories=int(target_calories * 0.30)
                )
            ]

        return NutritionPlan(
            daily_calorie_target=target_calories,
            water_liters=water_liters,
            benchmark_citation=NUTRITIONAL_BENCHMARK_CITATION,
            swallow_portion_rules=portion_rules,
            oil_and_cooking_rules=prep_rules,
            meals=meals,
            foods_to_embrace=[
                "Ewedu (Jute Leaves) - Oil-free draw soup rich in vitamins A & C",
                "Okra - Low calorie, gelatinous fiber slows carb absorption",
                "Iru / Dawadawa (Locust Beans) - Fermented probiotic with umami flavor",
                "Miyan Kuka (Baobab Leaf Powder) - High bioavailable calcium and iron",
                "Acha (Fonio) - Ancient low-glycemic African whole grain",
                "Grilled Mackerel / Tilapia - Heart-healthy omega-3 fatty acids"
            ],
            foods_to_minimize=[
                "Bleached palm oil or groundnut oil poured generously into soups",
                "Dodo (deep-fried ripe plantain) - Absorbs up to 300 kcal of oil per serving",
                "Excessive Maggi / Knorr cubes - Excess sodium exacerbates hypertension",
                "Oversized swallow portions (>1 clenched fist)",
                "Fried meats and chicken skin cooked in reused oil"
            ]
        )

