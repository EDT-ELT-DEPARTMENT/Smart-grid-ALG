import streamlit as st
import sqlite3
import random
import time
from datetime import datetime, timedelta

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Smart Grid - Facturation", layout="wide")

st.title("Plateforme de Facturation Smart Grid - Électricité et Gaz")

# --- CONSTANTES DE FACTURATION (SIMULATION) ---
A_INDEX_ELEC = 5000.0  # Ancien index de référence pour tous les clients
A_INDEX_GAZ = 2000.0   # Ancien index de référence pour tous les clients
COEF_ELEC = 1.0
PCS_GAZ = 9.15         # Coefficient de conversion m³ -> Thermies (Th)

def get_db():
    conn = sqlite3.connect("sonelgaz_gestion.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Vérification et recréation de la structure
    cursor.execute("PRAGMA table_info(abonnes)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if columns and "index_elec" not in columns:
        cursor.execute("DROP TABLE abonnes")
        cursor.execute("DROP TABLE IF EXISTS mesures")
        conn.commit()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS abonnes (
                        reference_contrat TEXT PRIMARY KEY, 
                        nom TEXT, 
                        index_elec REAL, 
                        index_gaz REAL)''')
    
    # Initialisation de la base de données
    cursor.execute('SELECT count(*) FROM abonnes')
    if cursor.fetchone()[0] == 0:
        # On initialise avec des données qui génèrent une facture similaire au document de référence
        noms = ["MILOUA Farid"] + [f"Client_{i}" for i in range(2, 11)]
        for i, nom in enumerate(noms, 1):
            # Index_elec = 5562 (soit 562 kWh de conso), Index_gaz = 2296 (soit 296 m3 * 9.15 = ~2708 Th)
            cursor.execute('INSERT INTO abonnes VALUES (?, ?, ?, ?)', 
                           (f"22203 44 30110 1 {i:02d}", nom, 5562.0, 2296.0))
        conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# Simulation d'arrivée des données des capteurs TTGO
try:
    cursor.execute('SELECT reference_contrat FROM abonnes')
    refs = cursor.fetchall()
    for (ref,) in refs:
        cursor.execute('UPDATE abonnes SET index_elec = index_elec + ?, index_gaz = index_gaz + ? WHERE reference_contrat = ?', 
                       (random.uniform(0.1, 0.5), random.uniform(0.1, 0.5), ref))
    conn.commit()
except Exception as e:
    st.error(f"Erreur lors de la mise à jour : {e}")


# --- INTERFACE DE SÉLECTION ---
st.header("Édition des Factures par Abonné")

cursor.execute('SELECT reference_contrat, nom FROM abonnes')
clients = cursor.fetchall()
client_options = {f"{row[0]} - {row[1]}": row[0] for row in clients}

selected_client_label = st.selectbox("Sélectionnez un abonné pour générer sa facture :", list(client_options.keys()))
selected_ref = client_options[selected_client_label]

# --- RÉCUPÉRATION ET CALCULS DES DONNÉES DU CLIENT ---
cursor.execute('SELECT nom, index_elec, index_gaz FROM abonnes WHERE reference_contrat = ?', (selected_ref,))
client_data = cursor.fetchone()

if client_data:
    client_nom, index_elec, index_gaz = client_data
    
    # Calcul des consommations
    consommation_elec_kwh = max(0.0, index_elec - A_INDEX_ELEC)
    consommation_gaz_m3 = max(0.0, index_gaz - A_INDEX_GAZ)
    consommation_gaz_th = consommation_gaz_m3 * PCS_GAZ
    
    # --- LOGIQUE DE TRANCHES ÉLECTRICITÉ ---
    e_t1 = min(consommation_elec_kwh, 125.0)
    rem_e = consommation_elec_kwh - e_t1
    e_t2 = min(rem_e, 125.0)
    rem_e -= e_t2
    e_t3 = min(rem_e, 750.0)
    e_t4 = rem_e - e_t3
    
    m_e_t1 = e_t1 * 1.7787
    m_e_t2 = e_t2 * 4.1789
    m_e_t3 = e_t3 * 4.8120
    m_e_t4 = e_t4 * 5.4796
    
    # --- LOGIQUE DE TRANCHES GAZ ---
    g_t1 = min(consommation_gaz_th, 1125.0)
    rem_g = consommation_gaz_th - g_t1
    g_t2 = min(rem_g, 1375.0)
    rem_g -= g_t2
    g_t3 = min(rem_g, 5000.0)
    g_t4 = rem_g - g_t3
    
    m_g_t1 = g_t1 * 0.1682
    m_g_t2 = g_t2 * 0.3245
    m_g_t3 = g_t3 * 0.4025
    m_g_t4 = g_t4 * 0.4599
    
    # --- CALCUL DES TOTAUX ET TVA ---
    abonnement = 164.16
    
    ht_elec_9 = m_e_t1 + m_e_t2
    ht_elec_19 = m_e_t3 + m_e_t4
    total_ht_elec = ht_elec_9 + ht_elec_19
    
    ht_gaz_9 = m_g_t1 + m_g_t2
    ht_gaz_19 = m_g_t3 + m_g_t4
    total_ht_gaz = ht_gaz_9 + ht_gaz_19
    
    total_ht = abonnement + total_ht_elec + total_ht_gaz
    
    tva_9 = (abonnement + ht_elec_9 + ht_gaz_9) * 0.09
    tva_19 = (ht_elec_19 + ht_gaz_19) * 0.19
    total_tva = tva_9 + tva_19
    
    droit_fixe = 200.0
    taxe_hab = 200.0
    
    net_ttc = total_ht + total_tva + droit_fixe + taxe_hab
    timbre = 40.0
    total_payer = net_ttc + timbre

    # --- DATES ---
    date_jour = datetime.now().strftime("%d/%m/%Y")
    date_limite = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")
    date_prochaine = (datetime.now() + timedelta(days=90)).strftime("%d/%m/%Y")

    # --- GÉNÉRATION DE LA FACTURE HTML/CSS ---
    st.markdown("""
<style>
    .facture-container { font-family: 'Arial', sans-serif; background-color: white; color: black; padding: 40px; border: 1px solid #ccc; border-radius: 5px; max-width: 1000px; margin: 0 auto; }
    .header-text { font-size: 11px; line-height: 1.3; }
    .title-box { text-align: center; border: 2px solid black; padding: 10px; margin: 20px 0; font-weight: bold; font-size: 18px; }
    .info-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }
    .info-table td { padding: 4px; border: 1px solid #ddd; }
    .data-table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; font-size: 12px; text-align: center; }
    .data-table th, .data-table td { border: 1px solid black; padding: 6px; }
    .data-table th { background-color: #f2f2f2; }
    .totals-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 20px; }
    .totals-table td { padding: 5px; border-bottom: 1px dotted #ccc; }
    .totals-table .amount { text-align: right; font-weight: bold; }
    .net-pay { font-size: 16px; font-weight: bold; background-color: #f0f0f0; border: 2px solid black; padding: 10px; text-align: center; margin-top: 20px;}
    .arabic { direction: rtl; font-family: 'Arial', sans-serif; }
</style>
    """, unsafe_allow_html=True)

    facture_html = f"""
<div class="facture-container">
    <div style="display: flex; justify-content: space-between;">
        <div class="header-text" style="width: 33%;">
            <strong>الشركة الجزائرية للكهرباء والغاز التوزيع</strong><br>
            Société algérienne de l'électricité et du gaz - Distribution<br>
            Société par action au capital social de 64 000 000 000.00 DA<br>
            Direction de distribution: SIDI BEL ABBES<br>
            RCN: 22/74-0005455806<br>
            NIS: 000609010536556<br>
            NIF: 000609080545593<br>
            RIB N°: 00100773030010182287<br>
            RIP N°: 007999990000380629/09<br>
            AI: 22645590011<br>
            Agence commerciale: SIDI EL DJILLALI
        </div>
        <div style="width: 33%; text-align:center; border: 1px solid black; padding: 10px; border-radius: 5px; height: fit-content;">
            <h2 style="margin:0; color:#1a5276;">3303</h2>
            <p style="font-size:12px; margin:0;">
            Assistance / إتصال<br>Dépannage / مساعدة<br>Réclamation / شكاوي<br>Pour Plus d'informations
            </p>
        </div>
        <div class="header-text arabic" style="width: 33%; text-align:right;">
            <strong>Facture de consommation<br>de l'Electricité et du Gaz</strong><br>
            فاتورة استهلاك<br>الكهرباء والغاز
        </div>
    </div>

    <div class="title-box">Facture n° 733260603359 | فاتورة رقم </div>

    <table class="info-table">
        <tr>
            <td><strong>Etablie le :</strong> {date_jour}</td>
            <td><strong>Client n° :</strong> 7314P001114</td>
        </tr>
        <tr>
            <td><strong>Référence/PDL :</strong> {selected_ref}</td>
            <td><strong>{client_nom}</strong></td>
        </tr>
        <tr>
            <td><strong>Lieu de consommation :</strong> SIDI BEL ABBES</td>
            <td><strong>NIF :</strong></td>
        </tr>
        <tr>
            <td><strong>Prochaine relève vers le :</strong> {date_prochaine}</td>
            <td><strong>RC N° :</strong></td>
        </tr>
    </table>

    <h4>Vos consommations / إستهلاكاتكم (Période du: Trimestre en cours)</h4>
    <table class="data-table">
        <tr>
            <th></th>
            <th>Consommation / الاستهلاك</th>
            <th>Montant en DA HT / المبلغ بالدينار</th>
        </tr>
        <tr>
            <td><strong>Electricité / الكهرباء</strong></td>
            <td>{consommation_elec_kwh:.2f} kWh</td>
            <td>{total_ht_elec:.2f}</td>
        </tr>
        <tr>
            <td><strong>Gaz / الغاز</strong></td>
            <td>{consommation_gaz_th:.2f} Th</td>
            <td>{total_ht_gaz:.2f}</td>
        </tr>
    </table>

    <h4>Vos contrats / عقودكم</h4>
    <h5>Electricité</h5>
    <table class="data-table">
        <tr>
            <th>N° Compteur</th><th>Tarif</th><th>PMD</th><th>Coef</th>
            <th>A. index (البيان السابق)</th><th>N. Index (البيان الجديد)</th>
        </tr>
        <tr>
            <td>070117</td><td>54M</td><td>6kW</td><td>1.0</td>
            <td>{A_INDEX_ELEC:.0f} R</td><td>{index_elec:.0f} R</td>
        </tr>
    </table>
    <table class="data-table">
        <tr>
            <th>Quantité / الكمية</th>
            <th>Tranche 1 ({e_t1:.2f})</th>
            <th>Tranche 2 ({e_t2:.2f})</th>
            <th>Tranche 3 ({e_t3:.2f})</th>
            <th>Tranche 4 ({e_t4:.2f})</th>
        </tr>
        <tr>
            <td><strong>Prix unitaire / ثمن الوحدة</strong></td>
            <td>1,7787</td><td>4,1789</td><td>4,8120</td><td>5,4796</td>
        </tr>
        <tr>
            <td><strong>Montant HT (9%)</strong></td>
            <td colspan="2">{(m_e_t1 + m_e_t2):.2f}</td><td>-</td><td>-</td>
        </tr>
        <tr>
            <td><strong>Montant HT (19%)</strong></td>
            <td>-</td><td>-</td><td colspan="2">{(m_e_t3 + m_e_t4):.2f}</td>
        </tr>
    </table>

    <h5>Gaz</h5>
    <table class="data-table">
        <tr>
            <th>N° Compteur</th><th>Tarif</th><th>DMD</th><th>PCS</th>
            <th>A. Index (البيان السابق)</th><th>N. index (البيان الجديد)</th>
        </tr>
        <tr>
            <td>126106</td><td>23M</td><td>5m³h</td><td>{PCS_GAZ}</td>
            <td>{A_INDEX_GAZ:.0f} R</td><td>{index_gaz:.0f} R</td>
        </tr>
    </table>
    <table class="data-table">
        <tr>
            <th>Quantité / الكمية</th>
            <th>Tranche 1 ({g_t1:.2f})</th>
            <th>Tranche 2 ({g_t2:.2f})</th>
            <th>Tranche 3 ({g_t3:.2f})</th>
            <th>Tranche 4 ({g_t4:.2f})</th>
        </tr>
        <tr>
            <td><strong>Prix unitaire / ثمن الوحدة</strong></td>
            <td>0,1682</td><td>0,3245</td><td>0,4025</td><td>0,4599</td>
        </tr>
        <tr>
            <td><strong>Montant HT (9%)</strong></td>
            <td colspan="2">{(m_g_t1 + m_g_t2):.2f}</td><td>-</td><td>-</td>
        </tr>
        <tr>
            <td><strong>Montant HT (19%)</strong></td>
            <td>-</td><td>-</td><td colspan="2">{(m_g_t3 + m_g_t4):.2f}</td>
        </tr>
    </table>

    <table class="totals-table">
        <tr><td>Redevances fixes HT (Abonnement) (DA) / الإتاوات الثابتة</td><td class="amount">{abonnement:.2f}</td></tr>
        <tr><td>Frais & Prestation HT (DA) / رسوم وخدمات</td><td class="amount">0.00</td></tr>
        <tr><td><strong>Montant HT (DA) / المبلغ دون رسوم</strong></td><td class="amount"><strong>{total_ht:.2f}</strong></td></tr>
        <tr><td>TVA à 9% (DA) / ر.ق.م 9%</td><td class="amount">{tva_9:.2f}</td></tr>
        <tr><td>TVA à 19% (DA) / ر.ق.م 19%</td><td class="amount">{tva_19:.2f}</td></tr>
        <tr><td><strong>Total TVA (DA) / مجموع ر.ق.م</strong></td><td class="amount"><strong>{total_tva:.2f}</strong></td></tr>
        <tr><td>Droit Fixe sur consommation (DA) / المستحقات الثابتة على الاستهلاك</td><td class="amount">{droit_fixe:.2f}</td></tr>
        <tr><td>Taxe d'habitation (DA) / رسم على المسكن</td><td class="amount">{taxe_hab:.2f}</td></tr>
    </table>

    <div class="net-pay">
        Net à payer TTC (DA) / الصافي للدفع متضمن جميع الرسوم (دج)<br>
        <span style="font-size:24px;">{net_ttc:.2f}</span>
    </div>

    <table class="totals-table" style="width:50%; margin: 20px auto;">
        <tr><td>Timbre (paiement en espèce) (DA) / الطابع</td><td class="amount">{timbre:.2f}</td></tr>
        <tr><td><strong>Total à payer (en espèces) (DA) / المستحق الإجمالي</strong></td><td class="amount" style="font-size:18px;"><strong>{total_payer:.2f}</strong></td></tr>
    </table>

    <div style="margin-top: 30px; border-top: 2px solid black; padding-top: 10px;">
        <div style="float:left; width: 45%;">
            <strong>Sauf erreur ou omission / عدا خطأ أو نسيان</strong><br>
            <span style="color:red; font-size:16px;"><strong>Date limite du paiement : {date_limite}</strong></span><br>
            Passé ce délai, nous nous réserverons le droit de procéder à la suspension de la fourniture d'énergie.
        </div>
        <div style="float:right; width: 45%; border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <strong>Espace information / معلومات</strong><br>
            Montant de votre consommation moyenne par jour : <strong>{(total_payer/90):.2f} DA/Jour</strong><br>
        </div>
        <div style="clear:both;"></div>
    </div>
</div>
"""
    
    st.markdown(facture_html, unsafe_allow_html=True)

st.divider()

if st.button("Actualiser les données des compteurs"):
    st.rerun()
