"""Comprehensive nutritional database of authentic Nigerian regional staples.

Portion metrics, caloric densities, and clinical modifications are benchmarked against:
FAO/INFOODS West African Food Composition Table (WAFCT) & Federal Ministry of Health (FMOH) Guidelines.
"""

from typing import Dict, List, Any, TypedDict, Optional

WAFCT_CITATION: str = "FAO/INFOODS West African Food Composition Table (WAFCT)"
NUTRITIONAL_BENCHMARK_CITATION: str = (
    "Nutritional benchmarks formulated using the FAO/INFOODS West African Food "
    "Composition Table & FMOH Guidelines."
)


class FoodItem(TypedDict):
    name: str
    local_name: str
    category: str  # "Swallow", "Soup / Vegetable", "Protein", "Legume / Grain", "Side"
    serving_portion: str
    calories_per_portion: int
    protein_g: float
    carbs_g: float
    fat_g: float
    clinical_modifications: str
    key_micronutrients: str


# Regional Food Ground Truth
NIGERIAN_REGIONAL_FOODS: Dict[str, Dict[str, Any]] = {
    "Yoruba": {
        "region_name": "South-West (Yoruba)",
        "description": "Rich in fermented staples, nutrient-dense soups, and legume proteins.",
        "staples": [
            {
                "name": "Amala (Yam / Plantain Flour)",
                "local_name": "Àmàlà (Ìṣu / Ògèdè)",
                "category": "Swallow",
                "serving_portion": "1 clenched-fist wrap (~150g cooked)",
                "calories_per_portion": 165,
                "protein_g": 2.2,
                "carbs_g": 38.5,
                "fat_g": 0.4,
                "clinical_modifications": "Limit strictly to 1 clenched-fist wrap (~150g). Blend unripe plantain flour with yam flour for lower glycemic index.",
                "key_micronutrients": "Dietary fiber, potassium, resistant starch"
            },
            {
                "name": "Ewedu (Jute Leaves)",
                "local_name": "Èwèdù",
                "category": "Soup / Vegetable",
                "serving_portion": "1 deep soup ladle (~120g)",
                "calories_per_portion": 35,
                "protein_g": 2.5,
                "carbs_g": 5.0,
                "fat_g": 0.3,
                "clinical_modifications": "Prepare 100% oil-free. Blend fresh jute leaves; season only with fermented locust beans (iru), ground crayfish, and a pinch of salt.",
                "key_micronutrients": "Vitamins A, C, E, calcium, iron, beta-carotene"
            },
            {
                "name": "Gbegiri (Cowpea Puree Soup)",
                "local_name": "Gbẹ̀gìrì",
                "category": "Soup / Legume",
                "serving_portion": "1 medium ladle (~100g)",
                "calories_per_portion": 95,
                "protein_g": 6.8,
                "carbs_g": 14.5,
                "fat_g": 1.2,
                "clinical_modifications": "Boil brown/honey beans soft and mash through sieve. Use at most 1 teaspoon of unbleached palm oil for color; rely on crayfish for umami.",
                "key_micronutrients": "Plant protein, dietary fiber, folate, magnesium"
            },
            {
                "name": "Efo Riro (Spinach / Shoko / Tete Soup)",
                "local_name": "Ẹ̀fọ́ Ríro",
                "category": "Soup / Vegetable",
                "serving_portion": "1 generous cup (~180g)",
                "calories_per_portion": 110,
                "protein_g": 7.5,
                "carbs_g": 8.0,
                "fat_g": 4.5,
                "clinical_modifications": "Drastically cut palm oil to 1 tablespoon for the whole family pot. Steam shredded greens; bulk with smoked panla fish, crayfish, and tatashe pepper base.",
                "key_micronutrients": "Iron, lutein, folic acid, vitamins K and C"
            },
            {
                "name": "Moimoi (Steamed Bean Pudding)",
                "local_name": "Mọ́ín-mọ́in Ẹlẹ́mí Méje",
                "category": "Protein / Legume",
                "serving_portion": "1 medium banana-leaf wrap (~160g)",
                "calories_per_portion": 170,
                "protein_g": 11.5,
                "carbs_g": 22.0,
                "fat_g": 3.5,
                "clinical_modifications": "Steam in leaves or ramekins with boiled egg/fish pieces. Do not add vegetable oil or margarine to the batter; flavor with onions and red bell peppers.",
                "key_micronutrients": "High bioavailable protein, B vitamins, zinc"
            },
            {
                "name": "Boiled Fish / Lean Goat Meat",
                "local_name": "Ẹja Yíyan / Eran Éwúrẹ́",
                "category": "Protein",
                "serving_portion": "1 palm-sized piece (~120g)",
                "calories_per_portion": 145,
                "protein_g": 24.0,
                "carbs_g": 0.0,
                "fat_g": 4.5,
                "clinical_modifications": "Boil or grill with garlic, ginger, and fresh hot peppers. Discard visible fat; never deep-fry in bleached vegetable oil.",
                "key_micronutrients": "Omega-3 fatty acids, vitamin B12, selenium, iron"
            }
        ]
    },
    "Hausa": {
        "region_name": "Northern (Hausa / Fulani)",
        "description": "Rich in hearty grain swallows, drought-resilient ancient grains, and therapeutic leaf broths.",
        "staples": [
            {
                "name": "Tuwon Shinkafa (Rice Swallow)",
                "local_name": "Tuwon Shinkafa",
                "category": "Swallow",
                "serving_portion": "1 clenched-fist wrap (~150g cooked)",
                "calories_per_portion": 175,
                "protein_g": 3.2,
                "carbs_g": 39.0,
                "fat_g": 0.5,
                "clinical_modifications": "Limit strictly to 1 clenched-fist size. Favor unpolished local brown rice (shinkafa mara goge) for enhanced fiber and blood-sugar regulation.",
                "key_micronutrients": "Manganese, thiamine, selenium"
            },
            {
                "name": "Tuwon Masara (Cornmeal Swallow)",
                "local_name": "Tuwon Masara",
                "category": "Swallow",
                "serving_portion": "1 clenched-fist wrap (~150g cooked)",
                "calories_per_portion": 160,
                "protein_g": 3.5,
                "carbs_g": 35.0,
                "fat_g": 0.8,
                "clinical_modifications": "Prepare from unrefined whole yellow maize flour without adding sugar or butter.",
                "key_micronutrients": "Zeaxanthin, fiber, vitamin B6"
            },
            {
                "name": "Miyan Kuka (Baobab Leaf Soup)",
                "local_name": "Miyan Kuka",
                "category": "Soup / Vegetable",
                "serving_portion": "1 deep soup bowl (~150g)",
                "calories_per_portion": 55,
                "protein_g": 3.8,
                "carbs_g": 8.5,
                "fat_g": 0.5,
                "clinical_modifications": "Prepare oil-free! Whisk sun-dried baobab leaf powder directly into seasoned meat/fish broth with dawadawa (locust beans). Zero added oil required.",
                "key_micronutrients": "High calcium (3x cow milk equivalent), bioavailable iron, potassium, soluble prebiotics"
            },
            {
                "name": "Miyan Zogale (Moringa Leaf Soup)",
                "local_name": "Miyan Zogale",
                "category": "Soup / Vegetable",
                "serving_portion": "1 generous soup bowl (~160g)",
                "calories_per_portion": 75,
                "protein_g": 5.2,
                "carbs_g": 6.5,
                "fat_g": 2.2,
                "clinical_modifications": "Steam tender moringa leaves in tomato-pepper broth. Eliminate groundnut paste; use crushed dried fish and dawadawa for body.",
                "key_micronutrients": "Antioxidants, quercetin, chlorogenic acid, vitamin A"
            },
            {
                "name": "Acha Porridge / Grain (Fonio)",
                "local_name": "Acha (Fonio / Digitaria exilis)",
                "category": "Legume / Grain",
                "serving_portion": "1 small cup cooked (~140g)",
                "calories_per_portion": 140,
                "protein_g": 3.8,
                "carbs_g": 30.0,
                "fat_g": 0.6,
                "clinical_modifications": "Low glycemic index ancient supergrain. Cook with fresh ginger, cloves, and light cinnamon. Do not add condensed milk or refined sugars.",
                "key_micronutrients": "Methionine, cystine, amino acids, low GI index (ideal for diabetes management)"
            },
            {
                "name": "Masa (Fermented Rice Cakes)",
                "local_name": "Waina / Masa",
                "category": "Side",
                "serving_portion": "2 small cakes (~80g)",
                "calories_per_portion": 125,
                "protein_g": 2.4,
                "carbs_g": 24.0,
                "fat_g": 1.5,
                "clinical_modifications": "Pan-sear on a cast-iron pan lightly misted with oil spray rather than deep-frying in groundnut oil.",
                "key_micronutrients": "Probiotic fermented carbohydrates"
            },
            {
                "name": "Boiled Eggs / Skinless Chicken Breast",
                "local_name": "Kwai Da Kaza",
                "category": "Protein",
                "serving_portion": "2 boiled eggs or 1 grilled chicken breast (~120g)",
                "calories_per_portion": 155,
                "protein_g": 26.0,
                "carbs_g": 0.5,
                "fat_g": 5.0,
                "clinical_modifications": "Hard boil eggs or grill skinless chicken seasoned with Yaji (suya spice herbs). Avoid deep-frying chicken in oil.",
                "key_micronutrients": "Complete branch-chain amino acids, choline, zinc"
            }
        ]
    },
    "Igbo": {
        "region_name": "South-East (Igbo)",
        "description": "Celebrated for medicinal wild leaf soups, zero-oil white broths, and mineral-dense seeds.",
        "staples": [
            {
                "name": "Ofe Nsala (White Soup)",
                "local_name": "Ọfe Nsàlà",
                "category": "Soup / Protein Broth",
                "serving_portion": "1 large bowl with fresh catfish (~220g)",
                "calories_per_portion": 135,
                "protein_g": 18.5,
                "carbs_g": 6.0,
                "fat_g": 3.2,
                "clinical_modifications": "Authentic clinical standout: ZERO palm oil required. Season with uziza, uda seeds, Cameroon pepper; thicken minimally with boiled yam or oat flour.",
                "key_micronutrients": "Anti-inflammatory piperine from uziza, omega-3, potassium"
            },
            {
                "name": "Ofe Onugbu (Bitterleaf Soup)",
                "local_name": "Ọfe Ọnụgbụ",
                "category": "Soup / Vegetable",
                "serving_portion": "1 medium bowl (~170g)",
                "calories_per_portion": 120,
                "protein_g": 8.0,
                "carbs_g": 7.5,
                "fat_g": 5.0,
                "clinical_modifications": "Wash bitterleaves thoroughly to moderate bitterness while retaining bioactive vernoniosides. Reduce red palm oil to 1 teaspoon per portion; bulk with dry catfish.",
                "key_micronutrients": "Vernoniosides (hypoglycemic benefits), calcium, iron"
            },
            {
                "name": "Ukwa (African Breadfruit Porridge)",
                "local_name": "Ụkwà (Treculia africana)",
                "category": "Legume / Grain",
                "serving_portion": "1 medium bowl (~160g cooked)",
                "calories_per_portion": 185,
                "protein_g": 10.5,
                "carbs_g": 28.0,
                "fat_g": 3.8,
                "clinical_modifications": "Boil tender with dry fish, dried prawns, scent leaves, and fresh pepper. Cook oil-free without added palm oil or potash.",
                "key_micronutrients": "Plant protein, complex fiber, iron, phosphorus"
            },
            {
                "name": "Okra Soup (Ofe Okwuru)",
                "local_name": "Ọfe Ọkwụrụ",
                "category": "Soup / Vegetable",
                "serving_portion": "1 deep soup bowl (~180g)",
                "calories_per_portion": 65,
                "protein_g": 4.5,
                "carbs_g": 8.0,
                "fat_g": 1.5,
                "clinical_modifications": "Finely dice fresh okra; cook directly in fish stock with scent leaves and ogiri/locust beans. Completely avoid palm oil frying.",
                "key_micronutrients": "Mucilage soluble fiber (blunts postprandial glucose spike), vitamin C"
            },
            {
                "name": "Grilled Mackerel / Stockfish",
                "local_name": "Azu Mackerel / Okporoko",
                "category": "Protein",
                "serving_portion": "1 palm-sized serving (~120g)",
                "calories_per_portion": 160,
                "protein_g": 25.0,
                "carbs_g": 0.0,
                "fat_g": 6.5,
                "clinical_modifications": "Steam stockfish until tender; grill fresh mackerel with dry uziza and chili. No battering or deep frying.",
                "key_micronutrients": "EPA/DHA omega-3 fatty acids, iodine, vitamin D"
            }
        ]
    },
    "South-South": {
        "region_name": "South-South (Niger Delta)",
        "description": "Dominated by fresh river seafood, nutrient-rich broths, and indigenous aromatics.",
        "staples": [
            {
                "name": "Banga Soup (Low-Oil Modified)",
                "local_name": "Banga / Oghwo Amiedi",
                "category": "Soup",
                "serving_portion": "1 small bowl (~140g)",
                "calories_per_portion": 145,
                "protein_g": 8.5,
                "carbs_g": 7.0,
                "fat_g": 8.5,
                "clinical_modifications": "CRITICAL MODIFICATION: Traditional Banga is dangerously high in saturated fats. Skim off all surface floating palm oil before serving; dilute palm base with fish broth and scent leaves.",
                "key_micronutrients": "Beta-carotene, tocotrienols (vitamin E)"
            },
            {
                "name": "Fisherman Soup",
                "local_name": "Fisherman Soup",
                "category": "Soup / Seafood Broth",
                "serving_portion": "1 large bowl with mixed seafood (~240g)",
                "calories_per_portion": 130,
                "protein_g": 23.0,
                "carbs_g": 4.0,
                "fat_g": 2.2,
                "clinical_modifications": "Naturally oil-free! Simmer fresh tilapia/catfish, periwinkles, crabs, and prawns with Cameroon pepper and scent leaves. Thicken with small boiled cocoyam mash.",
                "key_micronutrients": "High lean protein, zinc, copper, omega-3 fatty acids"
            },
            {
                "name": "Owo Soup",
                "local_name": "Owo Soup",
                "category": "Soup",
                "serving_portion": "1 medium bowl (~150g)",
                "calories_per_portion": 110,
                "protein_g": 7.5,
                "carbs_g": 9.0,
                "fat_g": 3.8,
                "clinical_modifications": "Cook with native starch substitute and reduced edible potash; restrict palm oil to 1 teaspoon per portion. Pack with smoked dry fish.",
                "key_micronutrients": "Potassium, calcium"
            },
            {
                "name": "Plantain Porridge with Vegetables",
                "local_name": "Ukodo / Plantain Pottage",
                "category": "Side / Grain",
                "serving_portion": "1 plate (~180g)",
                "calories_per_portion": 175,
                "protein_g": 4.5,
                "carbs_g": 36.0,
                "fat_g": 1.8,
                "clinical_modifications": "Use firm, unripe green plantains; simmer with scent leaves, dry fish, and crayfish. Add zero cooking oil.",
                "key_micronutrients": "Resistant starch, vitamin B6, magnesium"
            }
        ]
    },
    "General Urban": {
        "region_name": "General Urban Nigerian / Pan-African",
        "description": "Accessible, open-market and grocery staples adapted for urban working professionals.",
        "staples": [
            {
                "name": "Boiled Unripe Plantain",
                "local_name": "Boiled Green Plantain",
                "category": "Swallow / Carb",
                "serving_portion": "1 medium plantain sliced (~140g)",
                "calories_per_portion": 150,
                "protein_g": 1.8,
                "carbs_g": 38.0,
                "fat_g": 0.2,
                "clinical_modifications": "Boil in lightly salted water. Excellent replacement for Dodo (fried ripe plantain saves ~250-300 kcal per meal). Pair with vegetable stew.",
                "key_micronutrients": "Resistant starch type 2, potassium"
            },
            {
                "name": "Brown Beans Porridge (Ewa Oloyin)",
                "local_name": "Ẹ̀wà Olóyinjẹ",
                "category": "Legume",
                "serving_portion": "1 medium cup cooked (~170g)",
                "calories_per_portion": 185,
                "protein_g": 12.0,
                "carbs_g": 32.0,
                "fat_g": 1.5,
                "clinical_modifications": "Cook soft with onions, tatase, and crayfish. Limit palm/vegetable oil to 1 teaspoon for the portion.",
                "key_micronutrients": "Dietary fiber, iron, molybdenum, plant protein"
            },
            {
                "name": "Oat Swallow",
                "local_name": "Oatmeal Swallow",
                "category": "Swallow",
                "serving_portion": "1 clenched-fist wrap (~140g cooked)",
                "calories_per_portion": 155,
                "protein_g": 5.0,
                "carbs_g": 29.0,
                "fat_g": 2.2,
                "clinical_modifications": "Blend whole rolled oats into flour; stir into boiling water. Much higher beta-glucan fiber and lower glycemic index than cassava fufu.",
                "key_micronutrients": "Beta-glucan soluble fiber (lowers LDL cholesterol)"
            },
            {
                "name": "Fresh Pepper Soup (Catfish / Goat)",
                "local_name": "Pepper Soup",
                "category": "Soup / Broth",
                "serving_portion": "1 large bowl (~220g)",
                "calories_per_portion": 115,
                "protein_g": 17.5,
                "carbs_g": 2.5,
                "fat_g": 3.5,
                "clinical_modifications": "Oil-free broth made with uda, uziza, scent leaves, and chili. Promotes thermogenesis and metabolic circulation without added fat.",
                "key_micronutrients": "Capsaicin, piperine, bioflavonoids"
            }
        ]
    }
}


