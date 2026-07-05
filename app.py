import streamlit as st
import io
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="Plateforme de gestion - UDL-SBA", layout="wide")
st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# --- DONNÉES FACTURATION (Extrait de CamScanner 30-06-2026 18.29_2.pdf[cite: 2]) ---
facture_data = {
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
    "redevance": "164.16", "tva_9": "138.99", "tva_19": "301.19", "droit": "200.0", "taxe": "200.0", "net": "3969.68"
}

# --- DONNÉES EDT (Format mémorisé[cite: 1]) ---
edt_data = [
    {"ens": "Stabilité et dynamique des réseaux électriques", "code": "SDRE", "prof": "REZ", "h": "8h - 9h30", "j": "Dimanche", "lieu": "S06", "promo": "M2RE"},
    {"ens": "Éclairage LED: Principes et applications", "code": "LEDPA", "prof": "Bermaki", "h": "9h30 - 11h", "j": "Dimanche", "lieu": "S06", "promo": "M2RE"},
    {"ens": "Techniques d'intelligence artificielle", "code": "TIA", "prof": "Touhami", "h": "9h30 - 11h", "j": "Lundi", "lieu": "S06", "promo": "M2RE"},
    {"ens": "Intégration des ressources renouvelables", "code": "IRRRE", "prof": "BENHAMIDA", "h": "14h00 - 15h30", "j": "Lundi", "lieu": "S06", "promo": "M2RE"},
    {"ens": "Dimensionnement des Réseaux électriques industriels", "code": "DREI", "prof": "Rezoug", "h": "9h30 - 11h", "j": "Mardi", "lieu": "S06", "promo": "M2RE"},
    {"ens": "Technique de la haute tension", "code": "THT", "prof": "Bellebna", "h": "12h30 - 14h00", "j": "Mardi", "lieu": "S06", "promo": "M2RE"},
    {"ens": "Conduite des réseaux électriques", "code": "CdRE", "prof": "Benhamida", "h": "8h - 9h30", "j": "Mercredi", "lieu": "S06", "promo": "M2RE"},
    {"ens": "Réseaux électriques intelligents", "code": "REI", "prof": "Maamar", "h": "9h30 - 11h", "j": "Mercredi", "lieu": "S06", "promo": "M2RE"}
]

# --- AFFICHAGE ---
st.header("Gestion des Emplois du Temps (EDT)")
table_style = "width:100%; border-collapse: collapse; text-align: center;"
td_style = "border: 1px solid #2980b9; padding: 8px;"

edt_html = f"""<table style="{table_style}"><tr style="background-color: #d6eaf8;">
<th>Enseignements</th><th>Code</th><th>Enseignants</th><th>Horaire</th><th>Jours</th><th>Lieu</th><th>Promotion</th></tr>
""" + "".join([f"<tr><td style='{td_style}'>{i['ens']}</td><td style='{td_style}'>{i['code']}</td><td style='{td_style}'>{i['prof']}</td><td style='{td_style}'>{i['h']}</td><td style='{td_style}'>{i['j']}</td><td style='{td_style}'>{i['lieu']}</td><td style='{td_style}'>{i['promo']}</td></tr>" for i in edt_data]) + "</table>"

st.markdown(edt_html, unsafe_allow_html=True)

st.divider()

# --- RENDU FACTURE ---
facture_html = f"""<div style="border: 2px solid #2980b9; padding: 20px;">
<h2 style="color: #2980b9;">Détail de Facturation</h2>
... (continuer avec le code HTML de la facture détaillé précédemment) ...
</div>"""

st.markdown(facture_html, unsafe_allow_html=True)
