# main.py
import serial
import sqlite3
from datetime import datetime
from threshold_engine import analyser, generer_alertes

PORT = "COM3"
BAUD = 9600

# Couleurs console
COULEURS = {
    "LOW":      "\033[92m",   # vert
    "MEDIUM":   "\033[93m",   # jaune
    "HIGH":     "\033[91m",   # rouge clair
    "CRITICAL": "\033[41m",   # fond rouge
    "RESET":    "\033[0m"
}

def creer_base():
    conn = sqlite3.connect("surveillance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mesures (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        horodatage  TEXT,
        temperature REAL,
        humidite    REAL,
        fumee       INTEGER,
        poussiere   INTEGER,
        son         INTEGER,
        priorite    TEXT
    )''')
    conn.commit()
    return conn

def enregistrer(conn, temp, hum, fumee, pous, son, priorite):
    conn.execute('''INSERT INTO mesures
        (horodatage, temperature, humidite, fumee, poussiere, son, priorite)
        VALUES (?,?,?,?,?,?,?)''',
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         temp, hum, fumee, pous, son, priorite))
    conn.commit()

def main():
    conn = creer_base()
    ser  = serial.Serial(PORT, BAUD, timeout=2)
    print("✅ Connecté. En écoute...\n")

    while True:
        ligne = ser.readline().decode('utf-8').strip()
        if not ligne:
            continue

        try:
            temp, hum, fumee, pous, son, _ = ligne.split(",")
            temp  = float(temp)
            hum   = float(hum)
            fumee = int(fumee)
            pous  = int(pous)
            son   = int(son)

            # === Threshold Engine ===
            resultat = analyser(temp, hum, fumee, pous, son)
            alertes  = generer_alertes(resultat["etats"])
            priorite = resultat["priorite"]

            # === Affichage console ===
            couleur = COULEURS[priorite]
            reset   = COULEURS["RESET"]
            print(f"{couleur}[{priorite}]{reset} "
                  f"T={temp}°C | H={hum}% | "
                  f"Fumée={fumee} | Pous={pous} | Son={son}")

            for alerte in alertes:
                print(f"  ⚠️  {alerte['message']}")

            # === Sauvegarde SQLite ===
            enregistrer(conn, temp, hum, fumee, pous, son, priorite)

        except (ValueError, IndexError):
            pass

if __name__ == "__main__":
    main()