def get_regional_foods(culture_input: str) -> Dict[str, Any]:
    """Retrieve structured food profile for a given cultural cuisine string."""
    culture_lower = culture_input.lower()
    if "yoruba" in culture_lower:
        return NIGERIAN_REGIONAL_FOODS["Yoruba"]
    elif "hausa" in culture_lower or "north" in culture_lower:
        return NIGERIAN_REGIONAL_FOODS["Hausa"]
    elif "igbo" in culture_lower or "east" in culture_lower:
        return NIGERIAN_REGIONAL_FOODS["Igbo"]
    elif "south-south" in culture_lower or "banga" in culture_lower or "fisherman" in culture_lower:
        return NIGERIAN_REGIONAL_FOODS["South-South"]
    else:
        return NIGERIAN_REGIONAL_FOODS["General Urban"]


def format_food_ground_truth_for_prompt(culture_input: str) -> str:
    """Format structured regional foods into prompt context with portions and clinical modifications."""
    profile = get_regional_foods(culture_input)
    region_title = profile["region_name"]
    staples: List[FoodItem] = profile["staples"]

    lines = [
        f"AUTHENTIC REGIONAL INGREDIENT GROUND TRUTH ({region_title}):",
        f"Attribution: {WAFCT_CITATION}",
        "Use these verified regional staples with clinical portion and preparation guidelines:"
    ]

    for item in staples:
        lines.append(
            f"- {item['name']} ({item['local_name']}) [{item['category']}]: "
            f"Portion: {item['serving_portion']} (~{item['calories_per_portion']} kcal). "
            f"Clinical Prep: {item['clinical_modifications']}"
        )

    return "\n".join(lines)
