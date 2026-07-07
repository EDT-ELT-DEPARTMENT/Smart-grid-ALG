# ============================================================
# Smart-Grid SONELGAZ — Supervision Temps Réel & Facturation
# Version Améliorée : Interface moderne, temps réel, optimisée
# ============================================================

import streamlit as st
import sqlite3
import pandas as pd
import random
import io
import requests
from datetime import datetime
import streamlit.components.v1 as components

try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ============================================================
# 🎨 CONFIGURATION & THÈME
# ============================================================
st.set_page_config(
    page_title="Smart-Grid SONELGAZ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Global — Thème moderne bleu/vert énergie
st.markdown("""
<style>
    /* ---- Fond général ---- */
    .main { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
        border-right: 2px solid #00d4ff33;
    }

    /* ---- Typographie Sidebar ---- */
    [data-testid="stSidebar"] * { color: #e0e8f0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label { color: #a0c4d8 !important; }

    /* ---- Cartes KPI ---- */
    .kpi-card {
        background: linear-gradient(135deg, #1a2942 0%, #0f1e35 100%);
        border: 1px solid #00d4ff44;
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,212,255,0.15);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,212,255,0.3);
    }
    .kpi-icon { font-size: 2.5rem; margin-bottom: 8px; }
    .kpi-label { color: #7aadcb; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 6px 0; }
    .kpi-sub { color: #4a9eba; font-size: 0.8rem; }

    /* ---- Cartes Tranche ---- */
    .tranche-card {
        background: linear-gradient(135deg, #0d2137 0%, #142b45 100%);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #00d4ff;
        margin-bottom: 10px;
    }
    .tranche-title { color: #00d4ff; font-weight: 700; font-size: 0.9rem; }
    .tranche-val { color: #ffffff; font-size: 1.4rem; font-weight: 700; }
    .tranche-price { color: #7aadcb; font-size: 0.8rem; }
    .tranche-mt { color: #4ade80; font-size: 1rem; font-weight: 600; }

    /* ---- Barre de progression stylée ---- */
    .progress-bar-container {
        background: #1a2942;
        border-radius: 8px;
        height: 10px;
        margin-top: 8px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease;
    }

    /* ---- Bannière Header ---- */
    .header-banner {
        background: linear-gradient(135deg, #003d7a 0%, #005bb5 50%, #0073e6 100%);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        border: 1px solid #0073e633;
        box-shadow: 0 4px 20px rgba(0,115,230,0.3);
    }
    .header-title { color: #ffffff; font-size: 1.8rem; font-weight: 800; margin: 0; }
    .header-sub { color: #a0d4ff; font-size: 0.95rem; margin-top: 6px; }

    /* ---- Carte Client ---- */
    .client-card {
        background: linear-gradient(135deg, #0d2137 0%, #142b45 100%);
        border: 1px solid #00d4ff33;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
    }
    .client-card h4 { color: #00d4ff; margin-bottom: 10px; }
    .client-field { color: #a0c4d8; font-size: 0.9rem; margin: 4px 0; }
    .client-val { color: #ffffff; font-weight: 600; }

    /* ---- Résumé Financier ---- */
    .finance-summary {
        background: linear-gradient(135deg, #0a1e35 0%, #0d2a40 100%);
        border: 2px solid #00d4ff55;
        border-radius: 16px;
        padding: 20px 24px;
    }
    .net-payer {
        background: linear-gradient(135deg, #003d7a, #005bb5);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 12px 0;
    }
    .net-payer-label { color: #a0d4ff; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
    .net-payer-value { color: #ffffff; font-size: 2.2rem; font-weight: 800; }
    .especes-total {
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .especes-label { color: #fca5a5; font-size: 0.8rem; }
    .especes-value { color: #ffffff; font-size: 1.6rem; font-weight: 700; }

    /* ---- Boutons personnalisés ---- */
    .stButton > button {
        background: linear-gradient(135deg, #005bb5, #0073e6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0073e6, #00a0ff);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,115,230,0.4);
    }

    /* ---- Live Badge ---- */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #0d2137;
        border: 1px solid #00d4ff44;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        color: #00d4ff;
    }
    .live-dot {
        width: 8px; height: 8px;
        background: #00ff88;
        border-radius: 50%;
        animation: pulse-dot 1.5s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
    }

    /* ---- Alerte montant ---- */
    .alert-montant {
        background: linear-gradient(135deg, #14532d22, #166534aa);
        border: 1px solid #22c55e55;
        border-radius: 10px;
        padding: 10px 14px;
        color: #4ade80;
        font-size: 0.9rem;
        margin: 6px 0;
    }

    /* ---- Divider stylé ---- */
    .styled-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff44, transparent);
        margin: 20px 0;
        border: none;
    }

    /* ---- Metric overrides ---- */
    [data-testid="metric-container"] {
        background: #1a2942;
        border-radius: 12px;
        padding: 14px;
        border: 1px solid #00d4ff22;
    }
    [data-testid="metric-container"] label { color: #7aadcb !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffffff !important; }

    /* ---- Download buttons ---- */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #065f46, #047857) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #047857, #059669) !important;
    }

    /* ---- Sidebar Logo ---- */
    .sidebar-logo {
        text-align: center;
        padding: 16px 0 20px 0;
        border-bottom: 1px solid #00d4ff22;
        margin-bottom: 16px;
    }
    .sidebar-logo-text {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #0073e6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 🗄️ BASE DE DONNÉES — Initialisation & Connexion
# ============================================================
DB_PATH = 'sonelgaz_smartgrid.db'

def get_connection():
    """Connexion SQLite thread-safe."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Crée les tables et injecte les données de départ."""
    conn = get_connection()
    c = conn.cursor()
    # Table principale des mesures
    c.execute("""
        CREATE TABLE IF NOT EXISTS mesures (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type_energie TEXT NOT NULL,
            valeur_actuelle REAL DEFAULT 0,
            total_jour REAL DEFAULT 0,
            client_id TEXT NOT NULL
        )
    """)
    # Table d'audit pour tracer chaque session de facturation
    c.execute("""
        CREATE TABLE IF NOT EXISTS facturation_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            client_id TEXT,
            conso_elec REAL,
            conso_gaz  REAL,
            net_ttc    REAL,
            total_especes REAL
        )
    """)
    # Données initiales pour le client principal
    c.execute("SELECT COUNT(*) FROM mesures WHERE client_id='7314P001114'")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO mesures (timestamp,type_energie,valeur_actuelle,total_jour,client_id) VALUES (?,?,?,?,?)",
                  (now, "Elec", 0.0, 562.00, "7314P001114"))
        c.execute("INSERT INTO mesures (timestamp,type_energie,valeur_actuelle,total_jour,client_id) VALUES (?,?,?,?,?)",
                  (now, "Gaz", 0.0, 2708.40, "7314P001114"))
    conn.commit()
    conn.close()

init_db()


# ============================================================
# 👥 CONFIGURATION CLIENTS
# ============================================================
CLIENTS = {
    "7314P001114": {
        "nom": "MME BELASKRI ASMA",
        "facture": "733260603359",
        "lieu": "01 BLOC B CT 70 LOGTS UDL",
        "avatar": "👩"
    },
    "7314P001115": {
        "nom": "M. Client B",
        "facture": "733260603360",
        "lieu": "CITE 120 LOGTS BAT A",
        "avatar": "👨"
    },
    "7314P001116": {
        "nom": "M. Client C",
        "facture": "733260603361",
        "lieu": "VILLA N°45 ZONE 02",
        "avatar": "🏠"
    }
}

# Facteur de conversion impulsion → énergie
# ⚠️ À adapter selon les specs de votre compteur physique
FACTEUR_IMPULSION_ELEC = 1.0   # 1 impulsion = 1 kWh
FACTEUR_IMPULSION_GAZ  = 1.0   # 1 impulsion = 1 Th


# ============================================================
# ⚙️ MOTEUR DE CALCUL TARIFAIRE SONELGAZ
# ============================================================
TARIFS_ELEC = [
    {"tranche": "Tranche 1 (0–125 kWh)",   "limit": 125.0,  "prix": 1.7787, "color": "#4ade80"},
    {"tranche": "Tranche 2 (125–250 kWh)",  "limit": 125.0,  "prix": 4.1789, "color": "#facc15"},
    {"tranche": "Tranche 3 (>250 kWh)",     "limit": 1000.0, "prix": 4.8120, "color": "#f87171"},
]
TARIFS_GAZ = [
    {"tranche": "Tranche 1 (0–1125 Th)",    "limit": 1125.0, "prix": 0.1682, "color": "#4ade80"},
    {"tranche": "Tranche 2 (1125–2500 Th)", "limit": 1375.0, "prix": 0.3245, "color": "#facc15"},
    {"tranche": "Tranche 3 (>2500 Th)",     "limit": 1000.0, "prix": 0.4025, "color": "#f87171"},
]
TAXES_FIXES = {
    "Redevance fixe HT":  164.16,
    "TVA 9%":             138.99,
    "TVA 19%":            301.19,
    "Droit fixe":         200.00,
    "Taxe habitation":    200.00,
    "Timbre":              40.00,
}

def calculer_tranches_elec(conso: float) -> list:
    """Décompose la consommation électrique en tranches tarifaires."""
    qtés = [
        min(conso, 125.0),
        max(0, min(conso - 125.0, 125.0)),
        max(0, conso - 250.0),
    ]
    return [
        {**t, "qte": q, "mt": round(q * t["prix"], 2)}
        for t, q in zip(TARIFS_ELEC, qtés)
    ]

def calculer_tranches_gaz(conso: float) -> list:
    """Décompose la consommation gaz en tranches tarifaires."""
    qtés = [
        min(conso, 1125.0),
        max(0, min(conso - 1125.0, 1375.0)),
        max(0, conso - 2500.0),
    ]
    return [
        {**t, "qte": q, "mt": round(q * t["prix"], 2)}
        for t, q in zip(TARIFS_GAZ, qtés)
    ]

def calculer_facture(conso_elec: float, conso_gaz: float) -> dict:
    """
    Calcule la facture complète.
    Retourne un dictionnaire structuré avec tous les détails.
    """
    data_elec = calculer_tranches_elec(conso_elec)
    data_gaz  = calculer_tranches_gaz(conso_gaz)

    ht_elec = sum(t["mt"] for t in data_elec)
    ht_gaz  = sum(t["mt"] for t in data_gaz)
    total_ht = round(ht_elec + ht_gaz, 2)

    total_taxes = sum(v for k, v in TAXES_FIXES.items() if k != "Timbre")
    net_ttc = round(total_ht + total_taxes, 2)
    total_especes = round(net_ttc + TAXES_FIXES["Timbre"], 2)

    return {
        "data_elec":     data_elec,
        "data_gaz":      data_gaz,
        "ht_elec":       ht_elec,
        "ht_gaz":        ht_gaz,
        "total_ht":      total_ht,
        "total_taxes":   total_taxes,
        "net_ttc":       net_ttc,
        "total_especes": total_especes,
        "taxes":         TAXES_FIXES,
    }


# ============================================================
# 📡 DONNÉES TEMPS RÉEL
# ============================================================
def get_live_data(client_id: str, type_energie: str) -> float:
    """Retourne la dernière valeur cumulée pour un client et un type d'énergie."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT total_jour FROM mesures WHERE type_energie=? AND client_id=? ORDER BY id DESC LIMIT 1",
        conn, params=(type_energie, client_id)
    )
    conn.close()
    return float(df['total_jour'].iloc[0]) if not df.empty else 0.0

def get_historique(client_id: str, limite: int = 50) -> pd.DataFrame:
    """Retourne l'historique des mesures pour les graphiques."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM mesures WHERE client_id=? ORDER BY id DESC LIMIT ?",
        conn, params=(client_id, limite)
    )
    conn.close()
    return df

