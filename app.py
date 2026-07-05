import streamlit as st
import sqlite3
import pandas as pd
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
    # Table pour stocker les mesures des deux flux
    c.execute('''CREATE TABLE IF NOT EXISTS mesures 
                 (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- NAVIGATION ---
st.sidebar.title("Plateforme SONELGAZ")
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- FONCTION DE CALCUL DYNAMIQUE ---
def get_live_data():
    conn = sqlite3.connect('monitoring_energie.db')
    # On récupère le dernier cumul pour l'électricité
    df = pd.read_sql_query("SELECT total_jour FROM mesures WHERE type_energie='Elec' ORDER BY timestamp DESC LIMIT 1", conn)
    conn.close()
    if not df.empty:
        return df['total_jour'].iloc[0]
    return 0.0 # Valeur par défaut si rien n'est enregistré

# --- PAGE 1 : FACTURATION ---
def page_facturation():
    st.title("Plateforme de Facturation SONELGAZ")
    st.subheader("Direction de Distribution SIDI BEL ABBES")

    # Calcul dynamique des tranches
    total_conso = get_live_data()
    
    # Logique de découpage en tranches (125 kWh par palier)
    qte_t1 = min(total_conso, 125.0)
    qte_t2 = max(0, min(total_conso - 125.0, 125.0))
    qte_t3 = max(0, total_conso - 250.0)

    # Mise à jour des données avec les valeurs réelles
    data = {
        "nom": "Mr MILOUA Farid",
        "client_num": "7314P001114",
        "lieu_conso": "01 BLOC B CT 70 LOGTS UDL",
        "fact_num": "733260603359",
        "elec": [
            {"tranche": "Tranche 1", "qte": qte_t1, "prix": 1.7787, "mt": qte_t1 * 1.7787},
            {"tranche": "Tranche 2", "qte": qte_t2, "prix": 4.1789, "mt": qte_t2 * 4.1789},
            {"tranche": "Tranche 3", "qte": qte_t3, "prix": 4.8120, "mt": qte_t3 * 4.8120}
        ],
        "redevance": 164.16, "tva_9": 138.99, "tva_19": 301.19, "droit": 200.0, "taxe": 200.0
    }
    
    # Calcul du Net à payer
    sous_total_ht = sum([i['mt'] for i in data['elec']])
    data['net_ttc'] = sous_total_ht + data['redevance'] + data['tva_9'] + data['tva_19'] + data['droit'] + data['taxe']

    facture_html = f"""
    <div style="border: 2px solid #2980b9; padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation (Temps Réel)</h2>
    <p><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
    <p><strong>Abonné :</strong> {data['nom']} | <strong>Lieu :</strong> {data['lieu_conso']}</p>
    <h3 style="color: #2980b9;">Électricité (Consommation totale : {total_conso:.2f} kWh)</h3>
    <table style="width:100%; border-collapse: collapse;">
    <tr style="background-color: #d6eaf8;"><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
    {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data['elec']])}
    </table>
    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 10px;">
    <p>Redevance fixe : {data['redevance']} DA | TVA (9% : {data['tva_9']} DA | 19% : {data['tva_19']} DA)</p>
    <p>Droit fixe : {data['droit']} DA | Taxe habitation : {data['taxe']} DA</p>
    <h2 style="color: #2980b9; text-align: right;">Net à payer : {data['net_ttc']:.2f} DA</h2>
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
def page_supervision():
    st.title("Système de Supervision Énergétique - SONELGAZ")
    st.subheader("Client : Mr MILOUA Farid | ID : 7314P001114")

    # Fonction de simulation
    def add_simulated_data():
        conn = sqlite3.connect('monitoring_energie.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # On simule une augmentation du cumul quotidien pour tester le changement de facture
        cumul_actuel = random.uniform(50, 300) 
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?)", (now, "Elec", random.uniform(1.2, 3.5), cumul_actuel))
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?)", (now, "Gaz", random.uniform(0.5, 1.2), random.uniform(10, 15)))
        conn.commit()
        conn.close()

    col1, col2 = st.columns(2)
    if st.button("Rafraîchir les données Live"):
        add_simulated_data()

    conn = sqlite3.connect('monitoring_energie.db')
    df = pd.read_sql_query("SELECT * FROM mesures ORDER BY timestamp DESC LIMIT 20", conn)
    conn.close()

    if not df.empty:
        elec_data = df[df['type_energie'] == 'Elec'].iloc[0]
        gaz_data = df[df['type_energie'] == 'Gaz'].iloc[0]

        with col1:
            st.markdown("<h2 style='color: #2980b9;'>⚡ Électricité (Temps Réel)</h2>", unsafe_allow_html=True)
            st.metric(label="Consommation Instantanée", value=f"{elec_data['valeur_actuelle']:.2f} kW")
            st.metric(label="Cumul Journalier", value=f"{elec_data['total_jour']:.2f} kWh")
            chart_data_elec = df[df['type_energie'] == 'Elec'].set_index('timestamp')['valeur_actuelle']
            st.line_chart(chart_data_elec)

        with col2:
            st.markdown("<h2 style='color: #e67e22;'>🔥 Gaz (Temps Réel)</h2>", unsafe_allow_html=True)
            st.metric(label="Débit Instantané", value=f"{gaz_data['valeur_actuelle']:.2f} m³/h")
            st.metric(label="Cumul Journalier", value=f"{gaz_data['total_jour']:.2f} m³")
            chart_data_gaz = df[df['type_energie'] == 'Gaz'].set_index('timestamp')['valeur_actuelle']
            st.line_chart(chart_data_gaz)

        st.divider()
        st.subheader("État des Tranches de Consommation")
        col_t1, col_t2, col_t3 = st.columns(3)
        t1_prog = min((elec_data['total_jour'] / 125.0) * 100, 100)
        col_t1.progress(t1_prog / 100, text=f"Tranche 1 (125 kWh) : {t1_prog:.1f}%")
        t2_prog = min(max(((elec_data['total_jour'] - 125) / 125.0) * 100, 0), 100) if elec_data['total_jour'] > 125 else 0
        col_t2.progress(t2_prog / 100, text=f"Tranche 2 (125 kWh) : {t2_prog:.1f}%")
        t3_prog = max(((elec_data['total_jour'] - 250) / 1000) * 100, 0) if elec_data['total_jour'] > 250 else 0
        col_t3.progress(min(t3_prog / 100, 1.0), text=f"Tranche 3 (Supp) : {t3_prog:.1f}%")
    else:
        st.info("En attente de données de la carte TTGO ESP32...")
        if st.button("Initialiser avec des données fictives"):
            add_simulated_data()
            st.rerun()

    st.markdown("---")
    st.caption("Système de monitoring actif. Assurez-vous que votre ESP32 est configuré pour POSTer vers l'API de réception.")

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation()
elif page == "Supervision Temps Réel":
    page_supervision()
