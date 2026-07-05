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

# --- FONCTIONS DE CALCUL (Mise à jour pour précision) ---
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
    
    # 3. Taxes et Redevances (Révision du calcul)
    # Redevances fixes (ex: 200 DA)
    redevance_fixe = 200.0
    # TVA (9% sur électricité, 19% sur Gaz + Redevance)
    tva = (ht_elec * 0.09) + ((ht_gaz + redevance_fixe) * 0.19)
    # Taxe habitation fixe
    taxe_habitation = 150.0
    
    total_taxes = redevance_fixe + tva + taxe_habitation
    total_ht = ht_elec + ht_gaz
    total_ttc = total_ht + total_taxes
    
    return data_elec, data_gaz, ht_elec, ht_gaz, total_ht, total_taxes, total_ttc

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
    st.info(f"**Client :** {info['nom']} | **N° Facture :** {info['facture']} | **Lieu :** {info['lieu']}")

    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")

    data_elec, data_gaz, ht_elec, ht_gaz, total_ht, taxes, net_ttc = calculer_facture(conso_elec, conso_gaz)

    # HTML design Bleu
    facture_html = f"""
    <style>
        .invoice-box {{ font-family: 'Arial', sans-serif; padding: 25px; border: 1px solid #d1d1d1; background: #fff; }}
        .header {{ background-color: #004a99; color: white; padding: 15px; text-align: center; margin-bottom: 20px; }}
        .client-section {{ background-color: #f8f9fa; padding: 15px; border-left: 5px solid #004a99; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th {{ background-color: #005bb5; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        .summary {{ background-color: #eef6ff; padding: 15px; border: 1px solid #004a99; }}
    </style>
    <div class="invoice-box">
        <div class="header"><h2>SONELGAZ - Détail de Facturation</h2></div>
        <div class="client-section">
            <p><strong>Nom du client :</strong> {info['nom']}</p>
            <p><strong>N° de Facture :</strong> {info['facture']}</p>
            <p><strong>Adresse :</strong> {info['lieu']}</p>
        </div>
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
        <div class="summary">
            <p>Total HT Électricité : {ht_elec:.2f} DA</p>
            <p>Total HT Gaz : {ht_gaz:.2f} DA</p>
            <p><strong>TOTAL GLOBAL HT : {total_ht:.2f} DA</strong></p>
            <p>Taxes et Redevances : {taxes:.2f} DA</p>
            <h2 style="color: #004a99;">NET À PAYER (TTC) : {net_ttc:.2f} DA</h2>
        </div>
    </div>
    """
    components.html(facture_html, height=800, scrolling=True)

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
    st.subheader(f"Supervision Temps Réel : {info['nom']}")

    if st.button("Rafraîchir les données"):
        conn = sqlite3.connect('monitoring_energie.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Elec", random.uniform(1.0, 4.0), random.uniform(50, 400), client_id))
        c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", (now, "Gaz", random.uniform(0.5, 1.5), random.uniform(5, 50), client_id))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('monitoring_energie.db')
    df = pd.read_sql_query("SELECT * FROM mesures WHERE client_id=? ORDER BY timestamp DESC LIMIT 10", conn, params=(client_id,))
    conn.close()

    if not df.empty:
        elec_val = df[df['type_energie'] == 'Elec'].iloc[0]['total_jour']
        gaz_val = df[df['type_energie'] == 'Gaz'].iloc[0]['total_jour']

        # Calculer les tranches pour l'affichage temps réel
        data_elec, data_gaz, _, _, _, _, _ = calculer_facture(elec_val, gaz_val)

        st.subheader("Tranches Électricité")
        cols = st.columns(3)
        for i, tranche in enumerate(data_elec):
            cols[i].metric(tranche['tranche'], f"{tranche['qte']:.2f} kWh")
            cols[i].progress(min(tranche['qte'] / (125 if i==0 else 125 if i==1 else 1000), 1.0))

        st.subheader("Tranches Gaz")
        cols = st.columns(3)
        for i, tranche in enumerate(data_gaz):
            cols[i].metric(tranche['tranche'], f"{tranche['qte']:.2f} m³")
            cols[i].progress(min(tranche['qte'] / (1125 if i==0 else 1375 if i==1 else 1000), 1.0))

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
elif page == "Supervision Temps Réel":
    page_supervision(selected_id, client_info)
