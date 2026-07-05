import streamlit as st
import sqlite3
import random
import time
import os
from datetime import datetime
from fpdf import FPDF

# Configuration de la page
st.set_page_config(page_title="Plateforme de gestion des EDTs", layout="wide")

# ==========================================
# 1. Gestionnaire de la Base de Données
# ==========================================

class GestionnaireBD:
    def __init__(self, db_name="sonelgaz_gestion.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialiser()

    def initialiser(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS abonnes (
                reference_contrat TEXT PRIMARY KEY,
                nom TEXT,
                prenom TEXT,
                adresse TEXT,
                index_ref_elec REAL,
                index_ref_gaz REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesures_instantanees (
                reference_contrat TEXT PRIMARY KEY,
                index_actuel_elec REAL,
                index_actuel_gaz REAL
            )
        ''')
        # Insertion initiale pour 10 clients si vide
        self.cursor.execute('SELECT count(*) FROM abonnes')
        if self.cursor.fetchone()[0] == 0:
            for i in range(1, 11):
                self.cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?, ?, ?)', 
                                 (f"SNG-2026-{i:03d}", f"Nom_{i}", f"Client_{i}", f"Cité {i}, SBA", 5000.0, 2000.0))
        self.conn.commit()

    def obtenir_tous_les_abonnes(self):
        self.cursor.execute('SELECT * FROM abonnes')
        return self.cursor.fetchall()

    def obtenir_mesure_actuelle(self, reference_contrat):
        self.cursor.execute('SELECT index_actuel_elec, index_actuel_gaz FROM mesures_instantanees WHERE reference_contrat = ?', (reference_contrat,))
        return self.cursor.fetchone()

# ==========================================
# 2. Moteur de Facturation
# ==========================================

class MoteurFacturation:
    @staticmethod
    def generer_pdf(facture_data, nom_fichier):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="FACTURE SONELGAZ - DEPARTEMENT ELECTRIQUE", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        for ligne in facture_data:
            pdf.cell(200, 10, txt=ligne, ln=True)
        
        dossier = "factures_pdf"
        if not os.path.exists(dossier): os.makedirs(dossier)
        chemin = os.path.join(dossier, nom_fichier)
        pdf.output(chemin)
        return chemin

# ==========================================
# 3. Application Streamlit
# ==========================================

st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")

db = GestionnaireBD()

# Simulation flux IoT
abonnes = db.obtenir_tous_les_abonnes()
for abonne in abonnes:
    ref = abonne[0]
    mesure = db.obtenir_mesure_actuelle(ref)
    idx_e = mesure[0] if mesure else abonne[4]
    idx_g = mesure[1] if mesure else abonne[5]
    
    db.cursor.execute('INSERT OR REPLACE INTO mesures_instantanees VALUES (?, ?, ?)',
                     (ref, idx_e + random.uniform(0.1, 0.9), idx_g + random.uniform(0.1, 0.9)))
db.conn.commit()

# Affichage Tableau
st.subheader("Suivi en temps réel")
donnees = []
for abonne in abonnes:
    actuel = db.obtenir_mesure_actuelle(abonne[0])
    donnees.append({
        "Réf Contrat": abonne[0],
        "Nom": abonne[1],
        "Conso Élec": round(actuel[0] - abonne[4], 2),
        "Conso Gaz": round(actuel[1] - abonne[5], 2)
    })
st.table(donnees)

# Section Facturation
st.subheader("Génération de Factures")
ref_select = st.selectbox("Choisir un client pour facturation", [a[0] for a in abonnes])

if st.button("Émettre Facture PDF"):
    abonne = [a for a in abonnes if a[0] == ref_select][0]
    actuel = db.obtenir_mesure_actuelle(ref_select)
    
    facture_data = [
        f"Contrat: {abonne[0]}",
        f"Client: {abonne[1]} {abonne[2]}",
        f"Consommation Elec: {round(actuel[0] - abonne[4], 2)} kWh",
        f"Consommation Gaz: {round(actuel[1] - abonne[5], 2)} Thermies",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ]
    
    chemin_pdf = MoteurFacturation.generer_pdf(facture_data, f"Facture_{ref_select}.pdf")
    st.success(f"Facture générée : {chemin_pdf}")
    
    # Bouton de téléchargement
    with open(chemin_pdf, "rb") as f:
        st.download_button("Télécharger le PDF", f, file_name=f"Facture_{ref_select}.pdf")

# Rafraîchissement
time.sleep(2)
st.rerun()
