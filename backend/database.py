import sqlite3

# Function to initialize the database and create the stats table if it doesn't exist
def init_db():
    connection = sqlite3.connect("cs2_metrics.db")
    cursor = connection.cursor()
    
    # Create the players_stats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            date_analyzed TEXT NOT NULL,
            matches_played INTEGER,
            winrate REAL,
            kdr REAL,
            adr REAL,
            hs_percentage REAL,
            kast_percentage REAL,
            mechanics_rating REAL,
            impact_rating REAL
        )
    """)
    
    connection.commit()
    connection.close()

# Function to save new player metrics into the database
def save_player_stats(data: dict):
    connection = sqlite3.connect("cs2_metrics.db")
    cursor = connection.cursor()
    
    cursor.execute("""
        INSERT INTO players_stats (
            player_id, date_analyzed, matches_played, winrate, 
            kdr, adr, hs_percentage, kast_percentage, 
            mechanics_rating, impact_rating
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["player_id"],
        data["date_analyzed"],
        data["matches_played"],
        data["winrate"],
        data["stats_raw"]["kdr"],
        data["stats_raw"]["adr"],
        data["stats_raw"]["hs_percentage"],
        data["stats_raw"]["kast_percentage"],
        data["ratings"]["mechanics"],
        data["ratings"]["impact"]
    ))
    
    connection.commit()
    connection.close()

    # Function to fetch all historical stats for a specific player from the database
def get_player_history(player_id: str):
    connection = sqlite3.connect("cs2_metrics.db")
    # This line makes SQLite return rows as dictionaries instead of raw tuples
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT * FROM players_stats 
        WHERE player_id = ? 
        ORDER BY id DESC
    """, (player_id,))
    
    rows = cursor.fetchall()
    connection.close()
    
    # Convert database rows into a clean list of dictionaries
    history = [dict(row) for row in rows]
    return history