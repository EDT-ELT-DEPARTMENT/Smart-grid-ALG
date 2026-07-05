import streamlit as st
import io
from xhtml2pdf import pisa

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Plateforme de gestion des EDTs-S2-2026", 
    layout="wide"
)

# --- TITRES DE L'APPLICATION ---
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# --- DONNÉES DE FACTURATION ---
data = {
    "fact_num": "733260603359",
    "client_num": "7314P001114",
    "nom": "MME BELASKRI ASMA",
    "lieu": "01 BLOC B CT 70 LOGTS UDL",
    "redevance": "164.16",
    "tva_9": "138.99",
    "tva_19": "301.19",
    "droit_fixe": "200.00",
    "taxe_hab": "200.00",
    "net_ttc": "3969.68"
}

# --- CONSTRUCTION DU CONTENU HTML ---
# J'ai ajouté une largeur fixe (max-width) pour que le contenu ne s'étire pas trop sur les grands écrans
html_content = f"""
<div style="font-family: Arial, sans-serif; padding: 25px; border: 2px solid #2980b9; background-color: #ffffff; max-width: 1000px; margin: auto; box-sizing: border-box;">
    
    <h2 style="color: #2980b9; text-align: center; margin-top: 0;">SONELGAZ - Détail de Facturation Smart</h2>
    
    <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #d6eaf8; background-color: #fcfcfc;">
        <p style="margin: 5px 0;"><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
        <p style="margin: 5px 0;"><strong>Abonné :</strong> {data['nom']} | <strong>Lieu de consommation :</strong> {data['lieu']}</p>
    </div>

    <h3 style="color: #2980b9;">Électricité</h3>
    <table style="width:100%; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed;">
        <tr>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Tranche</th>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Quantité (kWh)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Prix Unitaire (DA)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Montant HT (DA)</th>
        </tr>
        <tr>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">Tranche 1</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">125.0</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">1.7787</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">744.70</td>
        </tr>
        <tr>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">Tranche 2</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">125.0</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">4.1789</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">744.70</td>
        </tr>
        <tr>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">Tranche 3</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">312.0</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">4.8120</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">1501.34</td>
        </tr>
    </table>

    <h3 style="color: #2980b9;">Gaz</h3>
    <table style="width:100%; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed;">
        <tr>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Tranche</th>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Quantité (Th)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Prix Unitaire (DA)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; background-color: #d6eaf8; color: #2980b9; width: 25%;">Montant HT (DA)</th>
        </tr>
        <tr>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">Tranche 1</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">1125.0</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">0.1682</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">635.42</td>
        </tr>
        <tr>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">Tranche 2</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">1375.0</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">0.3245</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">635.42</td>
        </tr>
        <tr>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">Tranche 3</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">208.4</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">0.4025</td>
            <td style="border: 1px solid #2980b9; padding: 10px; text-align: center;">83.88</td>
        </tr>
    </table>

    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 15px;">
        <p style="margin: 5px 0;"><strong>Redevance fixe :</strong> {data['redevance']} DA</p>
        <p style="margin: 5px 0;"><strong>Détail Taxes :</strong> TVA 9% ({data['tva_9']} DA) | TVA 19% ({data['tva_19']} DA) | Droit fixe ({data['droit_fixe']} DA) | Taxe habitation ({data['taxe_hab']} DA)</p>
        <h2 style="color: #2980b9; text-align: right; margin-top: 20px;">Net à payer : {data['net_ttc']} DA</h2>
    </div>
</div>
"""

# --- AFFICHAGE ---
st.markdown(html_content, unsafe_allow_html=True)

# --- FONCTION PDF ---
def convertir_en_pdf(html_string):
    resultat = io.BytesIO()
    pisa.CreatePDF(html_string, dest=resultat)
    return resultat.getvalue()

# --- ESPACE DE TÉLÉCHARGEMENT ---
st.markdown("---")
st.write("### Options d'exportation")

col1, col2 = st.columns(2)

col1.download_button(
    label="Télécharger en HTML",
    data=html_content,
    file_name="Facture_SONELGAZ.html",
    mime="text/html"
)

col2.download_button(
    label="Télécharger en PDF",
    data=convertir_en_pdf(html_content),
    file_name="Facture_SONELGAZ.pdf",
    mime="application/pdf"
)
