import streamlit as st
import sqlite3
import pandas as pd
import random
import time
from datetime import datetime
import streamlit.components.v1 as components
from xhtml2pdf import pisa
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA", layout="wide")

# --- TITRE DE LA PLATEFORME ---
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    
    for client_id in ["7314P001114", "7314P001115", "7314P001116"]:
        c.execute("SELECT COUNT(*) FROM mesures WHERE client_id=?", (client_id,))
        if c.fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", 0.0, 562.00, client_id))
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", 0.0, 2708.40, client_id))
    
    conn.commit()
    conn.close()

init_db()

# --- FONCTIONS ---
def calculer_facture(conso_elec, conso_gaz):
    e1 = min(conso_elec, 125.0)
    e2 = max(0, min(conso_elec - 125.0, 125.0))
    e3 = max(0, conso_elec - 250.0)
    data_elec = [
        {"tranche": "Tranche 1", "qte": e1, "prix": 1.7787, "mt": e1 * 1.7787},
        {"tranche": "Tranche 2", "qte": e2, "prix": 4.1789, "mt": e2 * 4.1789},
        {"tranche": "Tranche 3", "qte": e3, "prix": 4.8120, "mt": e3 * 4.8120}
    ]
    # Gaz reste identique
    g1 = min(conso_gaz, 1125.0)
    g2 = max(0, min(conso_gaz - 1125.0, 1375.0))
    g3 = max(0, conso_gaz - 2500.0)
    data_gaz = [
        {"tranche": "Tranche 1", "qte": g1, "prix": 0.1682, "mt": g1 * 0.1682},
        {"tranche": "Tranche 2", "qte": g2, "prix": 0.3245, "mt": g2 * 0.3245},
        {"tranche": "Tranche 3", "qte": g3, "prix": 0.4025, "mt": g3 * 0.4025}
    ]
    return data_elec, data_gaz

def get_db_value(client_id, type_energie):
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    query = "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(type_energie, client_id))
    conn.close()
    return float(df['total_jour'].iloc[0]) if not df.empty else 0.0

# --- NAVIGATION ---
CLIENTS = {
    "7314P001114": {"nom": "MME BELASKRI ASMA", "facture": "733260603359", "lieu": "01 BLOC B CT 70 LOGTS UDL"},
    "7314P001115": {"nom": "Client B", "facture": "733260603360", "lieu": "CITE 120 LOGTS BAT A"},
    "7314P001116": {"nom": "Client C", "facture": "733260603361", "lieu": "VILLA N°45 ZONE 02"}
}

st.sidebar.title("Navigation")
selected_id = st.sidebar.selectbox("Choisir un abonné :", list(CLIENTS.keys()))
mode_acquisition = st.sidebar.radio("Mode d'acquisition :", ["Mode Simulation", "Mode Réel (Carte TTGO)"])
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- PAGE SUPERVISION CORRIGÉE ---
def page_supervision(client_id, info):
    st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA : Supervision")
    
    if 'auto_sim' not in st.session_state: st.session_state.auto_sim = False

    # Mode Simulation
    if mode_acquisition == "Mode Simulation":
        st.info("🔧 **Mode Simulation** : Comptage additif dynamique.")
        st.session_state.auto_sim = st.toggle("Activer la simulation automatique", st.session_state.auto_sim)
        
        if st.session_state.auto_sim:
            # 1. Lire la valeur actuelle depuis la DB (pour éviter le cache)
            current_elec = get_db_value(client_id, "Elec")
            current_gaz = get_db_value(client_id, "Gaz")
            
            # 2. Calculer l'incrément
            inc_elec = random.uniform(0.5, 1.0)
            inc_gaz = inc_elec * 0.2
            new_elec = current_elec + inc_elec
            new_gaz = current_gaz + inc_gaz
            
            # 3. Écrire dans la DB
            conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
            c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", inc_elec, new_elec, client_id))
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", inc_gaz, new_gaz, client_id))
            conn.commit()
            conn.close()
            
            time.sleep(1) 
            st.rerun() # Force le rechargement immédiat
            
    # --- AFFICHAGE ---
    # Lecture fraîche des données pour l'affichage
    last_elec = get_db_value(client_id, "Elec")
    last_gaz = get_db_value(client_id, "Gaz")
    
    data_elec, _ = calculer_facture(last_elec, last_gaz)

    st.markdown(f"### ⚡ Consommation Électricité (Total: {last_elec:.2f} kWh)")
    cols_e = st.columns(3)
    for i, tranche in enumerate(data_elec):
        limit = 125 if i==0 else 125 if i==1 else 1000
        cols_e[i].metric(tranche['tranche'], f"{tranche['qte']:.2f} kWh")
        cols_e[i].progress(min(tranche['qte'] / limit, 1.0))
        
    st.divider()
    st.subheader("Historique")
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM mesures WHERE client_id=? ORDER BY timestamp DESC LIMIT 20", conn, params=(client_id,))
    conn.close()
    st.line_chart(df[df['type_energie'] == 'Elec'].set_index('timestamp')['total_jour'])

if page == "Supervision Temps Réel":
    page_supervision(selected_id, CLIENTS[selected_id])
