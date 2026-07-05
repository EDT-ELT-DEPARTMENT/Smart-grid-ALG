import streamlit as st
import sqlite3
import pandas as pd
import random
import io
import requests
from datetime import datetime
from xhtml2pdf import pisa
import streamlit.components.v1 as components

# --- TITRE INSTITUTIONNEL CONSTANT ---
TITRE_INSTITUTIONNEL = "Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA"

# --- CONFIGURATION ---
st.set_page_config(page_title="Smart-Grid SONELGAZ", layout="wide")

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    
    # Init client principal
    c.execute("SELECT COUNT(*) FROM mesures WHERE client_id='7314P001114'")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", 0.0, 562.00, "7314P001114"))
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", 0.0, 2708.40, "7314P001114"))
    
    conn.commit()
    conn.close()

init_db()

# --- CONFIGURATION CLIENTS ---
CLIENTS = {
    "7314P001114": {"nom": "MME BELASKRI ASMA", "facture": "733260603359", "lieu": "01 BLOC B CT 70 LOGTS UDL"},
    "7314P001115": {"nom": "Client B", "facture": "733260603360", "lieu": "CITE 120 LOGTS BAT A"},
    "7314P001116": {"nom": "Client C", "facture": "733260603361", "lieu": "VILLA N°45 ZONE 02"}
}

# --- FONCTIONS ---
def get_live_data(client_id, type_energie):
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    query = "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(type_energie, client_id))
    conn.close()
    return df['total_jour'].iloc[0] if not df.empty else 0.0

def calculer_facture(conso_elec, conso_gaz):
    # Logique de calcul
    data_elec = [
        {"tranche": "Tranche 1", "qte": min(conso_elec, 125.0), "prix": 1.7787},
        {"tranche": "Tranche 2", "qte": max(0, min(conso_elec - 125.0, 125.0)), "prix": 4.1789},
        {"tranche": "Tranche 3", "qte": max(0, conso_elec - 250.0), "prix": 4.8120}
    ]
    for i in data_elec: i['mt'] = i['qte'] * i['prix']
    
    data_gaz = [
        {"tranche": "Tranche 1", "qte": min(conso_gaz, 1125.0), "prix": 0.1682},
        {"tranche": "Tranche 2", "qte": max(0, min(conso_gaz - 1125.0, 1375.0)), "prix": 0.3245},
        {"tranche": "Tranche 3", "qte": max(0, conso_gaz - 2500.0), "prix": 0.4025}
    ]
    for i in data_gaz: i['mt'] = i['qte'] * i['prix']
    
    total_ht = sum([i['mt'] for i in data_elec]) + sum([i['mt'] for i in data_gaz])
    total_taxes = 164.16 + 138.99 + 301.19 + 200.00 + 200.00
    net_ttc = total_ht + total_taxes
    return data_elec, data_gaz, total_ht, total_taxes, net_ttc, net_ttc + 40.0

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("Navigation")
selected_id = st.sidebar.selectbox("Choisir un abonné :", list(CLIENTS.keys()))
client_info = CLIENTS[selected_id]
mode_acquisition = st.sidebar.radio("Mode d'acquisition :", ["Mode Simulation", "Mode Réel (Carte TTGO)"])
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- PAGES ---
def page_facturation(client_id, info):
    st.title(TITRE_INSTITUTIONNEL)
    st.subheader("Facturation Détaillée")
    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")
    data_elec, data_gaz, ht, taxes, net, total_especes = calculer_facture(conso_elec, conso_gaz)
    
    st.write(f"**Client :** {info['nom']} | **Lieu :** {info['lieu']}")
    st.metric("Total à Payer (Espèces)", f"{total_especes:.2f} DA")
    st.success("Facture calculée avec succès.")

def page_supervision(client_id, info):
    st.title(TITRE_INSTITUTIONNEL)
    st.subheader(f"Supervision par Impulsions : {info['nom']}")
    
    # Logique d'acquisition
    if mode_acquisition == "Mode Simulation":
        if st.button("Simuler réception impulsions"):
            last_elec = get_live_data(client_id, "Elec")
            conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (datetime.now(), "Elec", 5, last_elec + 0.005, client_id))
            conn.commit()
            conn.close()
            st.rerun()
            
    # Affichage Dashboard
    elec_total = get_live_data(client_id, "Elec")
    cols = st.columns(2)
    cols[0].metric("⚡ Total Impulsions Élec", f"{int(elec_total / 0.001)} pulses")
    
    # Graphique
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM mesures WHERE client_id=? ORDER BY timestamp DESC LIMIT 20", conn, params=(client_id,))
    conn.close()
    if not df.empty:
        st.line_chart(df[df['type_energie'] == 'Elec'].set_index('timestamp')['total_jour'])

# --- APPEL PRINCIPAL ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
else:
    page_supervision(selected_id, client_info)
