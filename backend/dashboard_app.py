import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path
from threshold_engine import analyser, generer_alertes

DB_PATH = Path(__file__).resolve().parent.parent / "surveillance.db"


# CONFIG PAGE

st.set_page_config(
    page_title="Surveillance Yura Corp",
    page_icon="🏭",
    layout="wide"
)


# CHARGEMENT DONNÉES

def charger_donnees():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('''
        SELECT * FROM mesures
        ORDER BY id DESC
        LIMIT 100
    ''', conn)
    conn.close()
    return df


# COULEURS PRIORITÉ

COULEURS_PRIORITE = {
    "LOW":      "🟢",
    "MEDIUM":   "🟡",
    "HIGH":     "🟠",
    "CRITICAL": "🔴"
}


# INTERFACE

st.title(" Surveillance Environnementale — Yura Corporation")
st.caption(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')} | Base de données : {DB_PATH}")
# Bouton refresh
if st.button("🔄 Actualiser"):
    st.rerun()

# Auto-refresh toutes les 5 secondes
st.markdown("""
<script>
setTimeout(function() {
    window.location.reload();
}, 5000);
</script>
""", unsafe_allow_html=True)


# CHARGEMENT

df = charger_donnees()

if df.empty:
    st.warning(
        f"⚠️ Aucune donnée disponible.\n\n"
        f"Assurez-vous que :\n"
        f"1. La simulation Wokwi est en cours d'exécution\n"
        f"2. `python backend/serial_reader.py` est lancé\n\n"
        f"Base de données : {DB_PATH}"
    )
    st.stop()

# Dernière mesure
derniere = df.iloc[0]


# LIGNE 1 — MÉTRIQUES EN TEMPS RÉEL

st.subheader(" Valeurs en temps réel")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta_t = f"{derniere['temperature'] - df['temperature'].mean():.1f}°C"
    st.metric(" Température", f"{derniere['temperature']:.1f} °C", delta_t)

with col2:
    delta_h = f"{derniere['humidite'] - df['humidite'].mean():.1f}%"
    st.metric(" Humidité", f"{derniere['humidite']:.1f} %", delta_h)

with col3:
    st.metric(" Fumée", f"{int(derniere['fumee'])}",
              f"seuil: 400")

with col4:
    st.metric(" Poussière", f"{int(derniere['poussiere'])}",
              f"seuil: 600")

with col5:
    st.metric(" Son", f"{int(derniere['son'])}",
              f"seuil: 700")

st.divider()


# LIGNE 2 — ÉTAT GLOBAL

priorite = derniere['priorite']
emoji    = COULEURS_PRIORITE.get(priorite, "⚪")

col_etat, col_alertes = st.columns([1, 2])

with col_etat:
    st.subheader(" État global")
    if priorite == "CRITICAL":
        st.error(f"{emoji} CRITIQUE — Intervention immédiate !")
    elif priorite == "HIGH":
        st.warning(f"{emoji} ÉLEVÉ — Surveiller de près")
    elif priorite == "MEDIUM":
        st.info(f"{emoji} MODÉRÉ — Attention requise")
    else:
        st.success(f"{emoji} NORMAL — Tout va bien")

with col_alertes:
    st.subheader(" Alertes actives")
    resultat = analyser(
        derniere['temperature'],
        derniere['humidite'],
        int(derniere['fumee']),
        int(derniere['poussiere']),
        int(derniere['son'])
    )
    alertes = generer_alertes(resultat['etats'])

    if alertes:
        for a in alertes:
            niveau = a['niveau']
            if niveau == "CRITICAL":
                st.error(f" {a['message']}")
            elif niveau == "HIGH":
                st.warning(f" {a['message']}")
            else:
                st.info(f" {a['message']}")
    else:
        st.success(" Aucune alerte — environnement sain")

st.divider()


# LIGNE 3 — GRAPHIQUES

st.subheader("📈 Historique des mesures")

# Inverser pour avoir chronologique
df_chrono = df.iloc[::-1].reset_index(drop=True)

tab1, tab2, tab3 = st.tabs([" Température & Humidité",
                             " Fumée & Poussière",
                             " Son"])

with tab1:
    fig = px.line(df_chrono, y=["temperature", "humidite"],
                  title="Température (°C) et Humidité (%)",
                  color_discrete_map={
                      "temperature": "#FF6B6B",
                      "humidite":    "#4ECDC4"
                  })
    fig.add_hline(y=40, line_dash="dash",
                  line_color="red",   annotation_text="Seuil Temp")
    fig.add_hline(y=80, line_dash="dash",
                  line_color="blue",  annotation_text="Seuil Hum")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.line(df_chrono, y=["fumee", "poussiere"],
                   title="Fumée et Poussière (valeur analogique)",
                   color_discrete_map={
                       "fumee":     "#FF9F43",
                       "poussiere": "#A29BFE"
                   })
    fig2.add_hline(y=400, line_dash="dash",
                   line_color="orange", annotation_text="Seuil Fumée")
    fig2.add_hline(y=600, line_dash="dash",
                   line_color="purple", annotation_text="Seuil Poussière")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.line(df_chrono, y="son",
                   title="Niveau sonore (analogique)",
                   color_discrete_sequence=["#54A0FF"])
    fig3.add_hline(y=700, line_dash="dash",
                   line_color="darkblue", annotation_text="Seuil Son")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()


# LIGNE 4 — RÉPARTITION DES PRIORITÉS

st.subheader(" Répartition des niveaux de priorité (100 dernières mesures)")

col_pie, col_table = st.columns([1, 2])

with col_pie:
    repartition = df['priorite'].value_counts().reset_index()
    repartition.columns = ["priorite", "count"]
    fig_pie = px.pie(
        repartition, names="priorite", values="count",
        title="Distribution des priorités",
        color="priorite",
        color_discrete_map={
            "LOW": "#2ECC71",
            "MEDIUM": "#F1C40F",
            "HIGH": "#E67E22",
            "CRITICAL": "#E74C3C"
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_table:
    st.markdown("**🗂️ Dernières mesures enregistrées**")
    df_affiche = df_chrono.copy()
    df_affiche["priorite"] = df_affiche["priorite"].apply(
        lambda p: f"{COULEURS_PRIORITE.get(p, '⚪')} {p}"
    )
    st.dataframe(
        df_affiche.tail(15).iloc[::-1],
        use_container_width=True,
        hide_index=True
    )

st.divider()


# PIED DE PAGE

st.caption(
    f"Surveillance Yura Corporation • {len(df)} mesures chargées • "
    f"Rafraîchissement automatique toutes les 5 secondes\n"
    f"📂 Base de données : `{DB_PATH}`"
)