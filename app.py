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
        # Injection des valeurs de la facture (562 kWh et 2708.40 Th)
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

# --- FONCTIONS DE CALCUL (Basées sur la facture Sonelgaz) ---
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
    
    # 3. Taxes et Redevances Exactes
    redevance_fixe_ht = 164.16
    tva_9 = 138.99 
    tva_19 = 301.19
    droit_fixe = 200.00
    taxe_habitation = 200.00
    timbre = 40.00
    
    total_ht = ht_elec + ht_gaz
    total_taxes = redevance_fixe_ht + tva_9 + tva_19 + droit_fixe + taxe_habitation
    
    # Net à payer et espèces
    net_ttc = total_ht + total_taxes
    total_especes = net_ttc + timbre
    
    details_taxes = {
        "Redevances fixes HT": redevance_fixe_ht,
        "TVA 9%": tva_9,
        "TVA 19%": tva_19,
        "Droit Fixe": droit_fixe,
        "Taxe habitation": taxe_habitation,
        "Timbre": timbre
    }
    
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
st.sidebar.markdown("**Smart-Grid SONELGAZ : Supervision Temps Réel et Facturation**")

selected_id = st.sidebar.selectbox("Choisir un abonné :", list(CLIENTS.keys()))
client_info = CLIENTS[selected_id]

mode_acquisition = st.sidebar.radio("Mode d'acquisition :", ["Mode Simulation", "Mode Réel (Carte TTGO)"])
page = st.sidebar.radio("Navigation", ["Facturation", "Supervision Temps Réel"])

# --- PAGE 1 : FACTURATION ---
def page_facturation(client_id, info):
    st.title("Smart-Grid SONELGAZ : Facturation Détaillée")
    st.info(f"**Client :** {info['nom']} | **N° Client :** {client_id} | **N° Facture :** {info['facture']} | **Lieu :** {info['lieu']}")

    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz = get_live_data(client_id, "Gaz")

    data_elec, data_gaz, ht_elec, ht_gaz, total_ht, taxes, net_ttc, total_especes, det_taxes = calculer_facture(conso_elec, conso_gaz)

    facture_html = f"""
    <style>
        .invoice-box {{ font-family: 'Arial', sans-serif; padding: 25px; border: 1px solid #d1d1d1; background: #fff; }}
        .header {{ background-color: #004a99; color: white; padding: 15px; text-align: center; margin-bottom: 20px; }}
        .client-section {{ background-color: #f8f9fa; padding: 15px; border-left: 5px solid #004a99; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; }}
        th {{ background-color: #005bb5; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        .summary {{ background-color: #eef6ff; padding: 15px; border: 1px solid #004a99; margin-top: 20px; }}
        .grid-container {{ display: flex; justify-content: space-between; }}
        .tax-box {{ width: 48%; }}
    </style>
    <div class="invoice-box">
        <div class="header"><h2>SONELGAZ - Facture de consommation</h2></div>
        
        <div class="client-section">
            <p><strong>Nom du client :</strong> {info['nom']}</p>
            <p><strong>N° Client :</strong> {client_id}</p>
            <p><strong>N° Facture :</strong> {info['facture']}</p>
            <p><strong>Lieu de consommation :</strong> {info['lieu']}</p>
        </div>
        
        <h3>⚡ Électricité ({conso_elec:.2f} kWh)</h3>
        <table>
            <tr><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_elec])}
        </table>
        
        <h3>🔥 Gaz ({conso_gaz:.2f} Th)</h3>
        <table>
            <tr><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
            {"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']:.2f}</td><td>{i['prix']:.4f}</td><td>{i['mt']:.2f}</td></tr>" for i in data_gaz])}
        </table>
        
        <div class="summary">
            <div class="grid-container">
                <div class="tax-box">
                    <h4>Détail des Taxes et Redevances</h4>
                    <p>Redevances fixes HT : {det_taxes['Redevances fixes HT']:.2f} DA</p>
                    <p>TVA à 9% : {det_taxes['TVA 9%']:.2f} DA</p>
                    <p>TVA à 19% : {det_taxes['TVA 19%']:.2f} DA</p>
                    <p>Droit Fixe sur consommation : {det_taxes['Droit Fixe']:.2f} DA</p>
                    <p>Taxe habitation : {det_taxes['Taxe habitation']:.2f} DA</p>
                </div>
                <div class="tax-box">
                    <h4>Récapitulatif Financier</h4>
                    <p>Total Montant HT : <strong>{total_ht:.2f} DA</strong></p>
                    <p>Total Taxes : <strong>{taxes:.2f} DA</strong></p>
                    <h3 style="color: #004a99; margin-bottom: 5px;">NET À PAYER TTC : {net_ttc:.2f} DA</h3>
                    <p>Timbre (paiement en espèce) : {det_taxes['Timbre']:.2f} DA</p>
                    <h3 style="color: #c0392b; margin-top: 5px;">TOTAL À PAYER (espèces) : {total_especes:.2f} DA</h3>
                </div>
            </div>
        </div>
    </div>
    """
    
    components.html(facture_html, height=1050, scrolling=True)

    def generate_pdf(html_string):
        result = io.BytesIO()
        pisa.CreatePDF(html_string, dest=result, encoding='utf-8')
        return result.getvalue()

    col1, col2 = st.columns(2)
    col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
    col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")

