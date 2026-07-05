import streamlit as st
import sqlite3
import pandas as pd
import io
import random
from datetime import datetime
from xhtml2pdf import pisa

# --- CONFIGURATION GLOBALE ---
st.set_page_config(page_title="SONELGAZ - Plateforme de Gestion", layout="wide")

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('sonelgaz_data.db')
    c = conn.cursor()
    # Table pour le monitoring
    c.execute('''CREATE TABLE IF NOT EXISTS mesures 
                 (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- NAVIGATION ---
st.sidebar.title("Plateforme SONELGAZ")
page = st.sidebar.radio("Menu de Navigation", ["Facturation", "Supervision Temps Réel"])

# --- PAGE 1 : FACTURATION ---
def page_facturation():
    st.title("Plateforme de Facturation SONELGAZ")
    st.subheader("Direction de Distribution SIDI BEL ABBES")

    data = {
        "nom": "Mr MILOUA Farid",
        "client_num": "7314P001114",
        "lieu_conso": "01 BLOC B CT 70 LOGTS UDL",
        "fact_num": "733260603359",
        "elec": [
            {"tranche": "Tranche 1", "qte": 125.0, "prix": 1.7787, "mt": 744.70},
            {"tranche": "Tranche 2", "qte": 125.0, "prix": 4.1789, "mt": 744.70},
            {"tranche": "Tranche 3", "qte": 312.0, "prix": 4.8120, "mt": 1501.34}
        ],
        "gaz": [
            {"tranche": "Tranche 1", "qte": 1125.0, "prix": 0.1682, "mt": 635.42},
            {"tranche": "Tranche 2", "qte": 1375.0, "prix": 0.3245, "mt": 635.42},
            {"tranche": "Tranche 3", "qte": 208.4, "prix": 0.4025, "mt": 83.88}
        ],
        "redevance": 164.16, "tva_9": 138.99, "tva_19": 301.19, "droit": 200.0, "taxe": 200.0, "net_ttc": 3969.68
    }

    html = f"""
    <div style="border: 2px solid #2980b9; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation</h2>
        <p><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
        <p><strong>Abonné :</strong> {data['nom']} | <strong>Lieu :</strong> {data['lieu_conso']}</p>
        <h3 style="color: #2980b9;">Électricité</h3>
        <table style="width:100%; border-collapse: collapse; margin-bottom: 15px;">
            <tr style="background-color: #d6eaf8;"><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']}</td><td>{i['prix']}</td><td>{i['mt']}</td></tr>" for i in data['elec']])}
        </table>
        <h3 style="color: #2980b9;">Gaz</h3>
        <table style="width:100%; border-collapse: collapse; margin-bottom: 15px;">
            <tr style="background-color: #d6eaf8;"><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']}</td><td>{i['prix']}</td><td>{i['mt']}</td></tr>" for i in data['gaz']])}
        </table>
        <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 10px;">
            <p>Redevance fixe : {data['redevance']} DA | TVA (9% : {data['tva_9']} DA | 19% : {data['tva_19']} DA)</p>
            <p>Droit fixe : {data['droit']} DA | Taxe habitation : {data['taxe']} DA</p>
            <h2 style="color: #2980b9; text-align: right;">Net à payer : {data['net_ttc']:.2f} DA</h2>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.download_button("Télécharger HTML", html, "facture.html", "text/html")
    
    def generate_pdf(html_content):
        result = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html_content.encode("utf-8")), dest=result)
        return result.getvalue()
        
    col2.download_button("Télécharger PDF", generate_pdf(html), "facture.pdf", "application/pdf")

# --- PAGE 2 : SUPERVISION ---
def page_supervision():
    st.title("Supervision Énergétique Temps Réel")
    st.subheader("Client : Mr MILOUA Farid | État : Connecté")
    
    # Simulation de données
    if st.button("Rafraîchir les données Live"):
        conn = sqlite3.connect('sonelgaz_data.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?)", (now, "Elec", random.uniform(1.0, 4.0), random.uniform(20, 30)))
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?)", (now, "Gaz", random.uniform(0.5, 1.5), random.uniform(5, 10)))
        conn.commit()
        conn.close()
        
    conn = sqlite3.connect('sonelgaz_data.db')
    df = pd.read_sql_query("SELECT * FROM mesures ORDER BY timestamp DESC LIMIT 20", conn)
    conn.close()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        # Elec
        with col1:
            st.markdown("### ⚡ Électricité")
            elec = df[df['type_energie'] == 'Elec'].iloc[0]
            st.metric("Consommation Instantanée", f"{elec['valeur_actuelle']:.2f} kW")
            st.line_chart(df[df['type_energie'] == 'Elec'].set_index('timestamp')['valeur_actuelle'])
            
        # Gaz
        with col2:
            st.markdown("### 🔥 Gaz")
            gaz = df[df['type_energie'] == 'Gaz'].iloc[0]
            st.metric("Débit Instantané", f"{gaz['valeur_actuelle']:.2f} m³/h")
            st.line_chart(df[df['type_energie'] == 'Gaz'].set_index('timestamp')['valeur_actuelle'])
    else:
        st.warning("Aucune donnée disponible. Appuyez sur 'Rafraîchir' pour simuler une réception de données ESP32.")

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation()
elif page == "Supervision Temps Réel":
    page_supervision()
