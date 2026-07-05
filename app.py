import streamlit as st
import sqlite3
import pandas as pd
import time
import random
import io
from datetime import datetime
from xhtml2pdf import pisa

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="SONELGAZ - Plateforme", layout="wide")

# --- INITIALISATION DES BASES DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('monitoring_energie.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    
    # Vérification si la colonne client_id existe, sinon on recrée la table
    c.execute("PRAGMA table_info(mesures)")
    columns = [row[1] for row in c.fetchall()]
    if 'client_id' not in columns:
        c.execute("DROP TABLE mesures")
        c.execute("CREATE TABLE mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
    
    conn.commit()
    conn.close()

init_db()

# --- CONFIGURATION DES DONNÉES ---
CLIENTS = {
    "7314P001114": {"nom": "MILOUA Farid", "facture": "733260603359", "lieu": "01 BLOC B CT 70 LOGTS UDL"},
    "7314P001115": {"nom": "BENI Ali", "facture": "733260603360", "lieu": "CITE 120 LOGTS BAT A"},
    "7314P001116": {"nom": "KADI Sarah", "facture": "733260603361", "lieu": "VILLA N°45 ZONE 02"}
}

# --- NAVIGATION ---
st.sidebar.title("Plateforme SONELGAZ")
selected_id = st.sidebar.selectbox("Choisir un abonné :", list(CLIENTS.keys()))
client_info = CLIENTS[selected_id]
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- FONCTION DE CALCUL DYNAMIQUE ---
def get_live_data(client_id):
    conn = sqlite3.connect('monitoring_energie.db')
    query = "SELECT total_jour FROM mesures WHERE type_energie='Elec' AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(client_id,))
    conn.close()
    if not df.empty:
        return df['total_jour'].iloc[0]
    return 0.0

# --- PAGE 1 : FACTURATION ---
def page_facturation(client_id, info):
    st.title("Plateforme de Facturation SONELGAZ")
    st.subheader("Direction de Distribution SIDI BEL ABBES")

    total_conso = get_live_data(client_id)
    
    qte_t1 = min(total_conso, 125.0)
    qte_t2 = max(0, min(total_conso - 125.0, 125.0))
    qte_t3 = max(0, total_conso - 250.0)

    data_elec = [
        {"tranche": "Tranche 1", "qte": qte_t1, "prix": 1.7787, "mt": qte_t1 * 1.7787},
        {"tranche": "Tranche 2", "qte": qte_t2, "prix": 4.1789, "mt": qte_t2 * 4.1789},
        {"tranche": "Tranche 3", "qte": qte_t3, "prix": 4.8120, "mt": qte_t3 * 4.8120}
    ]
    
    redevance, tva_9, tva_19, droit, taxe = 164.16, 138.99, 301.19, 200.0, 200.0
    sous_total_ht = sum([i['mt'] for i in data_elec])
    net_ttc = sous_total_ht + redevance + tva_9 + tva_19 + droit + taxe

    facture_html = f"""
    <div style="border: 2px solid #2980b9; padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation</h2>
    <p><strong>Facture n°:</strong> {info['facture']} | <strong>Client n°:</strong> {client_id}</p>
    <p><strong>Abonné :</strong> {info['nom']} | <strong>Lieu :</strong> {info['lieu']}</p>
    <h3 style="color: #2980b9;">Électricité (Consommation : {total_conso:.2f} kWh)</h3>
    <table style="width:100%; border-collapse: collapse;">
    <tr style="background-color: #d6eaf8;"><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
    {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_elec])}
    </table>
    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 10px;">
    <p>Redevance fixe : {redevance} DA | TVA : {tva_9 + tva_19:.2f} DA</p>
    <h2 style="color: #2980b9; text-align: right;">Net à payer : {net_ttc:.2f} DA</h2>
    </div>
    </div>
    """
    st.markdown(facture_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
    def generate_pdf(html):
        result = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=result)
        return result.getvalue()
    col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")

# --- PAGE 2 : SUPERVISION ---
def page_supervision(client_id, info):
    st.title("Système de Supervision Énergétique - SONELGAZ")
    st.subheader(f"Client : {info['nom']} | ID : {client_id}")

    def add_simulated_data(c_id):
        conn = sqlite3.connect('monitoring_energie.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", random.uniform(1.0, 4.0), random.uniform(50, 300), c_id))
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", random.uniform(0.5, 1.5), random.uniform(5, 20), c_id))
        conn.commit()
        conn.close()

    if st.button("Rafraîchir les données Live"):
        add_simulated_data(client_id)

    conn = sqlite3.connect('monitoring_energie.db')
    df = pd.read_sql_query("SELECT * FROM mesures WHERE client_id=? ORDER BY timestamp DESC LIMIT 20", conn, params=(client_id,))
    conn.close()

    if not df.empty:
        elec_data = df[df['type_energie'] == 'Elec'].iloc[0]
        gaz_data = df[df['type_energie'] == 'Gaz'].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h2 style='color: #2980b9;'>⚡ Électricité</h2>", unsafe_allow_html=True)
            st.metric("Consommation Instantanée", f"{elec_data['valeur_actuelle']:.2f} kW")
            st.line_chart(df[df['type_energie'] == 'Elec'].set_index('timestamp')['valeur_actuelle'])
        with col2:
            st.markdown("<h2 style='color: #e67e22;'>🔥 Gaz</h2>", unsafe_allow_html=True)
            st.metric("Débit Instantané", f"{gaz_data['valeur_actuelle']:.2f} m³/h")
            st.line_chart(df[df['type_energie'] == 'Gaz'].set_index('timestamp')['valeur_actuelle'])

        # --- SECTION TRANCHES RESTAURÉE ---
        st.divider()
        st.subheader("État des Tranches de Consommation")
        col_t1, col_t2, col_t3 = st.columns(3)
        
        # Logique des barres de progression
        conso_totale = elec_data['total_jour']
        t1_prog = min((conso_totale / 125.0) * 100, 100)
        col_t1.progress(t1_prog / 100, text=f"Tranche 1 (125 kWh) : {t1_prog:.1f}%")
        
        t2_prog = min(max(((conso_totale - 125) / 125.0) * 100, 0), 100) if conso_totale > 125 else 0
        col_t2.progress(t2_prog / 100, text=f"Tranche 2 (125 kWh) : {t2_prog:.1f}%")
        
        t3_prog = max(((conso_totale - 250) / 1000) * 100, 0) if conso_totale > 250 else 0
        col_t3.progress(min(t3_prog / 100, 1.0), text=f"Tranche 3 (Supp) : {t3_prog:.1f}%")

    else:
        st.info("En attente de données de la carte TTGO ESP32...")

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
elif page == "Supervision Temps Réel":
    page_supervision(selected_id, client_info)
