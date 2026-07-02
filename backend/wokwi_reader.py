
# Reads JSON output directly from Wokwi simulation serial output

import json
import sqlite3
import serial
import time
from datetime import datetime
from pathlib import Path

from threshold_engine import analyser

DB_PATH = Path(__file__).resolve().parent.parent / "surveillance.db"
RFC2217_URL = "rfc2217://localhost:4000"

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

def main():
    init_db()

    print(f"Attempting to connect to {RFC2217_URL} at 9600 baud...")
    print(f"Database: {DB_PATH}\n")

    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            ser = serial.serial_for_url(RFC2217_URL, baudrate=9600, timeout=2)
            print(f"✓ Connected to {RFC2217_URL}")
            retry_count = 0

            while True:
                try:
                    ligne = ser.readline().decode('utf-8').strip()
                    if not ligne:
                        continue

                    try:
                        data = json.loads(ligne)
                        if all(k in data for k in ("temperature", "humidite", "fumee", "poussiere", "son")):
                            inserer(data)
                        else:
                            print(f"[WARN] Missing keys in JSON: {ligne}")
                    except json.JSONDecodeError:
                        pass

                except Exception as e:
                    print(f"Error reading line: {e}")
                    break

        except serial.SerialException as e:
            retry_count += 1
            print(f"✗ Connection failed: {e}")
            if retry_count < max_retries:
                print(f"Retrying in 3 seconds... (attempt {retry_count}/{max_retries})")
                time.sleep(3)
            else:
                print("Max retries reached. Check that Wokwi is running and that RFC2217 bridging is enabled.")
                break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
