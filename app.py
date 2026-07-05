import streamlit as st
import io
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="Plateforme de Facturation Smart", layout="wide")

st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# --- DONNÉES ---
fact_num = "733260603359"
client_num = "7314P001114"
nom = "MME BELASKRI ASMA"
lieu = "01 BLOC B CT 70 LOGTS UDL"

# --- STYLE ---
table_style = "width:100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 20px;"
th_style = "border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; text-align: center; color: #2980b9;"
td_style = "border: 1px solid #2980b9; padding: 10px; text-align: center;"

# --- CONSTRUCTION HTML ---
html_content = f"""
<div style="border: 2px solid #2980b9; padding: 25px; font-family: Arial, sans-serif; background-color: #ffffff;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation Smart</h2>
    <div style="margin-bottom: 20px;">
        <p><strong>Facture n°:</strong> {fact_num} | <strong>Client n°:</strong> {client_num}</p>
        <p><strong>Abonné :</strong> {nom} | <strong>Lieu de consommation :</strong> {lieu}</p>
    </div>

    <h3 style="color: #2980b9;">Électricité</h3>
    <table style="{table_style}">
        <tr>
            <th style="{th_style}">Tranche</th>
            <th style="{th_style}">Quantité (kWh)</th>
            <th style="{th_style}">Prix Unitaire (DA)</th>
            <th style="{th_style}">Montant HT (DA)</th>
        </tr>
        <tr><td style="{td_style}">Tranche 1</td><td style="{td_style}">125.0</td><td style="{td_style}">1.7787</td><td style="{td_style}">744.70</td></tr>
        <tr><td style="{td_style}">Tranche 2</td><td style="{td_style}">125.0</td><td style="{td_style}">4.1789</td><td style="{td_style}">744.70</td></tr>
        <tr><td style="{td_style}">Tranche 3</td><td style="{td_style}">312.0</td><td style="{td_style}">4.8120</td><td style="{td_style}">1501.34</td></tr>
    </table>

    <h3 style="color: #2980b9;">Gaz</h3>
    <table style="{table_style}">
        <tr>
            <th style="{th_style}">Tranche</th>
            <th style="{th_style}">Quantité (Th)</th>
            <th style="{th_style}">Prix Unitaire (DA)</th>
            <th style="{th_style}">Montant HT (DA)</th>
        </tr>
        <tr><td style="{td_style}">Tranche 1</td><td style="{td_style}">1125.0</td><td style="{td_style}">0.1682</td><td style="{td_style}">635.42</td></tr>
        <tr><td style="{td_style}">Tranche 2</td><td style="{td_style}">1375.0</td><td style="{td_style}">0.3245</td><td style="{td_style}">635.42</td></tr>
        <tr><td style="{td_style}">Tranche 3</td><td style="{td_style}">208.4</td><td style="{td_style}">0.4025</td><td style="{td_style}">83.88</td></tr>
    </table>

    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 15px;">
        <p><strong>Redevance fixe :</strong> 164.16 DA</p>
        <p><strong>Détail Taxes :</strong> TVA 9% (138.99 DA) | TVA 19% (301.19 DA) | Droit fixe (200.00 DA) | Taxe habitation (200.00 DA)</p>
        <h2 style="color: #2980b9; text-align: right; margin-top: 20px;">Net à payer : 3969.68 DA</h2>
    </div>
</div>
"""

# --- AFFICHAGE ---
st.markdown(html_content, unsafe_allow_html=True)
