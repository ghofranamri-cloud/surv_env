# serial_reader.py
import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import websockets  # pip install websockets

from threshold_engine import analyser

DB_PATH = Path(__file__).resolve().parent.parent / "surveillance.db"

# ── Wokwi WebSocket URL ────────────────────────────────────────────────────────
# In VS Code + PlatformIO: run the simulation, then check the Wokwi terminal
# for the WebSocket port (usually ws://localhost:9012)
WOKWI_WS = "ws://localhost:9012"

# ── DB setup ──────────────────────────────────────────────────────────────────
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
          f"→ {resultat['priorite']}")

# ── Main loop ─────────────────────────────────────────────────────────────────
async def lire():
    """Connect to Wokwi WebSocket and consume Serial output."""
    print(f"Connexion à {WOKWI_WS} …")
    async with websockets.connect(WOKWI_WS) as ws:
        async for message in ws:
            try:
                data = json.loads(message)
                # Expected Arduino JSON: {"temperature":25.3,"humidite":60,"fumee":150,"poussiere":200,"son":300}
                if all(k in data for k in ("temperature","humidite","fumee","poussiere","son")):
                    inserer(data)
            except json.JSONDecodeError:
                pass  # ignore non-JSON lines (debug prints, etc.)

if __name__ == "__main__":
    init_db()
    asyncio.run(lire())