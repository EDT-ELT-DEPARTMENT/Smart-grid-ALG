import streamlit as st
import sqlite3
import random
import time
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Plateforme de gestion des EDTs", layout="wide")

st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")

# ==========================================
# 1. Gestion Base de Données
# ==========================================
def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS abonnes (
                        reference_contrat TEXT PRIMARY KEY, 
                        nom TEXT, index_elec REAL, index_gaz REAL)''')
    
    # Remplissage si vide
    cursor.execute('SELECT count(*) FROM abonnes')
    if cursor.fetchone()[0] == 0:
        for i in range(1, 11):
            cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?)', 
                           (f"SNG-2026-{i:03d}", f"Client_{i}", 5000.0, 2000.0))
        conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# ==========================================
# 2. Simulation (Remplace la boucle while)
# ==========================================
# On simule une mise à jour à chaque fois que la page est rafraîchie
for i in range(1, 11):
    ref = f"SNG-2026-{i:03d}"
    cursor.execute('UPDATE abonnes SET index_elec = index_elec + ?, index_gaz = index_gaz + ? WHERE reference_contrat = ?', 
                   (random.uniform(0.1, 0.5), random.uniform(0.1, 0.5), ref))
conn.commit()

# ==========================================
# 3. Affichage (Interface)
# ==========================================
st.subheader("État actuel des compteurs")

data = []
for row in cursor.execute('SELECT * FROM abonnes'):
    data.append({
        "Réf Contrat": row[0],
        "Nom": row[1],
        "Index Élec": round(row[2], 2),
        "Index Gaz": round(row[3], 2)
    })

st.table(data)

st.info(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")

# Bouton de rafraîchissement manuel
if st.button("Rafraîchir les données"):
    st.rerun()

# Rafraîchissement automatique toutes les 5 secondes
time.sleep(5)
st.rerun()
