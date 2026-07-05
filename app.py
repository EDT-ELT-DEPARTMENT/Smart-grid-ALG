import streamlit as st
import sqlite3
import pandas as pd
import random
import io
from datetime import datetime
from xhtml2pdf import pisa
import streamlit.components.v1 as components

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Plateforme de gestion des EDTs-S2-2026", layout="wide")

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('monitoring_energie.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- CONFIGURATION DES CLIENTS ---
CLIENTS = {
    "7314P001114": {"nom": "MILOUA Farid", "facture": "733260603359", "lieu": "01 BLOC B CT 70 LOGTS UDL"},
    "7314P001115": {"nom": "BENI Ali", "facture": "733260603360", "lieu": "CITE 120 LOGTS BAT A"},
    "7314P001116": {"nom": "KADI Sarah", "facture": "733260603361", "lieu": "VILLA N°45 ZONE 02"}
}

# --- NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.markdown("**Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA**")

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

# --- PAGE 1 : FACTURATION ---
def page_facturation(client_id, info):
    st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
    
    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")

    # Calculs
    data_elec = [
        {"tranche": "Tranche 1", "qte": min(conso_elec, 125.0), "prix": 1.7787},
        {"tranche": "Tranche 2", "qte": max(0, min(conso_elec - 125.0, 125.0)), "prix": 4.1789},
        {"tranche": "Tranche 3", "qte": max(0, conso_elec - 250.0), "prix": 4.8120}
    ]
    for i in data_elec: i['mt'] = i['qte'] * i['prix']
    ht_elec = sum([i['mt'] for i in data_elec])

    data_gaz = [
        {"tranche": "Tranche 1", "qte": min(conso_gaz, 1125.0), "prix": 0.1682},
        {"tranche": "Tranche 2", "qte": max(0, min(conso_gaz - 1125.0, 1375.0)), "prix": 0.3245},
        {"tranche": "Tranche 3", "qte": max(0, conso_gaz - 2500.0), "prix": 0.4025}
    ]
    for i in data_gaz: i['mt'] = i['qte'] * i['prix']
    ht_gaz = sum([i['mt'] for i in data_gaz])

    taxes = 164.16 + 138.99 + 301.19 + 200.0 + 200.0
    total_ht = ht_elec + ht_gaz
    net_ttc = total_ht + taxes

    # HTML avec design Bleu Professionnel
    facture_html = f"""
    <style>
        .invoice-box {{ font-family: 'Arial', sans-serif; padding: 30px; border: 1px solid #d1d1d1; background: #fff; border-radius: 10px; }}
        .header {{ background-color: #004a99; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background-color: #005bb5; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:nth-child(even) {{ background-color: #f2f7ff; }}
        .summary-box {{ background-color: #eef6ff; padding: 15px; border-left: 5px solid #004a99; margin-top: 20px; }}
        .total-line {{ font-size: 1.2em; font-weight: bold; color: #004a99; }}
    </style>
    <div class="invoice-box">
        <div class="header"><h2>SONELGAZ - Détail de Facturation</h2></div>
        <p><strong>Abonné :</strong> {info['nom']} | <strong>Lieu :</strong> {info['lieu']}</p>
        
        <h3>⚡ Électricité</h3>
        <table>
            <tr><th>Tranche</th><th>Quantité</th><th>Prix</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_elec])}
        </table>
        
        <h3>🔥 Gaz</h3>
        <table>
            <tr><th>Tranche</th><th>Quantité</th><th>Prix</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_gaz])}
        </table>
        
        <div class="summary-box">
            <p>Total HT Électricité : {ht_elec:.2f} DA</p>
            <p>Total HT Gaz : {ht_gaz:.2f} DA</p>
            <p class="total-line">TOTAL GLOBAL HT : {total_ht:.2f} DA</p>
            <p>Taxes et Redevances : {taxes:.2f} DA</p>
            <h2 style="color: #c0392b;">NET À PAYER (TTC) : {net_ttc:.2f} DA</h2>
        </div>
    </div>
    """
    
    components.html(facture_html, height=850, scrolling=True)

    def generate_pdf(html_string):
        result = io.BytesIO()
        pisa.CreatePDF(html_string, dest=result, encoding='utf-8')
        return result.getvalue()

    col1, col2 = st.columns(2)
    col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
    col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")

# --- PAGE 2 : SUPERVISION ---
def page_supervision(client_id, info):
    st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
    st.subheader(f"Supervision : {info['nom']}")
    
    # [Le reste du code supervision reste identique]
    conn = sqlite3.connect('monitoring_energie.db')
    df = pd.read_sql_query("SELECT * FROM mesures WHERE client_id=? ORDER BY timestamp DESC LIMIT 20", conn, params=(client_id,))
    conn.close()
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1: st.line_chart(df[df['type_energie'] == 'Elec'].set_index('timestamp')['valeur_actuelle'])
        with col2: st.line_chart(df[df['type_energie'] == 'Gaz'].set_index('timestamp')['valeur_actuelle'])
    else: st.warning("Données indisponibles.")

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
elif page == "Supervision Temps Réel":
    page_supervision(selected_id, client_info)
