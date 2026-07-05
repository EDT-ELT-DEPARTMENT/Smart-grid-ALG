import streamlit as st
import sqlite3
import base64
from datetime import datetime, timedelta
from weasyprint import HTML # Nécessite : pip install weasyprint

# --- CONFIGURATION ---
st.set_page_config(page_title="SONELGAZ - Facturation", layout="wide")
st.title("Plateforme de Facturation SONELGAZ - Direction de Distribution SIDI BEL ABBES")

# --- DATABASE ---
def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS abonnes (
                        reference_contrat TEXT PRIMARY KEY, 
                        nom TEXT, 
                        index_elec REAL, 
                        index_gaz REAL)''')
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# --- SÉLECTION ---
cursor.execute('SELECT reference_contrat, nom FROM abonnes')
clients = cursor.fetchall()
client_options = {f"{row[0]} - {row[1]}": row[0] for row in clients}
selected_label = st.selectbox("Sélectionnez un abonné :", list(client_options.keys()))
selected_ref = client_options[selected_label]

cursor.execute('SELECT nom, index_elec, index_gaz FROM abonnes WHERE reference_contrat = ?', (selected_ref,))
client_data = cursor.fetchone()

if client_data:
    client_nom, index_elec, index_gaz = client_data
    cons_elec = max(0.0, index_elec - 5000.0)
    cons_gaz = max(0.0, index_gaz - 2000.0) * 9.15
    net_ttc = (cons_elec * 1.77) + (cons_gaz * 0.16) + 164.16
    date_jour = datetime.now().strftime("%d/%m/%Y")

    # --- CODE HTML ---
    # Cette variable contient la structure exacte demandée
    facture_html = f"""
<div style="border: 2px solid #e67e22; padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: #e67e22; text-align: center;">SONELGAZ - Facture de Consommation</h2>
    <div style="display: flex; justify-content: space-between;">
        <div>
            <p><strong>Direction de Distribution :</strong> SIDI BEL ABBES</p>
            <p><strong>Date d'établissement :</strong> {date_jour}</p>
        </div>
        <div>
            <p><strong>Abonné :</strong> {client_nom}</p>
            <p><strong>Référence contrat :</strong> {selected_ref}</p>
        </div>
    </div>
    <table style="width:100%; border-collapse: collapse; margin-top: 20px;">
        <tr style="background-color: #f9e79f;">
            <th style="border: 1px solid #000; padding: 8px;">Service</th>
            <th style="border: 1px solid #000; padding: 8px;">Consommation</th>
            <th style="border: 1px solid #000; padding: 8px;">Montant HT (DA)</th>
        </tr>
        <tr>
            <td style="border: 1px solid #000; padding: 8px;">Électricité</td>
            <td style="border: 1px solid #000; padding: 8px;">{cons_elec:.2f} kWh</td>
            <td style="border: 1px solid #000; padding: 8px;">{(cons_elec * 1.77):.2f}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; padding: 8px;">Gaz</td>
            <td style="border: 1px solid #000; padding: 8px;">{cons_gaz:.2f} Th</td>
            <td style="border: 1px solid #000; padding: 8px;">{(cons_gaz * 0.16):.2f}</td>
        </tr>
    </table>
    <h3 style="text-align: right; margin-top: 20px; color: #d35400;">Net à payer TTC : {net_ttc:.2f} DA</h3>
</div>
"""
    # Affichage
    st.markdown(facture_html, unsafe_allow_html=True)

    # --- TÉLÉCHARGEMENT ---
    col1, col2 = st.columns(2)

    # 1. Bouton HTML
    b64_html = base64.b64encode(facture_html.encode()).decode()
    col1.download_button("Télécharger HTML", b64_html, "facture.html", "text/html")

    # 2. Bouton PDF
    pdf_bytes = HTML(string=facture_html).write_pdf()
    col2.download_button("Télécharger PDF", pdf_bytes, "facture.pdf", "application/pdf")
