import streamlit as st
import sqlite3
import io
from datetime import datetime
from xhtml2pdf import pisa
import streamlit as st
import io
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="SONELGAZ - Facturation", layout="wide")

# Titre requis pour la plateforme
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

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

# --- CONSTRUCTION DU HTML ---
# Ajout de styles CSS pour assurer un affichage propre des tableaux
style_table = "width:100%; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed;"
style_th = "border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; text-align: center; color: #2980b9;"
style_td = "border: 1px solid #2980b9; padding: 10px; text-align: center;"

facture_html = f"""
<div style="border: 2px solid #2980b9; padding: 25px; font-family: Arial, sans-serif; background-color: #ffffff;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation</h2>
    
    <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #d6eaf8; background-color: #fcfcfc;">
        <p><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
        <p><strong>Abonné :</strong> {data['nom']} | <strong>Lieu de consommation :</strong> {data['lieu_conso']}</p>
    </div>

    <h3 style="color: #2980b9;">Électricité</h3>
    <table style="{style_table}">
        <tr style="background-color: #d6eaf8;">
            <th style="{style_th}">Tranche</th>
            <th style="{style_th}">Quantité (kWh)</th>
            <th style="{style_th}">Prix Unitaire (DA)</th>
            <th style="{style_th}">Montant HT (DA)</th>
        </tr>
        {"".join([f"<tr><td style='{style_td}'>{i['tranche']}</td><td style='{style_td}'>{i['qte']}</td><td style='{style_td}'>{i['prix']}</td><td style='{style_td}'>{i['mt']}</td></tr>" for i in data['elec']])}
    </table>

    <h3 style="color: #2980b9;">Gaz</h3>
    <table style="{style_table}">
        <tr style="background-color: #d6eaf8;">
            <th style="{style_th}">Tranche</th>
            <th style="{style_th}">Quantité (Th)</th>
            <th style="{style_th}">Prix Unitaire (DA)</th>
            <th style="{style_th}">Montant HT (DA)</th>
        </tr>
        {"".join([f"<tr><td style='{style_td}'>{i['tranche']}</td><td style='{style_td}'>{i['qte']}</td><td style='{style_td}'>{i['prix']}</td><td style='{style_td}'>{i['mt']}</td></tr>" for i in data['gaz']])}
    </table>

    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 15px;">
        <p><strong>Redevance fixe :</strong> {data['redevance']} DA | <strong>Taxes :</strong> TVA 9% ({data['tva_9']} DA) | TVA 19% ({data['tva_19']} DA)</p>
        <p><strong>Droit fixe :</strong> {data['droit']} DA | <strong>Taxe habitation :</strong> {data['taxe']} DA</p>
        <h2 style="color: #2980b9; text-align: right; margin-top: 20px;">Net à payer : {data['net_ttc']:.2f} DA</h2>
    </div>
</div>
"""

# --- AFFICHAGE ---
st.markdown(facture_html, unsafe_allow_html=True)

# --- FONCTION POUR PDF ---
def generate_pdf(html):
    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result)
    return result.getvalue()

# --- TÉLÉCHARGEMENT ---
st.markdown("---")
st.write("### Options d'exportation")
col1, col2 = st.columns(2)

col1.download_button(
    label="Télécharger HTML", 
    data=facture_html, 
    file_name="facture.html", 
    mime="text/html"
)

col2.download_button(
    label="Télécharger PDF", 
    data=generate_pdf(facture_html), 
    file_name="facture.pdf", 
    mime="application/pdf"
)
