import streamlit as st
import sqlite3
import io
from datetime import datetime, timedelta
from xhtml2pdf import pisa

# --- CONFIGURATION ---
st.set_page_config(page_title="Facture SONELGAZ", layout="wide")
st.title("Plateforme de Gestion SONELGAZ - Sidi Bel Abbès")

# --- DATABASE ---
def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    # Ajout des champs spécifiques SONELGAZ dans la base
    cursor.execute('''CREATE TABLE IF NOT EXISTS abonnes (
                        reference_contrat TEXT PRIMARY KEY, 
                        nom TEXT, 
                        client_num TEXT,
                        lieu_conso TEXT,
                        facture_num TEXT,
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

cursor.execute('SELECT nom, client_num, lieu_conso, facture_num, index_elec, index_gaz FROM abonnes WHERE reference_contrat = ?', (selected_ref,))
client_data = cursor.fetchone()

if client_data:
    nom, client_num, lieu_conso, fact_num, index_elec, index_gaz = client_data
    
    # Calculs simples
    cons_elec = max(0.0, index_elec - 5000.0)
    cons_gaz = max(0.0, index_gaz - 2000.0) * 9.15
    net_ttc = (cons_elec * 1.77) + (cons_gaz * 0.16) + 164.16
    
    date_facture = datetime.now().strftime("%d/%m/%Y")
    prochain_releve = (datetime.now() + timedelta(days=90)).strftime("%d/%m/%Y")

    # --- CODE HTML ---
    # Désindenté totalement pour le rendu Streamlit
    facture_html = f"""
<div style="border: 1px solid #000; padding: 20px; font-family: Arial, sans-serif;">
<h2 style="text-align: center;">Facture de consommation d'Electricité et de Gaz</h2>
<div style="display: flex; justify-content: space-between;">
    <div>
        <p><strong>Facture n°:</strong> {fact_num}</p>
        <p><strong>Etablie le:</strong> {date_facture}</p>
        <p><strong>Client n°:</strong> {client_num}</p>
    </div>
    <div>
        <p><strong>Nom:</strong> {nom}</p>
        <p><strong>Lieu de consommation:</strong> {lieu_conso}</p>
        <p><strong>Prochaine relève:</strong> {prochain_releve}</p>
    </div>
</div>
<table style="width:100%; border-collapse: collapse; margin-top: 20px;">
    <tr style="background-color: #eee;">
        <th style="border: 1px solid #000; padding: 8px;">Service</th>
        <th style="border: 1px solid #000; padding: 8px;">Consommation</th>
        <th style="border: 1px solid #000; padding: 8px;">Montant HT (DA)</th>
    </tr>
    <tr>
        <td style="border: 1px solid #000; padding: 8px;">Electricité</td>
        <td style="border: 1px solid #000; padding: 8px;">{cons_elec:.2f} kWh</td>
        <td style="border: 1px solid #000; padding: 8px;">{(cons_elec * 1.77):.2f}</td>
    </tr>
    <tr>
        <td style="border: 1px solid #000; padding: 8px;">Gaz</td>
        <td style="border: 1px solid #000; padding: 8px;">{cons_gaz:.2f} Th</td>
        <td style="border: 1px solid #000; padding: 8px;">{(cons_gaz * 0.16):.2f}</td>
    </tr>
</table>
<h3 style="text-align: right;">Net à payer TTC : {net_ttc:.2f} DA</h3>
</div>
"""
    st.markdown(facture_html, unsafe_allow_html=True)

    # --- TÉLÉCHARGEMENT ---
    col1, col2 = st.columns(2)

    col1.download_button("Télécharger HTML", facture_html, "facture.html", "text/html")

    def generate_pdf(html_content):
        result = io.BytesIO()
        pisa.CreatePDF(html_content, dest=result)
        return result.getvalue()

    col2.download_button("Télécharger PDF", generate_pdf(facture_html), "facture.pdf", "application/pdf")
