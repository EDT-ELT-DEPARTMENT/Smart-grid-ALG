import streamlit as st
import sqlite3
import random
import time
from datetime import datetime

# Configuration
st.set_page_config(page_title="", layout="wide")

st.title("")

def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # 1. Vérification de la structure : si la table n'a pas les bonnes colonnes, on la supprime
    cursor.execute("PRAGMA table_info(abonnes)")
    columns = [info[1] for info in cursor.fetchall()]
    
    # Si la table existe mais n'a pas les colonnes attendues (4 colonnes), on reset
    if columns and "index_elec" not in columns:
        cursor.execute("DROP TABLE abonnes")
        cursor.execute("DROP TABLE mesures")
        conn.commit()
    
    # 2. Recréation propre
    cursor.execute('''CREATE TABLE IF NOT EXISTS abonnes (
                        reference_contrat TEXT PRIMARY KEY, 
                        nom TEXT, 
                        index_elec REAL, 
                        index_gaz REAL)''')
    
    # Initialisation si vide
    cursor.execute('SELECT count(*) FROM abonnes')
    if cursor.fetchone()[0] == 0:
        for i in range(1, 11):
            cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?)', 
                           (f"SNG-2026-{i:03d}", f"Client_{i}", 5000.0, 2000.0))
        conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# Simulation mise à jour
try:
    for i in range(1, 11):
        ref = f"SNG-2026-{i:03d}"
        cursor.execute('UPDATE abonnes SET index_elec = index_elec + ?, index_gaz = index_gaz + ? WHERE reference_contrat = ?', 
                       (random.uniform(0.1, 0.5), random.uniform(0.1, 0.5), ref))
    conn.commit()
except Exception as e:
    st.error(f"Erreur lors de la mise à jour : {e}")

# Affichage
st.subheader("État actuel des compteurs")
data = []
for row in cursor.execute('SELECT * FROM abonnes'):
    data.append({"Code": row[0], "Nom": row[1], "Index Élec": round(row[2], 2), "Index Gaz": round(row[3], 2)})

st.table(data)

if st.button("Rafraîchir"):
    st.rerun()

time.sleep(5)
st.rerun()
