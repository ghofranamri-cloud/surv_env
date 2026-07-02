#  Surveillance Environnementale 

Système de surveillance en temps réel pour les conditions environnementales d'une usine de câblage automobile.

##  Vue d'ensemble

Ce projet démontre une architecture complète de **monitoring embarqué** :
- **Simulation Wokwi** : Circuit Arduino avec 5 capteurs virtuels
- **Backend Python** : Logique de seuils + base de données SQLite
- **Dashboard Streamlit** : Visualisation temps réel + alertes

##  Fonctionnalités

✅ Mesure en temps réel :
- Température (DHT22)
- Humidité (DHT22)
- Fumée/Gaz (MQ-2)
- Poussière (simulée)
- Niveau sonore (simulé)

✅ Système d'alertes multi-niveaux (LOW / MEDIUM / HIGH / CRITICAL)
✅ LED strip NeoPixel pour visualisation d'état
✅ Dashboard Streamlit interactif avec graphiques Plotly
✅ Base de données SQLite pour historique

##  Architecture
Wokwi (Simulation Arduino)
↓ RFC2217
Python Reader + Threshold Engine
↓
SQLite Database
↓
Streamlit Dashboard
##  Installation

### 1. Prérequis
- Python 3.8+
- VS Code avec Wokwi Extension
- Git

### 2. Cloner le repo
```bash
git clone https://github.com/ton_username/surv_env.git
cd surv_env
```

### 3. Installer les dépendances
```bash
cd backend
pip install -r requirements.txt
```

### 4. Lancer la simulation
- VS Code : `Ctrl+Shift+P` → `Wokwi: Start Simulator`

### 5. Lancer le reader RFC2217
```bash
python rfc2217_reader.py
```

### 6. Lancer le dashboard
```bash
python -m streamlit run dashboard_app.py
```

##  Fichiers principaux

- `src/main.cpp` : Code Arduino (lecture capteurs + envoi JSON)
- `backend/threshold_engine.py` : Logique de seuils
- `backend/dashboard_app.py` : Dashboard Streamlit
- `backend/rfc2217_reader.py` : Pont Arduino → Python
- `wokwi.toml` : Configuration Wokwi RFC2217
- `diagram.json` : Schéma du circuit

##  Seuils par défaut

| Capteur | LOW | MEDIUM | HIGH | CRITICAL |
|---------|-----|--------|------|----------|
| Température | < 34°C | 34-40°C | - | ≥ 40°C |
| Humidité | < 68% | 68-80% | - | ≥ 80% |
| Fumée | < 300 | 300-400 | - | ≥ 400 |
| Poussière | < 450 | 450-600 | - | ≥ 600 |
| Son | < 560 | 560-700 | - | ≥ 700 |

##  Objectif

Projet de stage — 1ère année cycle ingénieur, spécialisation systèmes infotroniques.

##  Licence

MIT License - voir LICENSE file

##  Auteur

Ghofran Amri — Yura Corporation Tunisia (Stage 2025)

---

**Pour plus d'infos :** consulte la documentation dans `/docs`
