import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.nutrition_repo import insert_food
from db.connection import get_nutrition_db

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.citygross.se/matvaror/veckans-erbjudande",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

FOODS_TO_SEARCH = [
    "kycklingfile", "ris", "ägg", "lax",
    "havregryn", "banan", "mjölk"
]

def fetch_products(query):
    url = f"https://www.citygross.se/api/v1/Loop54/search/quick/?SearchQuery={query}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Skipping '{query}', status {response.status_code}")
        return []
    return response.json().get("searchResults", {}).get("products", [])

def extract_nutrients(product):
    nutrients_list = product.get("foodAndBeverageExtension", {}).get("nutrientInformations", [])
    if not nutrients_list:
        return None
    raw = nutrients_list[0].get("nutrients")
    if not raw:
        return None
    return {n["typeCode"]: n["value"] for n in raw}

def food_exists(name, brand):
    with get_nutrition_db() as conn:
        row = conn.execute("""
            SELECT id FROM foods WHERE LOWER(name) = ? AND LOWER(brand) = ?
        """, (name.lower(), brand.lower())).fetchone()
        return row is not None

def run_scraper():
    saved = 0
    skipped = 0

    for query in FOODS_TO_SEARCH:
        products = fetch_products(query)

        for product in products[:3]:
            name = product.get("name", "")
            brand = product.get("brand", "")

            if not name or not brand:
                skipped += 1
                continue

            if food_exists(name, brand):
                print(f"Skipping duplicate: {name} ({brand})")
                skipped += 1
                continue

            nutrients = extract_nutrients(product)
            if not nutrients:
                skipped += 1
                continue

            calories = nutrients.get("ENER-", 0)
            protein  = nutrients.get("PRO-", 0)
            carbs    = nutrients.get("CHOAVL", 0)
            fat      = nutrients.get("FAT", 0)

            insert_food(name, brand, calories, protein, carbs, fat)
            print(f"Saved: {name} ({brand})")
            saved += 1

    print(f"\nDone! Saved: {saved}, Skipped: {skipped}")

if __name__ == "__main__":
    run_scraper()