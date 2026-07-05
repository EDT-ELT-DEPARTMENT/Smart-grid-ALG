import streamlit as st
import sqlite3
import random
import time
from datetime import datetime, timedelta

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Smart Grid - Facturation", layout="wide")

st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")

# --- CONSTANTES DE FACTURATION ---
A_INDEX_ELEC = 5000.0
A_INDEX_GAZ = 2000.0
PCS_GAZ = 9.15

def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS abonnes (
                        reference_contrat TEXT PRIMARY KEY, 
                        nom TEXT, 
                        index_elec REAL, 
                        index_gaz REAL)''')
    cursor.execute('SELECT count(*) FROM abonnes')
    if cursor.fetchone()[0] == 0:
        noms = ["MILOUA Farid"] + [f"Client_{i}" for i in range(2, 11)]
        for i, nom in enumerate(noms, 1):
            cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?)', 
                           (f"SNG-2026-{i:03d}", nom, 5562.0, 2296.0))
        conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# Simulation mise à jour capteurs
cursor.execute('SELECT reference_contrat FROM abonnes')
refs = cursor.fetchall()
for (ref,) in refs:
    cursor.execute('UPDATE abonnes SET index_elec = index_elec + ?, index_gaz = index_gaz + ? WHERE reference_contrat = ?', 
                   (random.uniform(0.1, 0.5), random.uniform(0.1, 0.5), ref))
conn.commit()

# --- INTERFACE ---
st.header("Édition des Factures par Abonné")
cursor.execute('SELECT reference_contrat, nom FROM abonnes')
clients = cursor.fetchall()
client_options = {f"{row[0]} - {row[1]}": row[0] for row in clients}
selected_label = st.selectbox("Sélectionnez un abonné pour générer sa facture :", list(client_options.keys()))
selected_ref = client_options[selected_label]

cursor.execute('SELECT nom, index_elec, index_gaz FROM abonnes WHERE reference_contrat = ?', (selected_ref,))
client_data = cursor.fetchone()

if client_data:
    client_nom, index_elec, index_gaz = client_data
    cons_elec = max(0.0, index_elec - A_INDEX_ELEC)
    cons_gaz_m3 = max(0.0, index_gaz - A_INDEX_GAZ)
    cons_gaz_th = cons_gaz_m3 * PCS_GAZ
    
    # Calculs simplifiés pour l'exemple
    e_t1 = min(cons_elec, 125.0)
    m_e_t1 = e_t1 * 1.7787
    g_t1 = min(cons_gaz_th, 1125.0)
    m_g_t1 = g_t1 * 0.1682
    
    abonnement = 164.16
    total_ht = abonnement + m_e_t1 + m_g_t1
    tva = (total_ht) * 0.09
    net_ttc = total_ht + tva + 400
    total_payer = net_ttc + 40
    
    date_jour = datetime.now().strftime("%d/%m/%Y")
    date_limite = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")
    date_prochaine = (datetime.now() + timedelta(days=90)).strftime("%d/%m/%Y")

    st.markdown("""
<style>
.facture-container { font-family: sans-serif; background: white; color: black; padding: 20px; border: 1px solid #ccc; }
.data-table { width: 100%; border-collapse: collapse; text-align: center; }
.data-table th, .data-table td { border: 1px solid black; padding: 5px; }
.net-pay { font-weight: bold; border: 2px solid black; padding: 10px; margin-top: 20px; text-align: center; }
</style>
    """, unsafe_allow_html=True)

    facture_html = f"""
<div class="facture-container">
<h2>Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA</h2>
<table style="width:100%">
<tr><td><strong>Etablie le:</strong> {date_jour}</td><td><strong>Référence:</strong> {selected_ref}</td></tr>
<tr><td><strong>Client:</strong> {client_nom}</td><td><strong>Prochaine relève:</strong> {date_prochaine}</td></tr>
</table>
<table class="data-table">
<tr><th>Service</th><th>Consommation</th><th>Montant HT</th></tr>
<tr><td>Electricité</td><td>{cons_elec:.2f} kWh</td><td>{m_e_t1:.2f}</td></tr>
<tr><td>Gaz</td><td>{cons_gaz_th:.2f} Th</td><td>{m_g_t1:.2f}</td></tr>
</table>
<div class="net-pay">Net à payer TTC : {net_ttc:.2f} DA</div>
<p style="color:red;">Date limite : {date_limite}</p>
</div>
"""
    st.markdown(facture_html, unsafe_allow_html=True)
