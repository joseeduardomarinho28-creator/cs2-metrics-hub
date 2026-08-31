import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

gc_cookie = os.getenv("GC_COOKIE")

# 1. Define the target URL, player ID, and date
player_id = "2697336"
date = "2026-08"
url = f"https://gamersclub.com.br/api/box/historyFilterDate/{player_id}/{date}"

# 2. Create the "fake badge" (Headers) to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": f"https://gamersclub.com.br/player/{player_id}",
    "Authorization": "Basic ZnJvbnRlbmQ6NDdhMTZHMmtHTCFmNiRMRUQlJVpDI25X",
    "Cookie": gc_cookie
}

# 3. Make the GET request to the API
print(f"Fetching data for player ID {player_id}...")
response = requests.get(url, headers=headers)

# 4. Check if the server allowed us in (Status 200 = OK)
if response.status_code == 200:
    data = response.json()
    print("\n✅ Connection successful!\n")
    
    # 1. Get fixed stats
    total_matches = data["matches"]["matches"]
    wins = data["matches"]["wins"]

    # 2. Create empty variables for the stats inside the list
    kdr = None
    adr = None
    hs_percent = None
    kast_percent = None  # We added this one!

    # 3. Use a Safe Search Loop
    for item in data["stat"]:
        if item["stat"] == "KDR":
            kdr = item["value"]
        elif item["stat"] == "ADR":
            adr = item["value"]
        elif item["stat"] == "HS%":
            hs_percent = item["value"]
        elif item["stat"] == "KAST%":
            kast_percent = item["value"]

    # 3.1 Data Cleaning
    
    kdr_clean = float(kdr)
    adr_clean = float(adr)
    hs_clean = float(hs_percent.replace("%", ""))
    kast_clean = float(kast_percent.replace("%", ""))

    # 4. Math Time: Calculate the Winrate
    winrate = (wins / total_matches) * 100

    winrate = round(winrate, 2)

    # 4. Making a rating calculator

    # 4.1 Normalizing the stats

    kdr_score = min((kdr_clean / 1.7) * 100, 100)
    hs_score = min((hs_clean / 60) * 100, 100)
    adr_score = min((adr_clean / 120) * 100, 100)
    kast_score = min((kast_clean / 80) * 100, 100)

    # 4.2 Creating Mechanics Rating and Impacting Rating
    mechanics_rating = round((hs_score * 0.50) + (kdr_score * 0.25) + (adr_score * 0.25), 2)
    impact_rating = round((kdr_score * 0.40) + (adr_score * 0.40) + (hs_score * 0.20), 2)

    # 5. Print the final results
    print(f"Matches: {total_matches} | Wins: {wins} | Winrate: {winrate}%")
    print(f"KDR: {kdr} | ADR: {adr} | HS: {hs_percent} | KAST: {kast_percent}")
    print(f"🎯 Mechanics Rating: {mechanics_rating}/100")
    print(f"💥 Impact Rating: {impact_rating}/100")

else:
    print(f"\n❌ Connection failed. Status code: {response.status_code}")