# --- PAGE 2 : SUPERVISION ---
def page_supervision(client_id, info):
    st.title("Smart-Grid SONELGAZ : Plateforme de Supervision et de Facturation")
    st.subheader(f"Supervision par Impulsions : {info['nom']} (Client: {client_id})")

    # --- FACTEURS DE CONVERSION ---
    # ÉLECTRICITÉ : À vérifier sur votre compteur (ex: 1000 imp/kWh = 0.001)
    FACTEUR_IMP_ELEC_KWH = 0.001 
    
    # GAZ : Spécifique à votre compteur GALLUS 2000 et à Sonelgaz
    FACTEUR_IMP_GAZ_M3 = 0.01  # 1 impulsion = 10 dm3 = 0.01 m3
    COEF_SONELGAZ_PCS = 9.73   # Coefficient (Th/m3) - À lire sur votre facture !

    # Initialisation des compteurs d'impulsions brutes
    if 'imp_elec' not in st.session_state: st.session_state.imp_elec = 0
    if 'imp_gaz' not in st.session_state: st.session_state.imp_gaz = 0

    # --- GESTION DES MODES D'ACQUISITION ---
    if mode_acquisition == "Mode Simulation":
        st.info("🔧 **Mode Simulation** : Génération d'impulsions aléatoires.")
        
        if st.button("Simuler réception impulsions"):
            nouvelles_imp_elec = random.randint(1, 5)
            nouvelles_imp_gaz = random.randint(1, 3)

            # Calculs de conversion d'énergie
            energie_elec_kwh = nouvelles_imp_elec * FACTEUR_IMP_ELEC_KWH
            
            volume_gaz_m3 = nouvelles_imp_gaz * FACTEUR_IMP_GAZ_M3
            energie_gaz_th = volume_gaz_m3 * COEF_SONELGAZ_PCS

            last_elec = get_live_data(client_id, "Elec")
            last_gaz = get_live_data(client_id, "Gaz")

            conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
            c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # On stocke l'énergie convertie (kWh et Th) dans le total_jour
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", 
                      (now, "Elec", nouvelles_imp_elec, last_elec + energie_elec_kwh, client_id))
            c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", 
                      (now, "Gaz", nouvelles_imp_gaz, last_gaz + energie_gaz_th, client_id))
            conn.commit()
            conn.close()
            st.rerun()
            
    elif mode_acquisition == "Mode Réel (Carte TTGO)":
        st.success("📡 **Mode Réel (IoT)** : Réception d'impulsions depuis l'ESP32.")
        ip_ttgo = st.text_input("Adresse IP de la carte TTGO :", "192.168.1.50")
        
        if st.button("Acquérir les impulsions depuis la TTGO"):
            try:
                response = requests.get(f"http://{ip_ttgo}/impulsions", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    nouvelles_imp_elec = int(data.get('imp_elec', 0))
                    nouvelles_imp_gaz = int(data.get('imp_gaz', 0))

                    # Calculs de conversion d'énergie
                    energie_elec_kwh = nouvelles_imp_elec * FACTEUR_IMP_ELEC_KWH
                    volume_gaz_m3 = nouvelles_imp_gaz * FACTEUR_IMP_GAZ_M3
                    energie_gaz_th = volume_gaz_m3 * COEF_SONELGAZ_PCS

                    last_elec = get_live_data(client_id, "Elec")
                    last_gaz = get_live_data(client_id, "Gaz")

                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
                    c = conn.cursor()
                    c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", 
                              (now, "Elec", nouvelles_imp_elec, last_elec + energie_elec_kwh, client_id))
                    c.execute("INSERT INTO mesures VALUES (?, ?, ?, ?, ?)", 
                              (now, "Gaz", nouvelles_imp_gaz, last_gaz + energie_gaz_th, client_id))
                    conn.commit()
                    conn.close()
                    st.toast("✅ Impulsions acquises et converties avec succès !")
                    st.rerun()
                else:
                    st.error(f"⚠️ Erreur de communication. Code HTTP: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Erreur réseau : {e}")

    # --- DASHBOARD IMPULSIONS ---
    conn = sqlite3.connect('monitoring_energie.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM mesures WHERE client_id=? ORDER BY timestamp DESC LIMIT 20", conn, params=(client_id,))
    conn.close()

    elec_val = 0.0
    gaz_val = 0.0
    if not df.empty:
        df_elec = df[df['type_energie'] == 'Elec']
        df_gaz = df[df['type_energie'] == 'Gaz']
        if not df_elec.empty: elec_val = df_elec.iloc[0]['total_jour']
        if not df_gaz.empty: gaz_val = df_gaz.iloc[0]['total_jour']

    st.markdown("### 📊 État du Comptage (Impulsions)")
    col_grid1, col_grid2 = st.columns(2)
    # On recalcule le nombre total d'impulsions à partir de la valeur en base
    col_grid1.metric("⚡ Total Impulsions Élec", f"{int(elec_val / FACTEUR_IMPULSION)} pulses")
    col_grid2.metric("🔥 Total Impulsions Gaz", f"{int(gaz_val / FACTEUR_IMPULSION)} pulses")
    st.divider()

    # --- AFFICHAGE DES DONNÉES DE CONSOMMATION ---
    if not df.empty:
        data_elec, data_gaz, _, _, _, _, _, _, _ = calculer_facture(elec_val, gaz_val)

        # Tranches Électricité
        st.markdown("### ⚡ Consommation Électricité par Tranche")
        cols_e = st.columns(3)
        for i, tranche in enumerate(data_elec):
            limit = 125.0 if i==0 else 125.0 if i==1 else 1000.0
            cols_e[i].metric(tranche['tranche'], f"{tranche['qte']:.2f} kWh")
            cols_e[i].progress(min(tranche['qte'] / limit, 1.0))

        st.markdown("---")

        # Tranches Gaz
        st.markdown("### 🔥 Consommation Gaz par Tranche")
        cols_g = st.columns(3)
        for i, tranche in enumerate(data_gaz):
            limit = 1125.0 if i==0 else 1375.0 if i==1 else 1000.0
            cols_g[i].metric(tranche['tranche'], f"{tranche['qte']:.2f} Th")
            cols_g[i].progress(min(tranche['qte'] / limit, 1.0))

        st.markdown("---")
        
        st.subheader("Évolution Historique (Dernières lectures)")
        col1, col2 = st.columns(2)
        with col1: 
            st.write("Électricité (Unités Cumulées)")
            if not df_elec.empty: st.line_chart(df_elec.set_index('timestamp')['total_jour'])
        with col2: 
            st.write("Gaz (Unités Cumulées)")
            if not df_gaz.empty: st.line_chart(df_gaz.set_index('timestamp')['total_jour'])
    else: 
        st.warning("Données indisponibles.")

# --- ROUTAGE ---
if page == "Facturation":
    page_facturation(selected_id, client_info)
elif page == "Supervision Temps Réel":
    page_supervision(selected_id, client_info)
