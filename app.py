import streamlit as st
import sqlite3
import pandas as pd
import random
import io
from datetime import datetime
from xhtml2pdf import pisa

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Plateforme de gestion des EDTs-S2-2026", layout="wide")

# --- INITIALISATION ---
def init_db():
    conn = sqlite3.connect('monitoring_energie.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- DONNÉES ---
CLIENTS = {
    "7314P001114": {"nom": "MILOUA Farid", "facture": "733260603359", "lieu": "01 BLOC B CT 70 LOGTS UDL"},
    "7314P001115": {"nom": "BENI Ali", "facture": "733260603360", "lieu": "CITE 120 LOGTS BAT A"},
    "7314P001116": {"nom": "KADI Sarah", "facture": "733260603361", "lieu": "VILLA N°45 ZONE 02"}
}

# --- NAVIGATION ---
st.sidebar.title("Plateforme de gestion")
selected_id = st.sidebar.selectbox("Choisir un abonné :", list(CLIENTS.keys()))
client_info = CLIENTS[selected_id]
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- FONCTION RÉCUPÉRATION ---
def get_live_data(client_id, type_energie):
    conn = sqlite3.connect('monitoring_energie.db')
    query = "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(type_energie, client_id))
    conn.close()
    return df['total_jour'].iloc[0] if not df.empty else 0.0

# --- PAGE FACTURATION ---
def page_facturation(client_id, info):
    st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
    st.subheader("Direction de Distribution SIDI BEL ABBES")

    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")
    
    # Calcul Élec
    data_elec = [
        {"tranche": "T1", "qte": min(conso_elec, 125), "prix": 1.7787},
        {"tranche": "T2", "qte": max(0, min(conso_elec - 125, 125)), "prix": 4.1789},
        {"tranche": "T3", "qte": max(0, conso_elec - 250), "prix": 4.8120}
    ]
    for i in data_elec: i['mt'] = i['qte'] * i['prix']
    ht_elec = sum([i['mt'] for i in data_elec])

    # Calcul Gaz
    data_gaz = [
        {"tranche": "T1", "qte": min(conso_gaz, 1125), "prix": 0.1682},
        {"tranche": "T2", "qte": max(0, min(conso_gaz - 1125, 1375)), "prix": 0.3245},
        {"tranche": "T3", "qte": max(0, conso_gaz - 2500), "prix": 0.4025}
    ]
    for i in data_gaz: i['mt'] = i['qte'] * i['prix']
    ht_gaz = sum([i['mt'] for i in data_gaz])
    
    # Totaux
    total_ht = ht_elec + ht_gaz
    taxes = 164.16 + 138.99 + 301.19 + 200.0 + 200.0 # Redevance + TVA + Droits
    net_ttc = total_ht + taxes

    facture_html = f"""
    <html><body>
    <div style="font-family: Arial;">
    <h2>Détail Facturation - {info['nom']}</h2>
    <table style="width:100%; border: 1px solid #ccc;">
        <tr><th>Description</th><th>Montant HT</th></tr>
        <tr><td>Total Électricité</td><td>{ht_elec:.2f} DA</td></tr>
        <tr><td>Total Gaz</td><td>{ht_gaz:.2f} DA</td></tr>
        <tr style="background:#eee;"><td><strong>TOTAL GLOBAL HT</strong></td><td><strong>{total_ht:.2f} DA</strong></td></tr>
    </table>
    <p>Redevance et Taxes : {taxes:.2f} DA</p>
    <h2 style="color:red;">Net à payer (TTC) : {net_ttc:.2f} DA</h2>
    </div>
    </body></html>
    """
    st.markdown(facture_html, unsafe_allow_html=True)

# --- PAGE SUPERVISION ---
def page_supervision(client_id, info):
    st.title("Supervision - Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
    # ... (Code supervision identique aux versions précédentes pour la logique graphique)
    pass

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
elif page == "Supervision Temps Réel":
    page_supervision(selected_id, client_info)
