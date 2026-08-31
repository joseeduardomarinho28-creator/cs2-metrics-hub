from fastapi import FastAPI, HTTPException
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, save_player_stats, get_player_history

# Load environment variables and initialize the FastAPI app
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gc_cookie = os.getenv("GC_COOKIE")

init_db()

@app.get("/")
def read_root():
    # Returning a welcome JSON
    return {"message": "Welcome to the CS2 Metrics Hub API!", "status": "Online"}

# NEW ROUTE: Get all historical stats for a player from our database
@app.get("/api/history/{player_id}") # (ou @app.get, dependendo de como está o seu)
def get_history(player_id: str):
    history_data = get_player_history(player_id)
    
    if not history_data:
        raise HTTPException(status_code=404, detail="No history found for this player")
        
    return {
        "player_id": player_id,
        "total_records": len(history_data),
        "history": history_data
    }

# 1. Updated endpoint to require both player_id AND date
@app.get("/api/player/{player_id}/{date}")
def get_player_stats(player_id: str, date: str):
    
    # The target URL discovered through reverse engineering
    url = f"https://gamersclub.com.br/api/box/historyFilterDate/{player_id}/{date}"
    
    # Create the "fake badge" (Headers) to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://gamersclub.com.br/player/{player_id}",
        "Authorization": "Basic ZnJvbnRlbmQ6NDdhMTZHMmtHTCFmNiRMRUQlJVpDI25X",
        "Cookie": gc_cookie
    }

    # Make the GET request to the Gamers Club API
    response = requests.get(url, headers=headers)

    # If Gamers Club returns an error, we return a 404 Not Found status
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Player not found or Gamers Club error")

    data = response.json()
    
    # 2. Get fixed stats
    total_matches = data["matches"]["matches"]
    wins = data["matches"]["wins"]
    
    # 3. Create empty variables for the stats inside the list
    kdr = None
    adr = None
    hs_percent = None
    kast_percent = None

    # 4. Use a Safe Search Loop
    for item in data["stat"]:
        if item["stat"] == "KDR":
            kdr = item["value"]
        elif item["stat"] == "ADR":
            adr = item["value"]
        elif item["stat"] == "HS%":
            hs_percent = item["value"]
        elif item["stat"] == "KAST%":
            kast_percent = item["value"]

    # 5. Data cleaning
    kdr_clean = float(kdr)
    adr_clean = float(adr)
    hs_clean = float(hs_percent.replace("%", ""))
    kast_clean = float(kast_percent.replace("%", ""))

    # 6. Calculate the Winrate
    winrate = round((wins / total_matches) * 100, 2)

    # 7. Making a rating calculator
    
    # 7.1 Normalizing the stats
    kdr_score = min((kdr_clean / 1.7) * 100, 100)
    hs_score = min((hs_clean / 60) * 100, 100)
    adr_score = min((adr_clean / 120) * 100, 100)
    kast_score = min((kast_clean / 80) * 100, 100)

    # 7.2 Creating Mechanics Rating and Impact Rating
    mechanics_rating = round((hs_score * 0.50) + (kdr_score * 0.25) + (adr_score * 0.25), 2)
    impact_rating = round((kdr_score * 0.40) + (adr_score * 0.40) + (hs_score * 0.20), 2)

    # 8. Pack the result into a clean dictionary
    result = {
        "player_id": player_id,
        "date_analyzed": date,
        "matches_played": total_matches,
        "winrate": winrate,
        "stats_raw": {
            "kdr": kdr_clean,
            "adr": adr_clean,
            "hs_percentage": hs_clean,
            "kast_percentage": kast_clean
        },
        "ratings": {
            "mechanics": mechanics_rating,
            "impact": impact_rating
        }
    }

    save_player_stats(result)

    return result
    