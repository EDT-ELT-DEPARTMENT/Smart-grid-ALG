import streamlit as st
import sqlite3
import io
from datetime import datetime, timedelta
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="SONELGAZ - Facturation", layout="wide")
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

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
    cursor.execute('SELECT nom, client_num, lieu_conso, facture_num, index_elec, index_gaz FROM abonnes WHERE reference_contrat = ?', (selected_ref,))
    client_data = cursor.fetchone()

    if client_data:
        nom, client_num, lieu_conso, fact_num, index_elec, index_gaz = client_data
        # Calculs détaillés
        cons_elec = 562.0
        cons_gaz = 2708.40
        montant_ht_elec = 2246.04
        montant_ht_gaz = 719.30
        abonnement = 164.16
        tva_9 = 138.99
        tva_19 = 301.19
        droit_fixe = 200.00
        taxe_hab = 200.00
        net_ttc = 3969.68
        timbre = 40.00
        total_espece = 4009.68
        
        date_facture = "11/06/2026"
        prochain_releve = "06/09/2026"

        facture_html = f"""
<div style="border: 2px solid #e67e22; padding: 20px; font-family: Arial, sans-serif;">
<h2 style="color: #e67e22; text-align: center;">SONELGAZ - Facture de Consommation</h2>
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
    <tr style="background-color: #f9e79f;">
        <th style="border: 1px solid #000; padding: 8px;">Service</th>
        <th style="border: 1px solid #000; padding: 8px;">Consommation</th>
        <th style="border: 1px solid #000; padding: 8px;">Montant HT (DA)</th>
    </tr>
    <tr>
        <td style="border: 1px solid #000; padding: 8px;">Électricité (Tranches 1, 2, 3)</td>
        <td style="border: 1px solid #000; padding: 8px;">{cons_elec} kWh</td>
        <td style="border: 1px solid #000; padding: 8px;">{montant_ht_elec:.2f}</td>
    </tr>
    <tr>
        <td style="border: 1px solid #000; padding: 8px;">Gaz (Tranches 1, 2, 3)</td>
        <td style="border: 1px solid #000; padding: 8px;">{cons_gaz} Th</td>
        <td style="border: 1px solid #000; padding: 8px;">{montant_ht_gaz:.2f}</td>
    </tr>
</table>
<div style="margin-top: 20px;">
    <p>Redevance fixe HT : {abonnement} DA</p>
    <p>TVA (9% + 19%) : {(tva_9 + tva_19):.2f} DA</p>
    <p>Droit fixe & Taxe habitation : {(droit_fixe + taxe_hab):.2f} DA</p>
    <hr>
    <h3 style="text-align: right; color: #d35400;">Net à payer TTC : {net_ttc:.2f} DA</h3>
    <p style="text-align: right;">Total avec timbre (espèces) : {total_espece:.2f} DA</p>
</div>
</div>
"""
        st.markdown(facture_html, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
        def generate_pdf(html_content):
            result = io.BytesIO()
            pisa.CreatePDF(html_content, dest=result)
            return result.getvalue()
        col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")
