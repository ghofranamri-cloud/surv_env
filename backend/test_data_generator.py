# test_data_generator.py
# Simulates Arduino JSON output directly to database (no WebSocket needed)

import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
import random

from threshold_engine import analyser

DB_PATH = Path(__file__).resolve().parent.parent / "surveillance.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mesures (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT,
            temperature REAL,
            humidite    REAL,
            fumee       INTEGER,
            poussiere   INTEGER,
            son         INTEGER,
            priorite    TEXT
        )
    """)
    conn.commit()
    conn.close()

def inserer(data: dict):
    resultat = analyser(
        data["temperature"],
        data["humidite"],
        data["fumee"],
        data["poussiere"],
        data["son"]
    )
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO mesures
            (timestamp, temperature, humidite, fumee, poussiere, son, priorite)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        data["temperature"],
        data["humidite"],
        data["fumee"],
        data["poussiere"],
        data["son"],
        resultat["priorite"]
    ))
    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"T={data['temperature']:.1f}  H={data['humidite']:.1f}  "
          f"Fumée={data['fumee']}  Poussière={data['poussiere']}  Son={data['son']}  "
          f"→ {resultat['priorite']}")

def generer_donnees_test():
    """Generate realistic test data that varies over time"""
    base_temp = 25.0
    base_hum = 55.0
    
    while True:
        # Add some variation to make it realistic
        temp = base_temp + random.uniform(-2, 3)
        hum = base_hum + random.uniform(-10, 10)
        fumee = random.randint(50, 500)
        pous = random.randint(20, 400)
        son = random.randint(100, 650)
        
        data = {
            "temperature": round(temp, 1),
            "humidite": round(hum, 1),
            "fumee": fumee,
            "poussiere": pous,
            "son": son
        }
        
        inserer(data)
        time.sleep(2)  # Send data every 2 seconds, like the Arduino

if __name__ == "__main__":
    init_db()
    print(f"Database: {DB_PATH}")
    print("Generating test data... (Ctrl+C to stop)")
    try:
        generer_donnees_test()
    except KeyboardInterrupt:
        print("\nStopped.")
