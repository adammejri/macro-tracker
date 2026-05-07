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

SEARCH_TERMS = [
    "kyckling", "nötkött", "fläsk", "lax", "torsk", "räkor",
    "ägg", "mjölk", "yoghurt", "kvarg", "cottage cheese",
    "havregryn", "pasta", "ris", "bröd", "potatis",
    "broccoli", "spenat", "tomat", "gurka", "lök",
    "banan", "äpple", "apelsin",
    "smör", "olivolja", "mandel", "jordnötssmör",
    "proteinpulver", "makrill", "tonfisk"
]

def fetch_products(query, page=0, page_size=10):
    url = (
        f"https://www.citygross.se/api/v1/Loop54/search/quick/"
        f"?SearchQuery={query}&PageSize={page_size}&Page={page}"
    )
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Skipping '{query}' page {page}, status {response.status_code}")
        return [], 0

    data = response.json().get("searchResults", {})
    products = data.get("products", [])
    total = data.get("totalCount", 0)
    return products, total

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

def process_product(product, seen_this_run):
    name  = (product.get("name") or "").strip()
    brand = (product.get("brand") or "").strip()

    if not name or not brand:
        return False, "missing name or brand"

    key = (name.lower(), brand.lower())
    if key in seen_this_run:
        return False, "duplicate"

    if food_exists(name, brand):
        return False, "duplicate"

    nutrients = extract_nutrients(product)
    if not nutrients:
        return False, "no nutrients"

    calories = nutrients.get("ENER-", 0)
    protein  = nutrients.get("PRO-", 0)
    carbs    = nutrients.get("CHOAVL", 0)
    fat      = nutrients.get("FAT", 0)

    insert_food(name, brand, calories, protein, carbs, fat)
    seen_this_run.add(key)
    return True, f"saved {name} ({brand})"

def run_scraper(max_per_query=30):
    total_saved   = 0
    total_skipped = 0
    seen_this_run = set()

    for query in SEARCH_TERMS:
        print(f"\nScraping: '{query}'")
        page = 0
        page_size = 10
        query_saved = 0

        while query_saved < max_per_query:
            products, total_count = fetch_products(query, page, page_size)

            if not products:
                break

            for product in products:
                if query_saved >= max_per_query:
                    break
                success, msg = process_product(product, seen_this_run)
                if success:
                    print(f"  ✓ {msg}")
                    query_saved  += 1
                    total_saved  += 1
                else:
                    total_skipped += 1

            if (page + 1) * page_size >= total_count:
                break

            page += 1

        print(f"  Saved {query_saved} from '{query}'")

    print(f"\n{'='*40}")
    print(f"Total saved:   {total_saved}")
    print(f"Total skipped: {total_skipped}")

if __name__ == "__main__":
    run_scraper(max_per_query=30)