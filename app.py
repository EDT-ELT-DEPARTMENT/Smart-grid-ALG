import streamlit as st
import sqlite3
import random
import time
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Smart Grid - Facturation", layout="wide")

st.title("Plateforme de Facturation Smart Grid - Électricité et Gaz")

def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # 1. Vérification de la structure : si la table n'a pas les bonnes colonnes, on la supprime
    cursor.execute("PRAGMA table_info(abonnes)")
    columns = [info[1] for info in cursor.fetchall()]
    
    # Si la table existe mais n'a pas les colonnes attendues, on reset
    if columns and "index_elec" not in columns:
        cursor.execute("DROP TABLE abonnes")
        cursor.execute("DROP TABLE IF EXISTS mesures")
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
        # On initialise les compteurs à 5000 pour l'élec et 2000 pour le gaz
        for i in range(1, 11):
            cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?)', 
                           (f"SNG-2026-{i:03d}", f"Client_{i}", 5000.0, 2000.0))
        conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# Simulation de la mise à jour continue des index (les capteurs TTGO)
try:
    for i in range(1, 11):
        ref = f"SNG-2026-{i:03d}"
        cursor.execute('UPDATE abonnes SET index_elec = index_elec + ?, index_gaz = index_gaz + ? WHERE reference_contrat = ?', 
                       (random.uniform(0.1, 0.5), random.uniform(0.1, 0.5), ref))
    conn.commit()
except Exception as e:
    st.error(f"Erreur lors de la mise à jour : {e}")

# --- SUPERVISION INDIVIDUELLE ---
st.header("Supervision et Facturation par Client")

# Récupération de la liste des clients pour la liste déroulante
cursor.execute('SELECT reference_contrat, nom FROM abonnes')
clients = cursor.fetchall()
# Création d'un dictionnaire pour lier l'affichage "Réf - Nom" à la clé "Réf"
client_options = {f"{row[0]} - {row[1]}": row[0] for row in clients}

# Liste déroulante
selected_client_label = st.selectbox("Sélectionnez un abonné :", list(client_options.keys()))
selected_ref = client_options[selected_client_label]

# Récupération des index du client sélectionné
cursor.execute('SELECT index_elec, index_gaz FROM abonnes WHERE reference_contrat = ?', (selected_ref,))
client_data = cursor.fetchone()

if client_data:
    index_elec, index_gaz = client_data
    
    # Affichage des compteurs numériques
    st.markdown("### Index de consommation actuels")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="⚡ Index Électricité (kWh)", value=f"{index_elec:,.2f}")
        
    with col2:
        st.metric(label="🔥 Index Gaz (m³)", value=f"{index_gaz:,.2f}")

    # --- CALCUL DE LA FACTURE ---
    st.markdown("### Estimation de la Facture")
    
    # Paramètres de calcul (Tarifs Sonelgaz simplifiés à titre indicatif)
    TARIF_ELEC = 4.18  # DA par kWh
    TARIF_GAZ = 1.12   # DA par m³
    
    # Pour simuler la consommation du mois, on soustrait l'index initial (5000 et 2000)
    # Dans un cas réel, vous soustrairiez l'index du mois précédent stocké en base
    consommation_elec = index_elec - 5000.0
    consommation_gaz = index_gaz - 2000.0
    
    # Éviter les valeurs négatives en cas d'erreur
    consommation_elec = max(0, consommation_elec)
    consommation_gaz = max(0, consommation_gaz)
    
    montant_elec = consommation_elec * TARIF_ELEC
    montant_gaz = consommation_gaz * TARIF_GAZ
    montant_total = montant_elec + montant_gaz
    
    # Affichage de la facture sous forme de cartes
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric(label="Consommation Élec.", value=f"{consommation_elec:,.2f} kWh", delta=f"{montant_elec:,.2f} DA", delta_color="off")
        
    with col4:
        st.metric(label="Consommation Gaz", value=f"{consommation_gaz:,.2f} m³", delta=f"{montant_gaz:,.2f} DA", delta_color="off")
        
    with col5:
        # On utilise une boite de succès pour mettre le total en évidence
        st.success(f"**Montant Total Estimé : {montant_total:,.2f} DA**")

st.divider()

# --- VUE GLOBALE ---
# Tableau placé dans un expander pour ne pas surcharger l'interface principale
with st.expander("Voir l'état global de tous les compteurs"):
    data = []
    for row in cursor.execute('SELECT * FROM abonnes'):
        data.append({
            "Référence": row[0], 
            "Nom": row[1], 
            "Index Élec (kWh)": round(row[2], 2), 
            "Index Gaz (m³)": round(row[3], 2)
        })
    st.table(data)

# Actualisation de la page
if st.button("Rafraîchir manuellement"):
    st.rerun()

# Boucle de rafraîchissement automatique toutes les 5 secondes
time.sleep(5)
st.rerun()
