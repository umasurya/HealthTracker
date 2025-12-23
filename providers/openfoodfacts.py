import requests
from functools import lru_cache

API_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

@lru_cache(maxsize=256)
def search_openfoodfacts(food_name: str):
    """Search OpenFoodFacts and return nutrition info (per 100g) for the best match.

    Returns: dict | None: {'calories': float|None, 'protein': float|None, 'note': str}
    """
    params = {
        'search_terms': food_name,
        'search_simple': 1,
        'action': 'process',
        'json': 1,
        'page_size': 3,
    }
    try:
        resp = requests.get(API_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        products = data.get('products', [])
        if not products:
            return None

        # Pick the first product that has nutriments
        for p in products:
            nutriments = p.get('nutriments', {})
            if not nutriments:
                continue

            # OpenFoodFacts uses different keys; prefer energy-kcal_100g
            calories = nutriments.get('energy-kcal_100g') or nutriments.get('energy_100g')
            protein = nutriments.get('proteins_100g') or nutriments.get('protein_100g')

            # Normalize to floats if possible
            try:
                calories = float(calories) if calories is not None else None
            except Exception:
                calories = None
            try:
                protein = float(protein) if protein is not None else None
            except Exception:
                protein = None

            name = p.get('product_name') or p.get('generic_name') or food_name
            note_parts = []
            if name:
                note_parts.append(name)
            note_parts.append('per 100g')
            return {
                'calories': calories,
                'protein': protein,
                'note': ' - '.join(note_parts)
            }
    except Exception:
        return None

    return None
