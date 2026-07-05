import streamlit as st
import sqlite3
import io
from datetime import datetime, timedelta
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="SONELGAZ - Facturation", layout="wide")
st.title("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")
st.subheader("")

# --- DATABASE ---
def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS abonnes')
    cursor.execute('''CREATE TABLE IF NOT EXISTS abonnes (
                        reference_contrat TEXT PRIMARY KEY, 
                        nom TEXT, 
                        client_num TEXT,
                        lieu_conso TEXT,
                        facture_num TEXT,
                        index_elec REAL, 
                        index_gaz REAL)''')
    cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?, ?, ?, ?)', 
                   ("SNG-2026-001", "MME BELASKRI ASMA", "7314P001114", "01 BLOC B CT 70 LOGTS UDL", "733260603359", 5562.0, 2708.4))
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# --- SÉLECTION ---
cursor.execute('SELECT reference_contrat, nom FROM abonnes')
clients = cursor.fetchall()
if clients:
    client_options = {f"{row[0]} - {row[1]}": row[0] for row in clients}
    selected_label = st.selectbox("Sélectionnez un abonné :", list(client_options.keys()))
    selected_ref = client_options[selected_label]
    cursor.execute('SELECT nom, client_num, lieu_conso, facture_num FROM abonnes WHERE reference_contrat = ?', (selected_ref,))
    client_data = cursor.fetchone()

    if client_data:
        nom, client_num, lieu_conso, fact_num = client_data
        
        # Données détaillées extraites de CamScanner 30-06-2026 18.29_2.pdf[cite: 2]
        date_facture = "11/06/2026"
        prochain_releve = "06/09/2026"
        
        # Électricité[cite: 2]
        elec_tranche1 = 125.00
        elec_tranche2 = 125.00
        elec_tranche3 = 312.00
        montant_elec_ht_9 = 744.70
        montant_elec_ht_19 = 1501.34
        
        # Gaz[cite: 2]
        gaz_tranche1 = 1125.00
        gaz_tranche2 = 1375.00
        gaz_tranche3 = 208.40
        montant_gaz_ht_9 = 635.42
        montant_gaz_ht_19 = 83.88
        
        # Taxes et Frais[cite: 2]
        redevance_fixe = 164.16
        tva_9 = 138.99
        tva_19 = 301.19
        droit_fixe = 200.00
        taxe_habitation = 200.00
        net_ttc = 3969.68
        timbre = 40.00
        total_espece = 4009.68

        # --- CODE HTML ---
        facture_html = f"""
<div style="border: 2px solid #2980b9; padding: 20px; font-family: Arial, sans-serif;">
<h2 style="color: #2980b9; text-align: center;">SONELGAZ - Facture de Consommation</h2>
<div style="display: flex; justify-content: space-between;">
    <div>
        <p><strong>Facture n°:</strong> {fact_num}</p>
        <p><strong>Etablie le:</strong> {date_facture}</p>
        <p><strong>Client n°:</strong> {client_num}</p>
    </div>
    <div>
        <p><strong>Abonné :</strong> {nom}</p>
        <p><strong>Lieu de consommation :</strong> {lieu_conso}</p>
        <p><strong>Prochaine relève :</strong> {prochain_releve}</p>
    </div>
</div>

<table style="width:100%; border-collapse: collapse; margin-top: 20px;">
    <tr style="background-color: #d6eaf8;">
        <th style="border: 1px solid #000; padding: 8px;">Détails Consommation</th>
        <th style="border: 1px solid #000; padding: 8px;">Quantité</th>
        <th style="border: 1px solid #000; padding: 8px;">Montant HT (DA)</th>
    </tr>
    <tr><td colspan="3" style="background-color: #f2f2f2; font-weight: bold;">ÉLECTRICITÉ</td></tr>
    <tr><td>Tranche 1</td><td>{elec_tranche1} kWh</td><td>-</td></tr>
    <tr><td>Tranche 2</td><td>{elec_tranche2} kWh</td><td>-</td></tr>
    <tr><td>Tranche 3</td><td>{elec_tranche3} kWh</td><td>-</td></tr>
    <tr><td>Total HT (9% & 19%)</td><td>-</td><td>{montant_elec_ht_9 + montant_elec_ht_19:.2f}</td></tr>
    
    <tr><td colspan="3" style="background-color: #f2f2f2; font-weight: bold;">GAZ</td></tr>
    <tr><td>Tranche 1</td><td>{gaz_tranche1} Th</td><td>-</td></tr>
    <tr><td>Tranche 2</td><td>{gaz_tranche2} Th</td><td>-</td></tr>
    <tr><td>Tranche 3</td><td>{gaz_tranche3} Th</td><td>-</td></tr>
    <tr><td>Total HT (9% & 19%)</td><td>-</td><td>{montant_gaz_ht_9 + montant_gaz_ht_19:.2f}</td></tr>
</table>

<div style="margin-top: 20px; border-top: 1px solid #000; padding-top: 10px;">
    <p>Redevance fixe HT : {redevance_fixe} DA</p>
    <p>TVA 9% : {tva_9} DA | TVA 19% : {tva_19} DA</p>
    <p>Droit fixe sur consommation : {droit_fixe} DA</p>
    <p>Taxe d'habitation : {taxe_habitation} DA</p>
    <h3 style="text-align: right; color: #2980b9;">Net à payer TTC : {net_ttc:.2f} DA</h3>
    <p style="text-align: right;">Total avec timbre (espèces) : {total_espece:.2f} DA</p>
</div>
</div>
"""
        st.markdown(facture_html, unsafe_allow_html=True)
        
        # --- TÉLÉCHARGEMENT ---
        col1, col2 = st.columns(2)
        col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
        def generate_pdf(html_content):
            result = io.BytesIO()
            pisa.CreatePDF(html_content, dest=result)
            return result.getvalue()
        col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")
