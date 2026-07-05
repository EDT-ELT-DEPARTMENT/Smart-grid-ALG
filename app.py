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
    conn = sqlite3.connect('monitoring_energie.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    
    # Insertion de données initiales simulant la facture pour le client principal
    c.execute("SELECT COUNT(*) FROM mesures WHERE client_id='7314P001114'")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Injection des valeurs initiales
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", 0.0, 562.00, "7314P001114"))
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", 0.0, 2708.40, "7314P001114"))
    
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
    # 1. Électricité
    e1 = min(conso_elec, 125.0)
    e2 = max(0, min(conso_elec - 125.0, 125.0))
    e3 = max(0, conso_elec - 250.0)
    data_elec = [
        {"tranche": "Tranche 1", "qte": e1, "prix": 1.7787, "mt": e1 * 1.7787},
        {"tranche": "Tranche 2", "qte": e2, "prix": 4.1789, "mt": e2 * 4.1789},
        {"tranche": "Tranche 3", "qte": e3, "prix": 4.8120, "mt": e3 * 4.8120}
    ]
    ht_elec = sum([i['mt'] for i in data_elec])
    
    # 2. Gaz
    g1 = min(conso_gaz, 1125.0)
    g2 = max(0, min(conso_gaz - 1125.0, 1375.0))
    g3 = max(0, conso_gaz - 2500.0)
    data_gaz = [
        {"tranche": "Tranche 1", "qte": g1, "prix": 0.1682, "mt": g1 * 0.1682},
        {"tranche": "Tranche 2", "qte": g2, "prix": 0.3245, "mt": g2 * 0.3245},
        {"tranche": "Tranche 3", "qte": g3, "prix": 0.4025, "mt": g3 * 0.4025}
    ]
    ht_gaz = sum([i['mt'] for i in data_gaz])
    
    # 3. Taxes et Redevances
    total_ht = ht_elec + ht_gaz
    total_taxes = 164.16 + 138.99 + 301.19 + 200.00 + 200.00 # Fixes
    net_ttc = total_ht + total_taxes
    total_especes = net_ttc + 40.00 # Timbre
    
    details_taxes = {"Redevances fixes HT": 164.16, "TVA 9%": 138.99, "TVA 19%": 301.19, "Droit Fixe": 200.00, "Taxe habitation": 200.00, "Timbre": 40.00}
    
    return data_elec, data_gaz, ht_elec, ht_gaz, total_ht, total_taxes, net_ttc, total_especes, details_taxes

# --- FONCTION RÉCUPÉRATION ---
def get_live_data(client_id, type_energie):
    conn = sqlite3.connect('monitoring_energie.db')
    query = "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(type_energie, client_id))
    conn.close()
    return df['total_jour'].iloc[0] if not df.empty else 0.0

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("Navigation")
selected_id = st.sidebar.selectbox("Choisir un abonné :", list(CLIENTS.keys()))
client_info = CLIENTS[selected_id]
mode_acquisition = st.sidebar.radio("Mode d'acquisition :", ["Mode Simulation", "Mode Réel (Carte TTGO)"])
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- PAGE 1 : FACTURATION ---
def page_facturation(client_id, info):
    st.title("Smart-Grid SONELGAZ : Facturation Détaillée")
    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")
    data_elec, data_gaz, ht_elec, ht_gaz, total_ht, taxes, net_ttc, total_especes, det_taxes = calculer_facture(conso_elec, conso_gaz)
    
    facture_html = f"""
    <style>
        .invoice-box {{ font-family: 'Arial', sans-serif; padding: 20px; border: 1px solid #ccc; }}
        th {{ background-color: #005bb5; color: white; padding: 10px; }}
        td {{ border-bottom: 1px solid #eee; padding: 8px; }}
    </style>
    <div class="invoice-box">
        <h3>SONELGAZ - Facture : {info['facture']}</h3>
        <p><strong>Client:</strong> {info['nom']} | <strong>Lieu:</strong> {info['lieu']}</p>
        <h4>⚡ Électricité ({conso_elec:.2f} kWh)</h4>
        <table>
            <tr><th>Tranche</th><th>Qte</th><th>Prix</th><th>HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_elec])}
        </table>
        <h3>NET À PAYER TTC: {net_ttc:.2f} DA</h3>
    </div>
    """
    components.html(facture_html, height=800, scrolling=True)

# --- PAGE 2 : SUPERVISION ---
def page_supervision(client_id, info):
    st.title("Smart-Grid SONELGAZ : Supervision")
    
    # État simulation
    if 'tension' not in st.session_state: st.session_state.tension = 230.0
    if 'courant' not in st.session_state: st.session_state.courant = 0.0
    
    if mode_acquisition == "Mode Simulation":
        st.info("🔧 **Mode Simulation Dynamique** (1 impulsion = 1 Wh)")
        
        # Mapping activité -> impulsions
        activites = {
            "Veille TV": 50,
            "Éclairage LED (1h)": 200,
            "Réfrigérateur (Cycle)": 500,
            "Machine à laver": 1500,
            "Chauffage Électrique": 3000
        }
        
        selection = st.selectbox("Simuler une activité :", list(activites.keys()))
        if st.button("Valider la consommation"):
            imp = activites[selection]
            kwh = imp / 1000.0
            
            # Mise à jour BDD
            current_elec = get_live_data(client_id, "Elec")
            current_gaz = get_live_data(client_id, "Gaz")
            
            conn = sqlite3.connect('monitoring_energie.db')
            c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", 0.0, current_elec + kwh, client_id))
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", 0.0, current_gaz + (kwh * 0.5), client_id))
            conn.commit()
            conn.close()
            st.rerun()

    elif mode_acquisition == "Mode Réel (Carte TTGO)":
        ip_ttgo = st.text_input("IP TTGO :", "192.168.1.50")
        if st.button("Acquérir données"):
            try:
                response = requests.get(f"http://{ip_ttgo}/mesures", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.tension = float(data.get('v', 230.0))
                    # ... (reste du code acquisition réel)
            except Exception as e:
                st.error(f"Erreur : {e}")

    # Affichage Dashboard
    st.markdown("### 📊 État du Réseau")
    cols = st.columns(4)
    cols[0].metric("Tension", f"{st.session_state.tension:.1f} V")
    
    # Affichage des tranches
    elec_val = get_live_data(client_id, "Elec")
    gaz_val = get_live_data(client_id, "Gaz")
    data_elec, data_gaz, _, _, _, _, _, _, _ = calculer_facture(elec_val, gaz_val)
    
    st.markdown("### ⚡ Consommation Électricité")
    cols_e = st.columns(3)
    for i, t in enumerate(data_elec):
        cols_e[i].metric(t['tranche'], f"{t['qte']:.2f} kWh")

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
elif page == "Supervision Temps Réel":
    page_supervision(selected_id, client_info)
