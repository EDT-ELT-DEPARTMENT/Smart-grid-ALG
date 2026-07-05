import streamlit as st
import io
from xhtml2pdf import pisa

# --- CONFIGURATION DE LA PAGE ---
# Définit la mise en page en mode large pour un affichage optimal
st.set_page_config(
    page_title="Plateforme de gestion des EDTs-S2-2026", 
    layout="wide"
)

# --- TITRE DE L'APPLICATION ---
# Titre strict conformément à vos consignes
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# --- DONNÉES DE LA FACTURE ---
data = {
    "nom": "MME BELASKRI ASMA",
    "client_num": "7314P001114",
    "lieu_conso": "01 BLOC B CT 70 LOGTS UDL",
    "fact_num": "733260603359",
    "elec": [
        {"tranche": "Tranche 1", "qte": 125.0, "prix": 1.7787, "mt": 744.7},
        {"tranche": "Tranche 2", "qte": 125.0, "prix": 4.1789, "mt": 744.7},
        {"tranche": "Tranche 3", "qte": 312.0, "prix": 4.812, "mt": 1501.34}
    ],
    "gaz": [
        {"tranche": "Tranche 1", "qte": 1125.0, "prix": 0.1682, "mt": 635.42},
        {"tranche": "Tranche 2", "qte": 1375.0, "prix": 0.3245, "mt": 635.42},
        {"tranche": "Tranche 3", "qte": 208.4, "prix": 0.4025, "mt": 83.88}
    ],
    "redevance": 164.16,
    "tva_9": 138.99,
    "tva_19": 301.19,
    "droit": 200.0,
    "taxe": 200.0,
    "net_ttc": 3969.68
}

# --- CONSTRUCTION DU HTML ---
# Utilisation de styles inline robustes pour assurer le rendu dans l'interface et dans le PDF
html_content = f"""
<div style="border: 2px solid #2980b9; padding: 25px; font-family: Arial, sans-serif; background-color: #ffffff; max-width: 1000px; margin: auto;">
    <h2 style="color: #2980b9; text-align: center;">SONELGAZ - Détail de Facturation</h2>
    
    <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #d6eaf8; background-color: #fcfcfc;">
        <p><strong>Facture n°:</strong> {data['fact_num']} | <strong>Client n°:</strong> {data['client_num']}</p>
        <p><strong>Abonné :</strong> {data['nom']} | <strong>Lieu de consommation :</strong> {data['lieu_conso']}</p>
    </div>

    <h3 style="color: #2980b9;">Électricité</h3>
    <table style="width:100%; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed;">
        <tr style="background-color: #d6eaf8;">
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Tranche</th>
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Quantité (kWh)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Prix Unitaire (DA)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Montant HT (DA)</th>
        </tr>
        {"".join([f"<tr><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['tranche']}</td><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['qte']}</td><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['prix']}</td><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['mt']}</td></tr>" for i in data['elec']])}
    </table>

    <h3 style="color: #2980b9;">Gaz</h3>
    <table style="width:100%; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed;">
        <tr style="background-color: #d6eaf8;">
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Tranche</th>
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Quantité (Th)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Prix Unitaire (DA)</th>
            <th style="border: 1px solid #2980b9; padding: 12px; text-align: center; color: #2980b9;">Montant HT (DA)</th>
        </tr>
        {"".join([f"<tr><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['tranche']}</td><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['qte']}</td><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['prix']}</td><td style='border: 1px solid #2980b9; padding: 10px; text-align: center;'>{i['mt']}</td></tr>" for i in data['gaz']])}
    </table>

    <div style="margin-top: 20px; border-top: 2px solid #2980b9; padding-top: 15px;">
        <p><strong>Redevance fixe :</strong> {data['redevance']} DA | <strong>Taxes :</strong> TVA 9% ({data['tva_9']} DA) | TVA 19% ({data['tva_19']} DA)</p>
        <p><strong>Droit fixe :</strong> {data['droit']} DA | <strong>Taxe habitation :</strong> {data['taxe']} DA</p>
        <h2 style="color: #2980b9; text-align: right; margin-top: 20px;">Net à payer : {data['net_ttc']} DA</h2>
    </div>
</div>
"""

# --- AFFICHAGE ---
st.markdown(html_content, unsafe_allow_html=True)

# --- FONCTION POUR GÉNÉRER LE PDF ---
def generate_pdf(html_str):
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(html_str.encode("UTF-8")), dest=result)
    if not pdf.err:
        return result.getvalue()
    return None

# --- OPTIONS D'EXPORTATION ---
st.markdown("---")
st.write("### Options d'exportation")

col1, col2 = st.columns(2)

# Bouton HTML
col1.download_button(
    label="Télécharger en HTML",
    data=html_content,
    file_name="facture.html",
    mime="text/html"
)

# Bouton PDF
pdf_data = generate_pdf(html_content)
if pdf_data:
    col2.download_button(
        label="Télécharger en PDF",
        data=pdf_data,
        file_name="facture.pdf",
        mime="application/pdf"
    )
else:
    col2.error("Erreur génération PDF")
