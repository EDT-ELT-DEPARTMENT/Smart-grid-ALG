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
    c.execute("PRAGMA table_info(mesures)")
    columns = [row[1] for row in c.fetchall()]
    if 'client_id' not in columns:
        c.execute("DROP TABLE mesures")
        c.execute("CREATE TABLE mesures (timestamp DATETIME, type_energie TEXT, valeur_actuelle REAL, total_jour REAL, client_id TEXT)")
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

# --- FONCTION DE RÉCUPÉRATION ---
def get_live_data(client_id, type_energie):
    conn = sqlite3.connect('monitoring_energie.db')
    query = "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(type_energie, client_id))
    conn.close()
    return df['total_jour'].iloc[0] if not df.empty else 0.0

# --- PAGE 1 : FACTURATION ---
def page_facturation(client_id, info):
    st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
    st.subheader(f"Facturation : {info['nom']} | Client n°: {client_id}")

    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")

    # Calcul Électricité
    qte_e1 = min(conso_elec, 125.0)
    qte_e2 = max(0, min(conso_elec - 125.0, 125.0))
    qte_e3 = max(0, conso_elec - 250.0)
    data_elec = [
        {"tranche": "Tranche 1", "qte": qte_e1, "prix": 1.7787, "mt": qte_e1 * 1.7787},
        {"tranche": "Tranche 2", "qte": qte_e2, "prix": 4.1789, "mt": qte_e2 * 4.1789},
        {"tranche": "Tranche 3", "qte": qte_e3, "prix": 4.8120, "mt": qte_e3 * 4.8120}
    ]
    ht_elec = sum([i['mt'] for i in data_elec])

    # Calcul Gaz
    qte_g1 = min(conso_gaz, 1125.0)
    qte_g2 = max(0, min(conso_gaz - 1125.0, 1375.0))
    qte_g3 = max(0, conso_gaz - 2500.0)
    data_gaz = [
        {"tranche": "Tranche 1", "qte": qte_g1, "prix": 0.1682, "mt": qte_g1 * 0.1682},
        {"tranche": "Tranche 2", "qte": qte_g2, "prix": 0.3245, "mt": qte_g2 * 0.3245},
        {"tranche": "Tranche 3", "qte": qte_g3, "prix": 0.4025, "mt": qte_g3 * 0.4025}
    ]
    ht_gaz = sum([i['mt'] for i in data_gaz])

    # Totaux
    taxes_fixes = 164.16 + 138.99 + 301.19 + 200.0 + 200.0
    total_ht = ht_elec + ht_gaz
    net_ttc = total_ht + taxes_fixes

    # Construction HTML
    facture_html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ccc; background-color: white;">
        <h2>SONELGAZ - Détail de Facturation</h2>
        <p><strong>Abonné :</strong> {info['nom']} | <strong>Lieu :</strong> {info['lieu']}</p>
        <h3>Électricité</h3>
        <table border="1" style="width:100%; border-collapse: collapse;">
            <tr><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_elec])}
        </table>
        <h3>Gaz</h3>
        <table border="1" style="width:100%; border-collapse: collapse;">
            <tr><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_gaz])}
        </table>
        <div style="margin-top: 20px;">
            <p><strong>Total HT Électricité :</strong> {ht_elec:.2f} DA</p>
            <p><strong>Total HT Gaz :</strong> {ht_gaz:.2f} DA</p>
            <p style="background-color: #eee; padding: 10px;"><strong>TOTAL GLOBAL HT : {total_ht:.2f} DA</strong></p>
            <p><strong>Taxes, TVA et Redevances :</strong> {taxes_fixes:.2f} DA</p>
            <h2 style="color: #2980b9;">NET À PAYER (TTC) : {net_ttc:.2f} DA</h2>
        </div>
    </div>
    """
    
    # Rendu propre du HTML via le composant
    components.html(facture_html, height=700, scrolling=True)

    # Téléchargement
    def generate_pdf(html):
        result = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html.encode("utf-8")), dest=result, encoding='utf-8')
        return result.getvalue()

    col1, col2 = st.columns(2)
    col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
    col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")

# --- PAGE 2 : SUPERVISION ---
def page_supervision(client_id, info):
    st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
    st.subheader(f"Supervision Temps Réel : {info['nom']}")

    def add_simulated_data(c_id):
        conn = sqlite3.connect('monitoring_energie.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", random.uniform(1.0, 4.0), random.uniform(50, 400), c_id))
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", random.uniform(0.5, 1.5), random.uniform(5, 50), c_id))
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
            st.markdown("### ⚡ Électricité")
            st.line_chart(df[df['type_energie'] == 'Elec'].set_index('timestamp')['valeur_actuelle'])
        with col2:
            st.markdown("### 🔥 Gaz")
            st.line_chart(df[df['type_energie'] == 'Gaz'].set_index('timestamp')['valeur_actuelle'])

        st.divider()
        st.subheader("Tranches Électricité")
        c1, c2, c3 = st.columns(3)
        conso_e = elec_data['total_jour']
        c1.progress(min(conso_e/125.0, 1.0), text=f"T1 (125 kWh): {min((conso_e/125)*100, 100):.1f}%")
        c2.progress(min(max((conso_e-125)/125.0, 0), 1.0), text=f"T2 (125 kWh): {min(max((conso_e-125)/1.25, 0), 100):.1f}%")
        c3.progress(min(max((conso_e-250)/1000.0, 0), 1.0), text=f"T3 (Supp): {max((conso_e-250)/10, 0):.1f}%")

        st.subheader("Tranches Gaz")
        g1, g2, g3 = st.columns(3)
        conso_g = gaz_data['total_jour']
        g1.progress(min(conso_g/1125.0, 1.0), text=f"T1 (1125 m³): {min((conso_g/1125)*100, 100):.1f}%")
        g2.progress(min(max((conso_g-1125)/1375.0, 0), 1.0), text=f"T2 (1375 m³): {min(max((conso_g-1125)/13.75, 0), 100):.1f}%")
        g3.progress(min(max((conso_g-2500)/1000.0, 0), 1.0), text=f"T3 (Supp): {max((conso_g-2500)/10, 0):.1f}%")
    else:
        st.warning("Aucune donnée disponible. Appuyez sur 'Rafraîchir'.")

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
elif page == "Supervision Temps Réel":
    page_supervision(selected_id, client_info)
