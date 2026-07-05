import streamlit as st
import sqlite3
import random
import time
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Gestion Électrotechnique", layout="wide")

# ==========================================
# 1. Gestionnaire de la Base de Données
# ==========================================

class GestionnaireBD:
    def __init__(self, db_name="sonelgaz_temps_reel.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialiser()

    def initialiser(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS abonnes (
                reference_contrat TEXT PRIMARY KEY,
                nom TEXT,
                index_ref_elec REAL,
                index_ref_gaz REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesures_instantanees (
                reference_contrat TEXT PRIMARY KEY,
                index_actuel_elec REAL,
                index_actuel_gaz REAL,
                horodatage TEXT
            )
        ''')
        # Insertion initiale pour 10 clients si la table est vide
        self.cursor.execute('SELECT count(*) FROM abonnes')
        if self.cursor.fetchone()[0] == 0:
            for i in range(1, 11):
                self.cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?)', 
                                 (f"SNG-2026-{i:03d}", f"Client_{i}", 5000.0, 2000.0))
        self.conn.commit()

    def obtenir_tous_les_abonnes(self):
        self.cursor.execute('SELECT * FROM abonnes')
        return self.cursor.fetchall()

    def obtenir_mesure_actuelle(self, reference_contrat):
        self.cursor.execute('SELECT index_actuel_elec, index_actuel_gaz FROM mesures_instantanees WHERE reference_contrat = ?', (reference_contrat,))
        return self.cursor.fetchone()

# ==========================================
# 2. Logique de Simulation et Affichage
# ==========================================

def simuler_flux_iot(bd):
    abonnes = bd.obtenir_tous_les_abonnes()
    for abonne in abonnes:
        ref = abonne[0]
        mesure = bd.obtenir_mesure_actuelle(ref)
        
        if mesure is None:
            actuel_elec, actuel_gaz = abonne[2], abonne[3]
        else:
            actuel_elec, actuel_gaz = mesure
            
        variation_elec = random.uniform(0.01, 0.5)
        variation_gaz = random.uniform(0.01, 0.5)
        
        bd.cursor.execute('''
            INSERT OR REPLACE INTO mesures_instantanees (reference_contrat, index_actuel_elec, index_actuel_gaz, horodatage)
            VALUES (?, ?, ?, ?)
        ''', (ref, actuel_elec + variation_elec, actuel_gaz + variation_gaz, datetime.now().isoformat()))
    bd.conn.commit()

def afficher_tableau_bord(bd):
    abonnes = bd.obtenir_tous_les_abonnes()
    
    st.subheader("Suivi en temps réel des compteurs")
    
    donnees = []
    for abonne in abonnes:
        ref_contrat, nom, ref_elec, ref_gaz = abonne
        actuel = bd.obtenir_mesure_actuelle(ref_contrat)
        
        if actuel:
            conso_elec = actuel[0] - ref_elec
            conso_gaz = actuel[1] - ref_gaz
            donnees.append({
                "Réf Contrat": ref_contrat,
                "Nom": nom,
                "Conso Élec (kWh)": round(conso_elec, 2),
                "Conso Gaz (Th)": round(conso_gaz, 2)
            })
    
    st.table(donnees)
    st.caption(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 3. Application Streamlit
# ==========================================

st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")

# Initialisation de la base
db = GestionnaireBD()

# Simulation d'une nouvelle donnée
simuler_flux_iot(db)

# Affichage des résultats
afficher_tableau_bord(db)

# Rafraîchissement automatique toutes les 2 secondes
time.sleep(2)
st.rerun()
