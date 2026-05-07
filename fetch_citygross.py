import requests
import sqlite3

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.citygross.se/matvaror/veckans-erbjudande",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

conn = sqlite3.connect("nutrition.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY,
    name TEXT,
    brand TEXT,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL
)
""")

foods_to_search = ["kycklingfile", "ris", "ägg", "lax", "havregryn", "banan", "mjölk"]

for food in foods_to_search:
    url = f"https://www.citygross.se/api/v1/Loop54/search/quick/?SearchQuery={food}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Skipping {food}, status {response.status_code}")
        continue

    products = response.json().get("searchResults", {}).get("products", [])

    for product in products[:3]:
        name = product.get("name", "")
        brand = product.get("brand", "")
        nutrients_list = product.get("foodAndBeverageExtension", {}).get("nutrientInformations", [])

        if not nutrients_list:
            continue

        raw_nutrients = nutrients_list[0].get("nutrients")
        if not raw_nutrients:
            continue

        nutrients = {n["typeCode"]: n["value"] for n in raw_nutrients}

        calories = nutrients.get("ENER-", 0)
        protein = nutrients.get("PRO-", 0)
        carbs = nutrients.get("CHOAVL", 0)
        fat = nutrients.get("FAT", 0)

        cursor.execute("INSERT INTO foods VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                       (name, brand, calories, protein, carbs, fat))
        print(f"Saved: {name} ({brand})")

conn.commit()
conn.close()
print("Done!")