import sqlite3
import time
import random
from datetime import datetime

# ==========================================
# 1. Gestionnaire de la Base de Données
# ==========================================

class GestionnaireBD:
    def __init__(self, db_name="sonelgaz_temps_reel.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialiser()

    def initialiser(self):
        # Table des abonnés avec leur état de référence (dernière facture)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS abonnes (
                reference_contrat TEXT PRIMARY KEY,
                nom TEXT,
                index_ref_elec REAL,
                index_ref_gaz REAL
            )
        ''')
        # Table des mesures instantanées (les dernières valeurs envoyées par l'IoT)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesures_instantanees (
                reference_contrat TEXT PRIMARY KEY,
                index_actuel_elec REAL,
                index_actuel_gaz REAL,
                horodatage TEXT
            )
        ''')
        self.conn.commit()

    def obtenir_tous_les_abonnes(self):
        self.cursor.execute('SELECT * FROM abonnes')
        return self.cursor.fetchall()

    def obtenir_mesure_actuelle(self, reference_contrat):
        self.cursor.execute('SELECT index_actuel_elec, index_actuel_gaz FROM mesures_instantanees WHERE reference_contrat = ?', (reference_contrat,))
        return self.cursor.fetchone()

# ==========================================
# 2. Tableau de Bord Temps Réel
# ==========================================

class TableauDeBord:
    def __init__(self, bd):
        self.bd = bd

    def afficher_consommation_temps_reel(self):
        """
        Lit les index de référence et les compare aux mesures IoT instantanées
        pour afficher la consommation cumulée depuis la dernière facture.
        """
        abonnes = self.bd.obtenir_tous_les_abonnes()
        
        print("\n" + "="*95)
        print(f"{'SUIVI TEMPS RÉEL - CONSOMMATION ÉNERGÉTIQUE':^95}")
        print("="*95)
        print(f"{'Réf Contrat':<15} | {'Nom':<12} | {'Conso Élec (kWh)':<20} | {'Conso Gaz (Th)':<20}")
        print("-" * 95)
        
        for abonne in abonnes:
            ref_contrat, nom, ref_elec, ref_gaz = abonne
            
            # Récupération de la mesure IoT la plus récente
            actuel_elec, actuel_gaz = self.bd.obtenir_mesure_actuelle(ref_contrat)
            
            if actuel_elec is not None and actuel_gaz is not None:
                # Calcul de la consommation instantanée
                conso_elec = actuel_elec - ref_elec
                conso_gaz = actuel_gaz - ref_gaz
                
                print(f"{ref_contrat:<15} | {nom:<12} | {conso_elec:<20.2f} | {conso_gaz:<20.2f}")
            else:
                print(f"{ref_contrat:<15} | {nom:<12} | {'En attente...':<20} | {'En attente...':<20}")
        
        print("="*95)
        print(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 3. Simulation de flux IoT (Générateur de données)
# ==========================================

def simuler_flux_iot(bd):
    """Simule des compteurs qui envoient de nouvelles données chaque seconde."""
    abonnes = bd.obtenir_tous_les_abonnes()
    for abonne in abonnes:
        ref = abonne[0]
        # On ajoute une petite quantité aléatoire pour simuler une consommation en direct
        variation_elec = random.uniform(0.01, 0.5)
        variation_gaz = random.uniform(0.01, 0.5)
        
        # Récupérer l'index actuel, puis incrémenter
        actuel_elec, actuel_gaz = bd.obtenir_mesure_actuelle(ref)
        if actuel_elec is None:
            actuel_elec, actuel_gaz = abonne[2], abonne[3]
            
        bd.cursor.execute('''
            INSERT OR REPLACE INTO mesures_instantanees (reference_contrat, index_actuel_elec, index_actuel_gaz, horodatage)
            VALUES (?, ?, ?, ?)
        ''', (ref, actuel_elec + variation_elec, actuel_gaz + variation_gaz, datetime.now().isoformat()))
    bd.conn.commit()

# ==========================================
# 4. Exécution du Programme
# ==========================================

if __name__ == "__main__":
    # Initialisation
    db = GestionnaireBD()
    dashboard = TableauDeBord(db)
    
    # Remplissage initial avec 10 clients s'ils n'existent pas
    if not db.obtenir_tous_les_abonnes():
        for i in range(1, 11):
            db.cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?)', 
                             (f"SNG-2026-{i:03d}", f"Client_{i}", 5000.0, 2000.0))
        db.conn.commit()
    
    # Boucle infinie d'affichage (Temps Réel)
    try:
        print("Démarrage du suivi temps réel... (Appuyez sur Ctrl+C pour arrêter)")
        while True:
            simuler_flux_iot(db) # Simulation des compteurs qui tournent
            dashboard.afficher_consommation_temps_reel() # Affichage
            time.sleep(2) # Mise à jour toutes les 2 secondes
    except KeyboardInterrupt:
        print("\nSuivi arrêté par l'utilisateur.")