def inserer_impulsions(client_id: str, imp_elec: int, imp_gaz: int):
    """Insère de nouvelles impulsions en base et met à jour les totaux cumulés."""
    last_elec = get_live_data(client_id, "Elec")
    last_gaz  = get_live_data(client_id, "Gaz")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO mesures (timestamp,type_energie,valeur_actuelle,total_jour,client_id) VALUES (?,?,?,?,?)",
        (now, "Elec", imp_elec, last_elec + imp_elec * FACTEUR_IMPULSION_ELEC, client_id)
    )
    c.execute(
        "INSERT INTO mesures (timestamp,type_energie,valeur_actuelle,total_jour,client_id) VALUES (?,?,?,?,?)",
        (now, "Gaz",  imp_gaz,  last_gaz  + imp_gaz  * FACTEUR_IMPULSION_GAZ,  client_id)
    )
    conn.commit()
    conn.close()


# ============================================================
# 🎛️ SIDEBAR — Navigation & Sélection
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2.5rem;">⚡</div>
        <div class="sidebar-logo-text">SONELGAZ</div>
        <div style="color:#4a9eba; font-size:0.75rem; margin-top:4px;">Smart-Grid v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👤 Abonné")
    selected_id = st.selectbox(
        "Sélectionner un abonné :",
        list(CLIENTS.keys()),
        format_func=lambda k: f"{CLIENTS[k]['avatar']} {CLIENTS[k]['nom']}"
    )
    client_info = CLIENTS[selected_id]

    st.markdown("---")
    st.markdown("### 📡 Mode d'acquisition")
    mode_acquisition = st.radio(
        "Source des données :",
        ["🔧 Simulation", "📡 Carte TTGO (ESP32)"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Page :",
        ["📊 Supervision Temps Réel", "🧾 Facturation Détaillée"],
        label_visibility="collapsed"
    )

    # Résumé rapide dans la sidebar
    st.markdown("---")
    elec_sidebar = get_live_data(selected_id, "Elec")
    gaz_sidebar  = get_live_data(selected_id, "Gaz")
    facture_sidebar = calculer_facture(elec_sidebar, gaz_sidebar)
    st.markdown(f"""
    <div style="background:#0d2137; border-radius:10px; padding:12px; border:1px solid #00d4ff22;">
        <div style="color:#7aadcb; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">
               Montant Estimé
        </div>
        <div style="color:#ffffff; font-size:1.4rem; font-weight:700;">
            {facture_sidebar['net_ttc']:,.2f} DA
        </div>
        <div style="color:#4a9eba; font-size:0.78rem;">
            ⚡ {elec_sidebar:.1f} kWh &nbsp;|&nbsp; 🔥 {gaz_sidebar:.1f} Th
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 📈 PAGE 1 : SUPERVISION TEMPS RÉEL
# ============================================================
def page_supervision(client_id: str, info: dict):
    # --- Header ---
    st.markdown(f"""
    <div class="header-banner">
        <div style="display:flex; align-items:center; gap:16px;">
            <span style="font-size:3rem;">{info['avatar']}</span>
            <div>
                <p class="header-title">📊 Supervision Temps Réel</p>
                <p class="header-sub">{info['nom']} &nbsp;•&nbsp; N° {client_id} &nbsp;•&nbsp; {info['lieu']}</p>
            </div>
            <div style="margin-left:auto;" class="live-badge">
                <div class="live-dot"></div> LIVE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Acquisition des Impulsions ----
    with st.container():
        if "Simulation" in mode_acquisition:
            st.markdown("""
            <div style="background:#0d2137; border:1px solid #facc1544; border-radius:12px;
                        padding:16px 20px; margin-bottom:16px;">
                <span style="color:#facc15; font-weight:700;">🔧 Mode Simulation</span>
                <span style="color:#a0c4d8; font-size:0.9rem; margin-left:10px;">
                    Génération d'impulsions aléatoires pour tester le système
                </span>
            </div>
            """, unsafe_allow_html=True)

            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
            with col_btn2:
                if st.button("⚡ Simuler Impulsions", use_container_width=True):
                    imp_e = random.randint(1, 8)
                    imp_g = random.randint(1, 4)
                    inserer_impulsions(client_id, imp_e, imp_g)
                    st.toast(f"✅ +{imp_e} imp. Élec | +{imp_g} imp. Gaz insérées !", icon="⚡")
                    st.rerun()

        else:
            st.markdown("""
            <div style="background:#0d2137; border:1px solid #4ade8044; border-radius:12px;
                        padding:16px 20px; margin-bottom:16px;">
                <span style="color:#4ade80; font-weight:700;">📡 Mode IoT — Carte ESP32 TTGO</span>
                <span style="color:#a0c4d8; font-size:0.9rem; margin-left:10px;">
                    Lecture des impulsions via réseau local (HTTP/JSON)
                </span>
            </div>
            """, unsafe_allow_html=True)

            col_ip, col_btn = st.columns([3, 1])
            with col_ip:
                ip_ttgo = st.text_input(
                    "Adresse IP de la carte TTGO :",
                    "192.168.1.50",
                    placeholder="ex: 192.168.1.50"
                )
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📡 Acquérir", use_container_width=True):
                    try:
                        url = f"http://{ip_ttgo}/impulsions"
                        resp = requests.get(url, timeout=5)
                        if resp.status_code == 200:
                            data = resp.json()
                            imp_e = int(data.get("imp_elec", 0))
                            imp_g = int(data.get("imp_gaz", 0))
                            inserer_impulsions(client_id, imp_e, imp_g)
                            st.toast(f"✅ Acquis : +{imp_e} Élec, +{imp_g} Gaz", icon="📡")
                            st.rerun()
                        else:
                            st.error(f"⚠️ Erreur HTTP {resp.status_code}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Impossible de joindre la carte TTGO. Vérifiez l'adresse IP.")
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ---- Récupération des données ----
    elec_val = get_live_data(client_id, "Elec")
    gaz_val  = get_live_data(client_id, "Gaz")
    facture  = calculer_facture(elec_val, gaz_val)

    # ---- KPI Cards principales ----
    st.markdown("### 📊 Tableau de Bord Temps Réel")
    c1, c2, c3, c4 = st.columns(4)

    kpis = [
        ("⚡", "Consommation Électricité", f"{elec_val:,.2f}", "kWh", f"{int(elec_val / FACTEUR_IMPULSION_ELEC)} impulsions"),
        ("🔥", "Consommation Gaz",         f"{gaz_val:,.2f}",  "Th",  f"{int(gaz_val / FACTEUR_IMPULSION_GAZ)} impulsions"),
        ("💰", "Montant HT Total",          f"{facture['total_ht']:,.2f}", "DA",  f"Élec: {facture['ht_elec']:.2f} | Gaz: {facture['ht_gaz']:.2f}"),
        ("🧾", "NET TTC à Payer",           f"{facture['net_ttc']:,.2f}", "DA",  f"Espèces: {facture['total_especes']:.2f} DA"),
    ]
    for col, (icon, label, val, unit, sub) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val} <span style="font-size:0.9rem;color:#7aadcb;">{unit}</span></div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Tranches en temps réel ----
    col_elec, col_gaz = st.columns(2)

    with col_elec:
        st.markdown("#### ⚡ Tranches Électricité (kWh)")
        for t in facture["data_elec"]:
            pct = min(t["qte"] / t["limit"], 1.0) if t["limit"] > 0 else 0
            bar_w = int(pct * 100)
            st.markdown(f"""
            <div class="tranche-card" style="border-left-color:{t['color']};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div class="tranche-title" style="color:{t['color']};">{t['tranche']}</div>
                        <div class="tranche-val">{t['qte']:.2f} kWh</div>
                        <div class="tranche-price">Prix : {t['prix']:.4f} DA/kWh</div>
                    </div>
                    <div class="tranche-mt">{t['mt']:.2f} DA</div>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width:{bar_w}%; background:{t['color']};"></div>
                </div>
                <div style="color:#4a9eba; font-size:0.75rem; text-align:right; margin-top:4px;">{bar_w}% de la tranche</div>
            </div>
            """, unsafe_allow_html=True)

    with col_gaz:
        st.markdown("#### 🔥 Tranches Gaz (Th)")
        for t in facture["data_gaz"]:
            pct = min(t["qte"] / t["limit"], 1.0) if t["limit"] > 0 else 0
            bar_w = int(pct * 100)
            st.markdown(f"""
            <div class="tranche-card" style="border-left-color:{t['color']};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div class="tranche-title" style="color:{t['color']};">{t['tranche']}</div>
                        <div class="tranche-val">{t['qte']:.2f} Th</div>
                        <div class="tranche-price">Prix : {t['prix']:.4f} DA/Th</div>
                    </div>
                    <div class="tranche-mt">{t['mt']:.2f} DA</div>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width:{bar_w}%; background:{t['color']};"></div>
                </div>
                <div style="color:#4a9eba; font-size:0.75rem; text-align:right; margin-top:4px;">{bar_w}% de la tranche</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ---- Graphiques historiques ----
    df = get_historique(client_id, 60)
    if not df.empty:
        df_elec_h = df[df["type_energie"] == "Elec"].sort_values("timestamp")
        df_gaz_h  = df[df["type_energie"] == "Gaz"].sort_values("timestamp")

        st.markdown("### 📈 Évolution de la Consommation")
        tab1, tab2, tab3 = st.tabs(["⚡ Électricité", "🔥 Gaz", "📋 Données Brutes"])

        with tab1:
            if not df_elec_h.empty:
                chart_e = df_elec_h.set_index("timestamp")[["total_jour", "valeur_actuelle"]].rename(
                    columns={"total_jour": "Cumulé (kWh)", "valeur_actuelle": "Impulsions/lecture"}
                )
                st.line_chart(chart_e, use_container_width=True)
            else:
                st.info("Aucune donnée électricité disponible.")

        with tab2:
            if not df_gaz_h.empty:
                chart_g = df_gaz_h.set_index("timestamp")[["total_jour", "valeur_actuelle"]].rename(
                    columns={"total_jour": "Cumulé (Th)", "valeur_actuelle": "Impulsions/lecture"}
                )
                st.line_chart(chart_g, use_container_width=True)
            else:
                st.info("Aucune donnée gaz disponible.")

        with tab3:
            st.dataframe(
                df[["timestamp","type_energie","valeur_actuelle","total_jour"]].rename(columns={
                    "timestamp": "Horodatage",
                    "type_energie": "Énergie",
                    "valeur_actuelle": "Impulsions",
                    "total_jour": "Total Cumulé"
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("⚠️ Aucune donnée disponible. Veuillez simuler ou acquérir des impulsions.")

    # ---- Bouton de rafraîchissement auto ----
    st.markdown("---")
    col_r1, col_r2, col_r3 = st.columns([2, 1, 2])
    with col_r2:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()


# ============================================================
# 🧾 PAGE 2 : FACTURATION DÉTAILLÉE
# ============================================================
def page_facturation(client_id: str, info: dict):
    # --- Header ---
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#003d7a 0%,#005bb5 50%,#0073e6 100%);
                border-radius:16px; padding:24px 30px; margin-bottom:24px;
                border:1px solid #0073e633; box-shadow:0 4px 20px rgba(0,115,230,0.3);">
        <div style="display:flex; align-items:center; gap:16px;">
            <span style="font-size:3rem;">{info['avatar']}</span>
            <div>
                <p style="color:#ffffff; font-size:1.8rem; font-weight:800; margin:0;">
                    🧾 Facture de Consommation — SONELGAZ
                </p>
                <p style="color:#a0d4ff; font-size:0.95rem; margin-top:6px;">
                    N° Facture : {info['facture']} &nbsp;•&nbsp;
                    Générée le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Récupération et calcul ----
    conso_elec = get_live_data(client_id, "Elec")
    conso_gaz  = get_live_data(client_id, "Gaz")
    f = calculer_facture(conso_elec, conso_gaz)

    # ---- Carte Client ----
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d2137 0%,#142b45 100%);
                border:1px solid #00d4ff33; border-radius:12px;
                padding:18px 22px; margin-bottom:20px;">
        <h4 style="color:#00d4ff; margin:0 0 12px 0;">👤 Informations Abonné</h4>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:12px;">
            <div>
                <div style="color:#7aadcb; font-size:0.8rem; text-transform:uppercase;
                            letter-spacing:1px;">Nom du Client</div>
                <div style="color:#ffffff; font-weight:600; margin-top:4px;">{info['nom']}</div>
            </div>
            <div>
                <div style="color:#7aadcb; font-size:0.8rem; text-transform:uppercase;
                            letter-spacing:1px;">N° Client</div>
                <div style="color:#ffffff; font-weight:600; margin-top:4px;">{client_id}</div>
            </div>
            <div>
                <div style="color:#7aadcb; font-size:0.8rem; text-transform:uppercase;
                            letter-spacing:1px;">N° Facture</div>
                <div style="color:#ffffff; font-weight:600; margin-top:4px;">{info['facture']}</div>
            </div>
            <div>
                <div style="color:#7aadcb; font-size:0.8rem; text-transform:uppercase;
                            letter-spacing:1px;">Lieu de consommation</div>
                <div style="color:#ffffff; font-weight:600; margin-top:4px;">{info['lieu']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Tableaux des tranches ----
    def render_table_tranches(data, unite, ht):
        rows = ""
        for t in data:
            rows += f"""
            <tr>
                <td style="padding:9px 12px; border-bottom:1px solid #1a2942;
                           color:{t['color']}; font-weight:600;">{t['tranche']}</td>
                <td style="padding:9px 12px; border-bottom:1px solid #1a2942;
                           color:#ffffff;">{t['qte']:.2f} {unite}</td>
                <td style="padding:9px 12px; border-bottom:1px solid #1a2942;
                           color:#7aadcb;">{t['prix']:.4f} DA/{unite}</td>
                <td style="padding:9px 12px; border-bottom:1px solid #1a2942;
                           color:#4ade80; font-weight:700;">{t['mt']:.2f} DA</td>
            </tr>"""
        return f"""
        <div style="background:#0d2137; border-radius:12px; padding:16px;
                    border:1px solid #00d4ff22; overflow:hidden;">
            <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                <thead>
                    <tr style="background:#0a1e35;">
                        <th style="padding:10px 12px; text-align:left; color:#00d4ff;
                                   border-bottom:2px solid #00d4ff44;">Tranche</th>
                        <th style="padding:10px 12px; text-align:left; color:#00d4ff;
                                   border-bottom:2px solid #00d4ff44;">Quantité</th>
                        <th style="padding:10px 12px; text-align:left; color:#00d4ff;
                                   border-bottom:2px solid #00d4ff44;">Prix Unitaire</th>
                        <th style="padding:10px 12px; text-align:left; color:#00d4ff;
                                   border-bottom:2px solid #00d4ff44;">Montant HT</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
                <tfoot>
                    <tr style="background:#0a2540;">
                        <td colspan="3" style="padding:10px 12px; color:#a0c4d8;
                                              font-weight:600;">SOUS-TOTAL HT</td>
                        <td style="padding:10px 12px; color:#facc15;
                                   font-size:1.05rem; font-weight:700;">{ht:.2f} DA</td>
                    </tr>
                </tfoot>
            </table>
        </div>"""

    col_e, col_g = st.columns(2)
    with col_e:
        st.markdown(f"#### ⚡ Électricité — {conso_elec:.2f} kWh")
        st.markdown(
            render_table_tranches(f["data_elec"], "kWh", f["ht_elec"]),
            unsafe_allow_html=True
        )
    with col_g:
        st.markdown(f"#### 🔥 Gaz — {conso_gaz:.2f} Th")
        st.markdown(
            render_table_tranches(f["data_gaz"], "Th", f["ht_gaz"]),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

        # ---- Taxes & Récapitulatif ----
    col_taxes, col_recap = st.columns(2)

    with col_taxes:
        st.markdown("#### 📋 Taxes et Redevances")

        # Construction des lignes — PAS de commentaires HTML, guillemets sécurisés
        taxes_rows = ""
        for nom, val in f["taxes"].items():
            taxes_rows += (
                '<div style="display:flex; justify-content:space-between;'
                ' padding:9px 0; border-bottom:1px solid #1a2942;">'
                f'<span style="color:#a0c4d8; font-size:0.9rem;">{nom}</span>'
                f'<span style="color:#facc15; font-weight:600; font-size:0.9rem;">{val:.2f} DA</span>'
                '</div>'
            )

        total_taxes_val = f['total_taxes']
        taxes_html = (
            '<div style="background:linear-gradient(135deg,#0a1e35 0%,#0d2a40 100%);'
            ' border:2px solid #00d4ff55; border-radius:16px; padding:20px 24px;">'
            + taxes_rows +
            '<div style="display:flex; justify-content:space-between;'
            ' padding:12px 0 0 0; margin-top:8px; border-top:2px solid #00d4ff33;">'
            '<span style="color:#ffffff; font-weight:700; font-size:1rem;">Total Taxes</span>'
            f'<span style="color:#f87171; font-size:1.2rem; font-weight:700;">{total_taxes_val:.2f} DA</span>'
            '</div>'
            '</div>'
        )
        st.markdown(taxes_html, unsafe_allow_html=True)

    with col_recap:
        st.markdown("#### 💰 Récapitulatif Final")

        # Extraire les valeurs AVANT la construction HTML (évite les f-strings imbriqués)
        ht_elec_v      = f['ht_elec']
        ht_gaz_v       = f['ht_gaz']
        total_ht_v     = f['total_ht']
        total_taxes_v  = f['total_taxes']
        net_ttc_v      = f['net_ttc']
        total_esp_v    = f['total_especes']
        timbre_v       = f['taxes']['Timbre']

        recap_html = (
            '<div style="background:linear-gradient(135deg,#0a1e35 0%,#0d2a40 100%);'
            ' border:2px solid #00d4ff55; border-radius:16px; padding:20px 24px;">'

            # Ligne 1
            '<div style="display:flex; justify-content:space-between;'
            ' padding:9px 0; border-bottom:1px solid #1a2942;">'
            '<span style="color:#a0c4d8; font-size:0.9rem;">Montant HT Electricite</span>'
            f'<span style="color:#ffffff; font-weight:600;">{ht_elec_v:.2f} DA</span>'
            '</div>'

            # Ligne 2
            '<div style="display:flex; justify-content:space-between;'
            ' padding:9px 0; border-bottom:1px solid #1a2942;">'
            '<span style="color:#a0c4d8; font-size:0.9rem;">Montant HT Gaz</span>'
            f'<span style="color:#ffffff; font-weight:600;">{ht_gaz_v:.2f} DA</span>'
            '</div>'

            # Ligne 3
            '<div style="display:flex; justify-content:space-between;'
            ' padding:9px 0; border-bottom:1px solid #1a2942;">'
            '<span style="color:#a0c4d8; font-size:0.9rem;">Total HT</span>'
            f'<span style="color:#facc15; font-weight:700; font-size:1.05rem;">{total_ht_v:.2f} DA</span>'
            '</div>'

            # Ligne 4
            '<div style="display:flex; justify-content:space-between;'
            ' padding:9px 0; border-bottom:1px solid #1a2942;">'
            '<span style="color:#a0c4d8; font-size:0.9rem;">Total Taxes</span>'
            f'<span style="color:#f87171; font-weight:600;">{total_taxes_v:.2f} DA</span>'
            '</div>'

            # Bloc NET TTC — SANS commentaire HTML
            '<div style="background:linear-gradient(135deg,#003d7a,#005bb5);'
            ' border-radius:12px; padding:16px; text-align:center; margin-top:16px;">'
            '<div style="color:#a0d4ff; font-size:0.8rem; text-transform:uppercase;'
            ' letter-spacing:1.5px; font-weight:600;">NET A PAYER TTC</div>'
            f'<div style="color:#ffffff; font-size:2.2rem; font-weight:800; margin-top:6px;">{net_ttc_v:,.2f} DA</div>'
            '</div>'

            # Bloc ESPECES — SANS commentaire HTML
            '<div style="background:linear-gradient(135deg,#7f1d1d,#991b1b);'
            ' border-radius:12px; padding:13px; text-align:center; margin-top:10px;">'
            f'<div style="color:#fca5a5; font-size:0.78rem; letter-spacing:1px;">TOTAL ESPECES (+ timbre {timbre_v:.2f} DA)</div>'
            f'<div style="color:#ffffff; font-size:1.6rem; font-weight:700; margin-top:4px;">{total_esp_v:,.2f} DA</div>'
            '</div>'

            '</div>'
        )
        st.markdown(recap_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Export PDF & HTML ----
    # Construire les lignes de tableaux SÉPARÉMENT (évite f-strings imbriqués)
    rows_elec = ""
    for t in f['data_elec']:
        rows_elec += (
            f'<tr><td>{t["tranche"]}</td>'
            f'<td>{t["qte"]:.2f}</td>'
            f'<td>{t["prix"]:.4f}</td>'
            f'<td>{t["mt"]:.2f}</td></tr>'
        )

    rows_gaz = ""
    for t in f['data_gaz']:
        rows_gaz += (
            f'<tr><td>{t["tranche"]}</td>'
            f'<td>{t["qte"]:.2f}</td>'
            f'<td>{t["prix"]:.4f}</td>'
            f'<td>{t["mt"]:.2f}</td></tr>'
        )

    rows_taxes = ""
    for k, v in f['taxes'].items():
        rows_taxes += f'<p>{k} : <strong>{v:.2f} DA</strong></p>'

    date_generation  = datetime.now().strftime('%d/%m/%Y a %H:%M:%S')
    annee_courante   = datetime.now().year
    nom_fichier_date = datetime.now().strftime('%Y%m%d_%H%M')

    facture_html_export = (
        '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
        'body{font-family:Arial,sans-serif;color:#1a1a2e;margin:0;padding:20px}'
        '.header{background:#004a99;color:white;padding:20px;text-align:center;border-radius:8px;margin-bottom:20px}'
        '.header h1{margin:0;font-size:22px}'
        '.header p{margin:4px 0 0 0;font-size:13px;color:#a0d4ff}'
        '.client-box{background:#f0f6ff;border-left:5px solid #004a99;padding:14px;margin-bottom:20px;border-radius:0 8px 8px 0}'
        '.client-box p{margin:4px 0;font-size:13px}'
        'h3{color:#004a99;border-bottom:2px solid #004a99;padding-bottom:4px;font-size:15px}'
        'table{width:100%;border-collapse:collapse;margin-bottom:18px;font-size:13px}'
        'th{background:#005bb5;color:white;padding:9px 12px;text-align:left}'
        'td{padding:8px 12px;border-bottom:1px solid #dce8f5}'
        'tr:nth-child(even){background:#f7fbff}'
        '.tf td{background:#e8f0fe;font-weight:bold;color:#004a99}'
        '.sg{display:flex;gap:20px}'
        '.tb,.rb{flex:1;background:#f0f6ff;border:1px solid #c0d8f0;border-radius:8px;padding:14px}'
        '.rb p{margin:5px 0;font-size:13px}'
        '.nb{background:#004a99;color:white;border-radius:6px;padding:12px;text-align:center;margin:10px 0}'
        '.nb .lb{font-size:11px;letter-spacing:1px}'
        '.nb .am{font-size:22px;font-weight:800}'
        '.eb{background:#b91c1c;color:white;border-radius:6px;padding:10px;text-align:center}'
        '.eb .am{font-size:18px;font-weight:700}'
        '.ft{text-align:center;margin-top:20px;color:#666;font-size:11px}'
        '</style></head><body>'

        '<div class="header">'
        '<h1>SONELGAZ - Facture de Consommation</h1>'
        f'<p>Generee le {date_generation} | Smart-Grid v2.0</p>'
        '</div>'

        '<div class="client-box">'
        f'<p><strong>Nom :</strong> {info["nom"]}</p>'
        f'<p><strong>N Client :</strong> {client_id} &nbsp;&nbsp; <strong>N Facture :</strong> {info["facture"]}</p>'
        f'<p><strong>Lieu :</strong> {info["lieu"]}</p>'
        '</div>'

        f'<h3>Electricite - {conso_elec:.2f} kWh</h3>'
        '<table>'
        '<tr><th>Tranche</th><th>Quantite (kWh)</th><th>Prix (DA/kWh)</th><th>Montant HT (DA)</th></tr>'
        + rows_elec +
        f'<tr class="tf"><td colspan="3">Sous-Total Electricite HT</td><td>{f["ht_elec"]:.2f}</td></tr>'
        '</table>'

        f'<h3>Gaz - {conso_gaz:.2f} Th</h3>'
        '<table>'
        '<tr><th>Tranche</th><th>Quantite (Th)</th><th>Prix (DA/Th)</th><th>Montant HT (DA)</th></tr>'
        + rows_gaz +
        f'<tr class="tf"><td colspan="3">Sous-Total Gaz HT</td><td>{f["ht_gaz"]:.2f}</td></tr>'
        '</table>'

        '<div class="sg">'
        '<div class="tb">'
        '<h3>Taxes et Redevances</h3>'
        + rows_taxes +
        f'<p><strong>Total Taxes : {f["total_taxes"]:.2f} DA</strong></p>'
        '</div>'
        '<div class="rb">'
        '<h3>Recapitulatif Financier</h3>'
        f'<p>Total HT Electricite : <strong>{f["ht_elec"]:.2f} DA</strong></p>'
        f'<p>Total HT Gaz : <strong>{f["ht_gaz"]:.2f} DA</strong></p>'
        f'<p>Total HT : <strong>{f["total_ht"]:.2f} DA</strong></p>'
        f'<p>Total Taxes : <strong>{f["total_taxes"]:.2f} DA</strong></p>'
        '<div class="nb">'
        '<div class="lb">NET A PAYER TTC</div>'
        f'<div class="am">{f["net_ttc"]:,.2f} DA</div>'
        '</div>'
        '<div class="eb">'
        '<div class="lb" style="font-size:11px;">TOTAL ESPECES (timbre inclus)</div>'
        f'<div class="am">{f["total_especes"]:,.2f} DA</div>'
        '</div>'
        '</div>'
        '</div>'

        f'<div class="ft">Document genere automatiquement par Smart-Grid SONELGAZ v2.0 - {annee_courante}</div>'
        '</body></html>'
    )

    st.markdown("#### 📥 Télécharger la Facture")
    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            label="📄 Télécharger HTML",
            data=facture_html_export,
            file_name=f"facture_{client_id}_{nom_fichier_date}.html",
            mime="text/html",
            use_container_width=True
        )
    with c2:
        if PDF_AVAILABLE:
            def gen_pdf(html):
                buf = io.BytesIO()
                pisa.CreatePDF(html, dest=buf, encoding='utf-8')
                return buf.getvalue()
            st.download_button(
                label="📑 Télécharger PDF",
                data=gen_pdf(facture_html_export),
                file_name=f"facture_{client_id}_{nom_fichier_date}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("📦 `pip install xhtml2pdf` pour activer l'export PDF")




# ============================================================
# 🚦 ROUTAGE PRINCIPAL
# ============================================================
if "Supervision" in page:
    page_supervision(selected_id, client_info)
elif "Facturation" in page:
    page_facturation(selected_id, client_info)
