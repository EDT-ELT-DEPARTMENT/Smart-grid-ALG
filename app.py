import streamlit as st
import sqlite3
import io
from datetime import datetime
from xhtml2pdf import pisa

# Configuration de l'interface (bleue)
st.set_page_config(page_title="SONELGAZ - Facturation", layout="wide")
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# Simulation de données (identiques aux détails de votre facture)
data = {
    "nom": "MME BELASKRI ASMA",
    "client_num": "7314P001114",
    "lieu_conso": "01 BLOC B CT 70 LOGTS UDL",
    "fact_num": "733260603359",
    "date": "11/06/2026",
    "releve": "06/09/2026",
    "elec_ht": 2246.04,
    "gaz_ht": 719.30,
    "redevance": 164.16,
    "tva_9": 138.99,
    "tva_19": 301.19,
    "droit": 200.0,
    "taxe": 200.0,
    "net_ttc": 3969.68,
    "total_espece": 4009.68
}

# Rendu HTML avec style bleu
facture_html = f"""
<div style="border: 2px solid #2980b9; padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Facture de Consommation</h2>
    <p><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
    <p><strong>Abonné :</strong> {data['nom']} | <strong>Lieu :</strong> {data['lieu_conso']}</p>
    <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
        <tr style="background-color: #d6eaf8;"><th>Service</th><th>Montant HT (DA)</th></tr>
        <tr><td>Électricité (Total Tranches)</td><td>{data['elec_ht']:.2f}</td></tr>
        <tr><td>Gaz (Total Tranches)</td><td>{data['gaz_ht']:.2f}</td></tr>
    </table>
    <div style="margin-top: 10px;">
        <p>Redevance fixe : {data['redevance']} | TVA (9%+19%) : {(data['tva_9']+data['tva_19']):.2f}</p>
        <p>Taxes (Fixe + Habitation) : {(data['droit']+data['taxe']):.2f}</p>
        <h3 style="color: #2980b9; text-align: right;">Net à payer : {data['net_ttc']:.2f} DA</h3>
    </div>
</div>
"""

st.markdown(facture_html, unsafe_allow_html=True)

# Boutons de téléchargement
col1, col2 = st.columns(2)
col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")

def generate_pdf(html):
    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result)
    return result.getvalue()

col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")
