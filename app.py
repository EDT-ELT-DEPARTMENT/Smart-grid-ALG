import streamlit as st
import sqlite3
import pandas as pd
import time
import random
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="SONELGAZ - Supervision Temps Réel", layout="wide")

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('monitoring_energie.db')
    c = conn.cursor()
    # Table unique pour stocker les mesures des deux flux
    c.execute('''CREATE TABLE IF NOT EXISTS mesures 
                 (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- TITRE ---
st.title("Système de Supervision Énergétique - SONELGAZ")
st.subheader("Client : Mr MILOUA Farid | ID : 7314P001114")

# --- FONCTION DE SIMULATION D'ENTRÉE (Pour tester votre TTGO) ---
def add_simulated_data():
    conn = sqlite3.connect('monitoring_energie.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Simuler électricité (kW) et gaz (m3)
    c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?)", (now, "Elec", random.uniform(1.2, 3.5), random.uniform(50, 60)))
    c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?)", (now, "Gaz", random.uniform(0.5, 1.2), random.uniform(10, 15)))
    conn.commit()
    conn.close()

# --- INTERFACE DE MONITORING ---
col1, col2 = st.columns(2)

# Bouton pour forcer une mise à jour (simulation)
if st.button("Rafraîchir les données Live"):
    add_simulated_data()

# Récupération des dernières données
conn = sqlite3.connect('monitoring_energie.db')
df = pd.read_sql_query("SELECT * FROM mesures ORDER BY timestamp DESC LIMIT 20", conn)
conn.close()

if not df.empty:
    elec_data = df[df['type_energie'] == 'Elec'].iloc[0]
    gaz_data = df[df['type_energie'] == 'Gaz'].iloc[0]

    # --- SECTION ÉLECTRICITÉ (Bleu) ---
    with col1:
        st.markdown("<h2 style='color: #2980b9;'>⚡ Électricité (Temps Réel)</h2>", unsafe_allow_html=True)
        st.metric(label="Consommation Instantanée", value=f"{elec_data['valeur_actuelle']:.2f} kW")
        st.metric(label="Cumul Journalier", value=f"{elec_data['total_jour']:.2f} kWh")
        
        # Graphique Elec
        chart_data_elec = df[df['type_energie'] == 'Elec'].set_index('timestamp')['valeur_actuelle']
        st.line_chart(chart_data_elec)

    # --- SECTION GAZ (Orange) ---
    with col2:
        st.markdown("<h2 style='color: #e67e22;'>🔥 Gaz (Temps Réel)</h2>", unsafe_allow_html=True)
        st.metric(label="Débit Instantané", value=f"{gaz_data['valeur_actuelle']:.2f} m³/h")
        st.metric(label="Cumul Journalier", value=f"{gaz_data['total_jour']:.2f} m³")
        
        # Graphique Gaz
        chart_data_gaz = df[df['type_energie'] == 'Gaz'].set_index('timestamp')['valeur_actuelle']
        st.line_chart(chart_data_gaz)

    # --- DÉTAIL DES TRANCHES (Logique métier SONELGAZ) ---
    st.divider()
    st.subheader("État des Tranches de Consommation")
    
    # Simulation de calcul de tranche
    col_t1, col_t2, col_t3 = st.columns(3)
    
    # Tranche 1 (0-125)
    t1_prog = min((elec_data['total_jour'] / 125.0) * 100, 100)
    col_t1.progress(t1_prog / 100, text=f"Tranche 1 (125 kWh) : {t1_prog:.1f}%")
    
    # Tranche 2 (125-250)
    t2_prog = min(max(((elec_data['total_jour'] - 125) / 125.0) * 100, 0), 100) if elec_data['total_jour'] > 125 else 0
    col_t2.progress(t2_prog / 100, text=f"Tranche 2 (125 kWh) : {t2_prog:.1f}%")
    
    # Tranche 3 (> 250)
    t3_prog = max(((elec_data['total_jour'] - 250) / 1000) * 100, 0) if elec_data['total_jour'] > 250 else 0
    col_t3.progress(min(t3_prog / 100, 1.0), text=f"Tranche 3 (Supp) : {t3_prog:.1f}%")

else:
    st.info("En attente de données de la carte TTGO ESP32...")
    if st.button("Initialiser avec des données fictives"):
        add_simulated_data()
        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("Système de monitoring actif. Assurez-vous que votre ESP32 est configuré pour POSTer vers l'API de réception.")
