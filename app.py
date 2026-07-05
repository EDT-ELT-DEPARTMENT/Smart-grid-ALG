import streamlit as st
import sqlite3
import pandas as pd
import random
import io
import requests
from datetime import datetime
from xhtml2pdf import pisa
import streamlit.components.v1 as components

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Smart-Grid SONELGAZ : Supervision Temps Réel et Facturation", layout="wide")

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    # Ajout de check_same_thread=False pour éviter les erreurs de connexion avec Streamlit
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    
    # Initialisation pour les clients si vide
    for client_id in ["7314P001114", "7314P001115", "7314P001116"]:
        c.execute("SELECT COUNT(*) FROM mesures WHERE client_id=?", (client_id,))
        if c.fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", 0.0, 562.00, client_id))
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", 0.0, 2708.40, client_id))
    
    conn.commit()
    conn.close()

init_db()

# --- CONFIGURATION DES CLIENTS ---
CLIENTS = {
    "7314P001114": {"nom": "MME BELASKRI ASMA", "facture": "733260603359", "lieu": "01 BLOC B CT 70 LOGTS UDL"},
    "7314P001115": {"nom": "Client B", "facture": "733260603360", "lieu": "CITE 120 LOGTS BAT A"},
    "7314P001116": {"nom": "Client C", "facture": "733260603361", "lieu": "VILLA N°45 ZONE 02"}
}

# --- FONCTIONS DE CALCUL ---
def calculer_facture(conso_elec, conso_gaz):
    # Logique progressive des tranches
    e1 = min(conso_elec, 125.0)
    e2 = max(0, min(conso_elec - 125.0, 125.0))
    e3 = max(0, conso_elec - 250.0)
    
    data_elec = [
        {"tranche": "Tranche 1", "qte": e1, "prix": 1.7787, "mt": e1 * 1.7787},
        {"tranche": "Tranche 2", "qte": e2, "prix": 4.1789, "mt": e2 * 4.1789},
        {"tranche": "Tranche 3", "qte": e3, "prix": 4.8120, "mt": e3 * 4.8120}
    ]
    ht_elec = sum([i['mt'] for i in data_elec])
    
    g1 = min(conso_gaz, 1125.0)
    g2 = max(0, min(conso_gaz - 1125.0, 1375.0))
    g3 = max(0, conso_gaz - 2500.0)
    
    data_gaz = [
        {"tranche": "Tranche 1", "qte": g1, "prix": 0.1682, "mt": g1 * 0.1682},
        {"tranche": "Tranche 2", "qte": g2, "prix": 0.3245, "mt": g2 * 0.3245},
        {"tranche": "Tranche 3", "qte": g3, "prix": 0.4025, "mt": g3 * 0.4025}
    ]
    ht_gaz = sum([i['mt'] for i in data_gaz])
    
    # Taxes
    total_ht = ht_elec + ht_gaz
    total_taxes = 164.16 + 138.99 + 301.19 + 200.00 + 200.00
    net_ttc = total_ht + total_taxes
    total_especes = net_ttc + 40.00
    
    details_taxes = {"Redevances fixes HT": 164.16, "TVA 9%": 138.99, "TVA 19%": 301.19, "Droit Fixe": 200.00, "Taxe habitation": 200.00, "Timbre": 40.00}
    
    return data_elec, data_gaz, ht_elec, ht_gaz, total_ht, total_taxes, net_ttc, total_especes, details_taxes

def get_live_data(client_id, type_energie):
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    query = "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(type_energie, client_id))
    conn.close()
    return df['total_jour'].iloc[0] if not df.empty else 0.0

# --- NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.markdown("**Smart-Grid SONELGAZ : Supervision Temps Réel et Facturation**")
selected_id = st.sidebar.selectbox("Choisir un abonné :", list(CLIENTS.keys()))
client_info = CLIENTS[selected_id]
mode_acquisition = st.sidebar.radio("Mode d'acquisition :", ["Mode Simulation", "Mode Réel (Carte TTGO)"])
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- PAGE FACTURATION ---
def page_facturation(client_id, info):
    st.title("Smart-Grid SONELGAZ : Facturation Détaillée")
    st.info(f"**Client :** {info['nom']} | **N° Client :** {client_id}")
    
    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")
    data_elec, data_gaz, ht_elec, ht_gaz, total_ht, taxes, net_ttc, total_especes, det_taxes = calculer_facture(conso_elec, conso_gaz)
    
    # Génération du HTML
    facture_html = f"""
    <div style="font-family: sans-serif; padding: 20px; border: 1px solid #ccc;">
        <h2>SONELGAZ - Facture</h2>
        <p><strong>Électricité:</strong> {conso_elec:.2f} kWh</p>
        <p><strong>Gaz:</strong> {conso_gaz:.2f} Th</p>
        <hr>
        <h3>Détails Électricité</h3>
        <ul>{"".join([f"<li>{i['tranche']}: {i['qte']:.2f} kWh -> {i['mt']:.2f} DA</li>" for i in data_elec])}</ul>
        <h3>Net à payer TTC: {net_ttc:.2f} DA</h3>
    </div>
    """
    components.html(facture_html, height=600)

# --- PAGE SUPERVISION ---
def page_supervision(client_id, info):
    st.title("Smart-Grid SONELGAZ : Supervision Temps Réel")
    
    if 'tension' not in st.session_state: st.session_state.tension = 230.0
    
    if mode_acquisition == "Mode Simulation":
        if st.button("Simuler une impulsion"):
            # Récupération des valeurs actuelles
            curr_elec = get_live_data(client_id, "Elec")
            curr_gaz = get_live_data(client_id, "Gaz")
            
            # Incrémentation (Impulsions)
            new_elec = curr_elec + random.uniform(0.5, 2.0)
            new_gaz = curr_gaz + random.uniform(0.1, 0.5)
            
            conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
            c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", 1.0, new_elec, client_id))
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", 1.0, new_gaz, client_id))
            conn.commit()
            conn.close()
            st.rerun()

    # Affichage dynamique basé sur la DB
    elec_val = get_live_data(client_id, "Elec")
    data_elec, _, _, _, _, _, _, _, _ = calculer_facture(elec_val, get_live_data(client_id, "Gaz"))
    
    st.subheader(f"Total Élec actuel : {elec_val:.2f} kWh")
    cols = st.columns(3)
    for i, tranche in enumerate(data_elec):
        cols[i].metric(tranche['tranche'], f"{tranche['qte']:.2f} kWh")
        cols[i].progress(min(tranche['qte'] / (125 if i<2 else 1000), 1.0))

if page == "Facturation":
    page_facturation(selected_id, client_info)
else:
    page_supervision(selected_id, client_info)
