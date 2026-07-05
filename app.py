import streamlit as st
import io
from xhtml2pdf import pisa

# --- CONFIGURATION DE LA PAGE ---
# Mode wide pour utiliser toute la largeur de l'écran
st.set_page_config(
    page_title="Plateforme de gestion des EDTs-S2-2026", 
    layout="wide"
)

# --- TITRES ---
# Rappel du titre de l'application selon vos consignes[cite: 1]
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# --- DONNÉES DE FACTURATION ---
facture_num = "733260603359"
client_num = "7314P001114"
nom_abonne = "MME BELASKRI ASMA"
lieu_consommation = "01 BLOC B CT 70 LOGTS UDL"

# --- CONSTRUCTION DU CONTENU HTML ---
# Utilisation de box-sizing: border-box pour éviter les débordements de largeur
html_content = f"""
<div style="font-family: Arial, sans-serif; padding: 25px; border: 2px solid #2980b9; background-color: #ffffff; box-sizing: border-box; width: 100%; margin: 0;">
    
    <h2 style="color: #2980b9; text-align: center; margin-top: 0;">SONELGAZ - Détail de Facturation Smart</h2>
    
    <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #d6eaf8; background-color: #fcfcfc;">
        <p style="margin: 5px 0;"><strong>Facture n°:</strong> {facture_num} | <strong>Client n°:</strong> {client_num}</p>
        <p style="margin: 5px 0;"><strong>Abonné :</strong> {nom_abonne} | <strong>Lieu de consommation :</strong> {lieu_consommation}</p>
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
        <p style="margin: 5px 0;"><strong>Redevance fixe :</strong> 164.16 DA</p>
        <p style="margin: 5px 0;"><strong>Détail Taxes :</strong> TVA 9% (138.99 DA) | TVA 19% (301.19 DA) | Droit fixe (200.00 DA) | Taxe habitation (200.00 DA)</p>
        <h2 style="color: #2980b9; text-align: right; margin-top: 20px;">Net à payer : 3969.68 DA</h2>
    </div>
</div>
"""

# --- AFFICHAGE DANS L'INTERFACE ---
# Utilisation d'un conteneur dédié pour isoler l'affichage
with st.container():
    st.markdown(html_content, unsafe_allow_html=True)

# --- FONCTION POUR GÉNÉRER LE PDF ---
def convertir_en_pdf(html_string):
    resultat = io.BytesIO()
    pisa.CreatePDF(html_string, dest=resultat)
    return resultat.getvalue()

# --- ESPACE DE TÉLÉCHARGEMENT ---
st.markdown("---")
st.write("### Options d'exportation")

col1, col2 = st.columns(2)

# Bouton pour télécharger le HTML
col1.download_button(
    label="Télécharger en HTML",
    data=html_content,
    file_name="Facture_SONELGAZ.html",
    mime="text/html"
)

# Bouton pour télécharger le PDF
col2.download_button(
    label="Télécharger en PDF",
    data=convertir_en_pdf(html_content),
    file_name="Facture_SONELGAZ.pdf",
    mime="application/pdf"
)
