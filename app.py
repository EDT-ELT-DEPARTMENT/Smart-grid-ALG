import streamlit as st
import sqlite3
import io
from datetime import datetime
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="SONELGAZ - Facturation", layout="wide")
st.title("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")
# --- DONNÉES ---
data = {
    "nom": "MME BELASKRI ASMA",
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

# --- CONSTRUCTION DU HTML (Désindenté pour le rendu) ---
facture_html = f"""
<div style="border: 2px solid #2980b9; padding: 20px; font-family: Arial, sans-serif;">
<h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation</h2>
<p><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
<p><strong>Abonné :</strong> {data['nom']} | <strong>Lieu :</strong> {data['lieu_conso']}</p>
<h3 style="color: #2980b9;">Électricité</h3>
<table style="width:100%; border-collapse: collapse;">
<tr style="background-color: #d6eaf8;"><th>Tranche</th><th>Quantité</th><th>Prix Unitaire</th><th>Montant HT</th></tr>
{"".join([f"<tr><td>{i['tranche']}</td><td>{i['qte']}</td><td>{i['prix']}</td><td>{i['mt']}</td></tr>" for i in data['elec']])}
</table>
<h3 style="color: #2980b9;">Gaz</h3>
<table style="width:100%; border-collapse: collapse;">
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

# --- AFFICHAGE ---
st.markdown(facture_html, unsafe_allow_html=True)

# --- TÉLÉCHARGEMENT ---
col1, col2 = st.columns(2)
col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")
def generate_pdf(html):
    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result)
    return result.getvalue()
col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")
