import streamlit as st
import io
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="SONELGAZ - Facturation Smart", layout="wide")
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# --- DONNÉES DÉTAILLÉES ---
data = {
    "nom": "MME BELASKRI ASMA",
    "client_num": "7314P001114",
    "lieu_conso": "01 BLOC B CT 70 LOGTS UDL",
    "fact_num": "733260603359",
    "elec": [
        {"tranche": "Tranche 1", "qte": "125.0", "prix": "1.7787", "mt": "744.70"},
        {"tranche": "Tranche 2", "qte": "125.0", "prix": "4.1789", "mt": "744.70"},
        {"tranche": "Tranche 3", "qte": "312.0", "prix": "4.8120", "mt": "1501.34"}
    ],
    "gaz": [
        {"tranche": "Tranche 1", "qte": "1125.0", "prix": "0.1682", "mt": "635.42"},
        {"tranche": "Tranche 2", "qte": "1375.0", "prix": "0.3245", "mt": "635.42"},
        {"tranche": "Tranche 3", "qte": "208.4", "prix": "0.4025", "mt": "83.88"}
    ],
    "redevance": "164.16",
    "tva_9": "138.99",
    "tva_19": "301.19",
    "droit_fixe": "200.00",
    "taxe_hab": "200.00",
    "net_ttc": "3969.68"
}

# --- STYLES ---
table_style = "width:100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 20px;"
th_style = "border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; text-align: center; color: #2980b9;"
td_style = "border: 1px solid #2980b9; padding: 10px; text-align: center;"

# --- CONSTRUCTION HTML ---
facture_html = f"""
<div style="border: 2px solid #2980b9; padding: 25px; font-family: Arial, sans-serif; background-color: #ffffff;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation Smart</h2>
    <div style="margin-bottom: 20px;">
        <p><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
        <p><strong>Abonné :</strong> {data['nom']} | <strong>Lieu de consommation :</strong> {data['lieu_conso']}</p>
    </div>
    
    <h3 style="color: #2980b9;">Électricité</h3>
    <table style="{table_style}">
        <tr>
            <th style="{th_style}">Tranche</th>
            <th style="{th_style}">Quantité (kWh)</th>
            <th style="{th_style}">Prix Unitaire (DA)</th>
            <th style="{th_style}">Montant HT (DA)</th>
        </tr>
        {"".join([f"<tr><td style='{td_style}'>{i['tranche']}</td><td style='{td_style}'>{i['qte']}</td><td style='{td_style}'>{i['prix']}</td><td style='{td_style}'>{i['mt']}</td></tr>" for i in data['elec']])}
    </table>

    <h3 style="color: #2980b9;">Gaz</h3>
    <table style="{table_style}">
        <tr>
            <th style="{th_style}">Tranche</th>
            <th style="{th_style}">Quantité (Th)</th>
            <th style="{th_style}">Prix Unitaire (DA)</th>
            <th style="{th_style}">Montant HT (DA)</th>
        </tr>
        {"".join([f"<tr><td style='{td_style}'>{i['tranche']}</td><td style='{td_style}'>{i['qte']}</td><td style='{td_style}'>{i['prix']}</td><td style='{td_style}'>{i['mt']}</td></tr>" for i in data['gaz']])}
    </table>

    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 15px;">
        <p><strong>Redevance fixe :</strong> {data['redevance']} DA</p>
        <p><strong>Détail Taxes :</strong> TVA 9% ({data['tva_9']} DA) | TVA 19% ({data['tva_19']} DA) | Droit fixe ({data['droit_fixe']} DA) | Taxe habitation ({data['taxe_hab']} DA)</p>
        <h2 style="color: #2980b9; text-align: right; margin-top: 20px;">Net à payer : {data['net_ttc']} DA</h2>
    </div>
</div>
"""

# --- AFFICHAGE ET ACTIONS ---
st.markdown(facture_html, unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns(2)

col1.download_button("Télécharger HTML", facture_html, "facture_smart.html", "text/html")

def generate_pdf(html_content):
    result = io.BytesIO()
    pisa.CreatePDF(html_content, dest=result)
    return result.getvalue()

col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture_smart.pdf", "application/pdf")
