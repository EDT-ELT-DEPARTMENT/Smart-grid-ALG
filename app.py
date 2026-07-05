import sqlite3
import random
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# ==============================================================================
# CONFIGURATION ET BASE DE DONNÉES
# ==============================================================================
DB_NAME = "sonelgaz_gestion_complete.db"

class GestionnaireBD:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.creer_tables()

    def creer_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS abonnes (
                reference_contrat TEXT PRIMARY KEY,
                nom TEXT,
                prenom TEXT,
                adresse TEXT,
                index_elec_total REAL,
                index_gaz_total REAL
            )
        ''')
        # Initialisation par défaut de 10 clients
        self.cursor.execute('SELECT count(*) FROM abonnes')
        if self.cursor.fetchone()[0] == 0:
            for i in range(1, 11):
                self.cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?, ?, ?)', 
                                 (f"SNG-2026-{i:03d}", f"Nom_{i}", f"Client_{i}", "Sidi Bel Abbes", 5000.0, 2000.0))
        self.conn.commit()

    def mettre_a_jour_index(self, ref, delta_elec, delta_gaz):
        self.cursor.execute('''
            UPDATE abonnes 
            SET index_elec_total = index_elec_total + ?, 
                index_gaz_total = index_gaz_total + ? 
            WHERE reference_contrat = ?
        ''', (delta_elec, delta_gaz, ref))
        self.conn.commit()

# ==============================================================================
# GESTION MQTT (ACQUISITION RÉELLE)
# ==============================================================================
def on_message(client, userdata, msg):
    try:
        # Exemple de topic: "dept_elt/sba/SNG-2026-001/elec"
        topic_parts = msg.topic.split('/')
        ref_contrat = topic_parts[2]
        valeur = float(msg.payload.decode())
        
        print(f"[MQTT] Réception réelle pour {ref_contrat} : {valeur}")
        
        # Mise à jour de la DB selon le type de message
        if "elec" in msg.topic:
            db.mettre_a_jour_index(ref_contrat, valeur, 0)
        elif "gaz" in msg.topic:
            db.mettre_a_jour_index(ref_contrat, 0, valeur)
    except Exception as e:
        print(f"Erreur lors du traitement MQTT : {e}")

# ==============================================================================
# SIMULATION (MODE TEST)
# ==============================================================================
def simuler_consommation(db):
    abonnes = db.cursor.execute('SELECT reference_contrat FROM abonnes').fetchall()
    for row in abonnes:
        ref = row[0]
        # Consommation aléatoire pour simulation
        d_elec = random.uniform(0.01, 0.5)
        d_gaz = random.uniform(0.01, 0.5)
        db.mettre_a_jour_index(ref, d_elec, d_gaz)
    print("[SIMULATION] Mise à jour effectuée pour tous les compteurs.")

# ==============================================================================
# BOUCLE PRINCIPALE
# ==============================================================================
if __name__ == "__main__":
    db = GestionnaireBD()
    
    # Configuration du Client MQTT avec gestion de version API
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_message = on_message
    
    # Connexion au broker (à adapter avec votre IP)
    try:
        client.connect("192.168.1.50", 1883, 60)
        client.subscribe("dept_elt/sba/+/elec")
        client.subscribe("dept_elt/sba/+/gaz")
        client.loop_start()
        print("Mode Acquisition MQTT activé...")
        mqtt_active = True
    except:
        print("Broker MQTT inaccessible. Passage en mode Simulation pure.")
        mqtt_active = False

    # Boucle d'exécution
    try:
        while True:
            # Si pas de MQTT, on simule
            if not mqtt_active:
                simuler_consommation(db)
            
            # Affichage de l'état actuel de la base
            print(f"\n--- État actuel des compteurs ({datetime.now().strftime('%H:%M:%S')}) ---")
            for row in db.cursor.execute('SELECT reference_contrat, index_elec_total, index_gaz_total FROM abonnes'):
                print(f"Réf: {row[0]} | Elec: {row[1]:.2f} | Gaz: {row[2]:.2f}")
            
            time.sleep(10) # Rafraîchissement toutes les 10 secondes
    except KeyboardInterrupt:
        if mqtt_active:
            client.loop_stop()
        print("\nArrêt du système.")
