
# SEUILS 

SEUILS = {
    "temperature": {"low": 30.0, "medium": 35.0, "high": 40.0},
    "humidite":    {"low": 60.0, "medium": 70.0, "high": 80.0},
    "fumee":       {"low": 200,  "medium": 300,  "high": 400 },
    "poussiere":   {"low": 300,  "medium": 450,  "high": 600 },
    "son":         {"low": 400,  "medium": 550,  "high": 700 }
}


# ÉVALUATION D'UN CAPTEUR retourne LOW/MEDIUM/HIGH/CRITICAL

def evaluer_capteur(nom, valeur):
    s = SEUILS[nom]

    if valeur >= s["high"]:
        return "CRITICAL"
    elif valeur >= s["medium"]:
        return "HIGH"
    elif valeur >= s["low"]:
        return "MEDIUM"
    else:
        return "LOW"

# ============================================================
# PRIORITÉ GLOBALE → le pire capteur dicte l'état global
# ============================================================
PRIORITE = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

def priorite_globale(etats):
    pire = "LOW"
    for etat in etats.values():
        if PRIORITE[etat] > PRIORITE[pire]:
            pire = etat
    return pire

# ============================================================
# FONCTION PRINCIPALE D'ANALYSE
# ============================================================
def analyser(temp, hum, fumee, pous, son):

    etats = {
        "temperature": evaluer_capteur("temperature", temp),
        "humidite":    evaluer_capteur("humidite",    hum),
        "fumee":       evaluer_capteur("fumee",       fumee),
        "poussiere":   evaluer_capteur("poussiere",   pous),
        "son":         evaluer_capteur("son",         son)
    }

    global_priority = priorite_globale(etats)

    return {
        "etats":    etats,
        "priorite": global_priority
    }


# MESSAGES D'ALERTE PAR CAPTEUR

MESSAGES = {
    "temperature": {
        "MEDIUM":   "Température élevée — surveiller",
        "HIGH":     "Température dangereuse — ventiler",
        "CRITICAL": " SURCHAUFFE — évacuer la zone !"
    },
    "humidite": {
        "MEDIUM":   "Humidité importante",
        "HIGH":     "Humidité très élevée — risque matériel",
        "CRITICAL": " Humidité critique !"
    },
    "fumee": {
        "MEDIUM":   "Légère présence de fumée",
        "HIGH":     "Fumée détectée — vérifier machines",
        "CRITICAL": " FUMÉE CRITIQUE — alarme incendie !"
    },
    "poussiere": {
        "MEDIUM":   "Taux de poussière modéré",
        "HIGH":     "Poussière élevée — porter masque",
        "CRITICAL": " Pollution air critique !"
    },
    "son": {
        "MEDIUM":   "Niveau sonore élevé",
        "HIGH":     "Bruit excessif — protections auditives",
        "CRITICAL": " Bruit dangereux — norme dépassée !"
    }
}

def generer_alertes(etats):
    alertes = []
    for capteur, etat in etats.items():
        if etat != "LOW":
            msg = MESSAGES[capteur].get(etat, "")
            if msg:
                alertes.append({
                    "capteur":  capteur,
                    "niveau":   etat,
                    "message":  msg
                })
    return alertes