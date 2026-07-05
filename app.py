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

# --- FONCTION DE RÉCUPÉRATION DONNÉES ---
def get_live_data(client_id, type_energie):
    conn = sqlite3.connect('monitoring_energie.db')
    query = "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(type_energie, client_id))
    conn.close()
    if not df.empty:
        return df['total_jour'].iloc[0]
    return 0.0

# --- PAGE 1 : FACTURATION ---
def page_facturation(client_id, info):
    st.title("Plateforme de Facturation SONELGAZ")
    st.subheader("Direction de Distribution SIDI BEL ABBES")

    # Récupération des totaux
    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")
    
    # Calcul Tranches Elec
    qte_t1_e = min(conso_elec, 125.0)
    qte_t2_e = max(0, min(conso_elec - 125.0, 125.0))
    qte_t3_e = max(0, conso_elec - 250.0)
    
    data_elec = [
        {"tranche": "Tranche 1", "qte": qte_t1_e, "prix": 1.7787, "mt": qte_t1_e * 1.7787},
        {"tranche": "Tranche 2", "qte": qte_t2_e, "prix": 4.1789, "mt": qte_t2_e * 4.1789},
        {"tranche": "Tranche 3", "qte": qte_t3_e, "prix": 4.8120, "mt": qte_t3_e * 4.8120}
    ]

    # Calcul Tranches Gaz
    qte_t1_g = min(conso_gaz, 1125.0)
    qte_t2_g = max(0, min(conso_gaz - 1125.0, 1375.0))
    qte_t3_g = max(0, conso_gaz - 2500.0)

    data_gaz = [
        {"tranche": "Tranche 1", "qte": qte_t1_g, "prix": 0.1682, "mt": qte_t1_g * 0.1682},
        {"tranche": "Tranche 2", "qte": qte_t2_g, "prix": 0.3245, "mt": qte_t2_g * 0.3245},
        {"tranche": "Tranche 3", "qte": qte_t3_g, "prix": 0.4025, "mt": qte_t3_g * 0.4025}
    ]
    
    # Frais annexes
    redevance, tva_9, tva_19, droit, taxe = 164.16, 138.99, 301.19, 200.0, 200.0
    total_ht = sum([i['mt'] for i in data_elec]) + sum([i['mt'] for i in data_gaz])
    net_ttc = total_ht + redevance + tva_9 + tva_19 + droit + taxe

    facture_html = f"""
    <html>
    <head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head>
    <body>
    <div style="border: 2px solid #2980b9; padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation</h2>
    <p><strong>Facture n°:</strong> {info['facture']} | <strong>Client n°:</strong> {client_id}</p>
    <p><strong>Abonné :</strong> {info['nom']} | <strong>Lieu :</strong> {info['lieu']}</p>
    
    <h3 style="color: #2980b9;">Électricité (Total : {conso_elec:.2f} kWh)</h3>
    <table style="width:100%; border-collapse: collapse;">
    <tr style="background-color: #d6eaf8;"><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
    {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_elec])}
    </table>

    <h3 style="color: #e67e22;">Gaz (Total : {conso_gaz:.2f} m³)</h3>
    <table style="width:100%; border-collapse: collapse;">
    <tr style="background-color: #fbdac2;"><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
    {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_gaz])}
    </table>

    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 10px;">
    <p>Redevance fixe : {redevance} DA | TVA : {tva_9 + tva_19:.2f} DA | Droit/Taxe : {droit + taxe:.2f} DA</p>
    <h2 style="color: #2980b9; text-align: right;">Net à payer : {net_ttc:.2f} DA</h2>
    </div>
    </div>
    </body>
    </html>
    """
    st.markdown(facture_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
    
    def generate_pdf(html):
        result = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html.encode("utf-8")), dest=result, encoding='utf-8')
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
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", random.uniform(0.5, 1.5), random.uniform(5, 40), c_id))
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

        st.divider()
        st.subheader("État des Tranches Électriques")
        col_t1, col_t2, col_t3 = st.columns(3)
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
