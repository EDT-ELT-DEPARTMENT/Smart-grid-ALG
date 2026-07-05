import streamlit as st
import sqlite3
import io
from datetime import datetime, timedelta
from xhtml2pdf import pisa  # Remplace weasyprint

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
    
    # (Optionnel) Ajout de données de test si la base est vide pour éviter un crash
    cursor.execute('SELECT count(*) FROM abonnes')
    if cursor.fetchone()[0] == 0:
        for i in range(1, 11):
            cursor.execute('INSERT OR IGNORE INTO abonnes VALUES (?, ?, ?, ?)', 
                           (f"SNG-2026-{i:03d}", f"Client_{i}", 5562.0, 2296.0))
    
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# --- SÉLECTION ---
cursor.execute('SELECT reference_contrat, nom FROM abonnes')
clients = cursor.fetchall()

if clients:
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
        # ATTENTION : Ce bloc ne doit avoir AUCUN espace à gauche pour que l'affichage marche.
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
        # Affichage direct sur Streamlit
        st.markdown(facture_html, unsafe_allow_html=True)

        # --- TÉLÉCHARGEMENT ---
        col1, col2 = st.columns(2)

        # 1. Bouton HTML (Streamlit gère directement la chaine HTML, sans base64)
        col1.download_button(
            label="Télécharger HTML", 
            data=facture_html, 
            file_name="facture.html", 
            mime="text/html"
        )

        # 2. Bouton PDF (avec xhtml2pdf)
        def generate_pdf(html_content):
            result = io.BytesIO()
            pisa.CreatePDF(html_content, dest=result)
            return result.getvalue()

        pdf_bytes = generate_pdf(facture_html)
        
        col2.download_button(
            label="Télécharger PDF", 
            data=pdf_bytes, 
            file_name="facture.pdf", 
            mime="application/pdf"
        )
else:
    st.warning("La base de données est vide. Veuillez insérer des abonnés.")
