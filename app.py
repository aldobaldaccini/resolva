import streamlit as st
import pandas as pd
import plotly.express as px
import httpx
import json
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Resolva - Gestione Reclami", page_icon="⚖️", layout="wide")

# ── CONNESSIONE SUPABASE via REST API diretta (no libreria supabase) ──
SUPABASE_URL = "https://szqkzsijcyhqtubywpik.supabase.co"
SUPABASE_KEY = "sb_publishable_5ZKZUO6AZ158aR9HtxL7EQ_eymBsGcm"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
TABLE_URL = f"{SUPABASE_URL}/rest/v1/reclami"

def sb_get():
    r = httpx.get(TABLE_URL, headers=HEADERS, params={"order": "created_at.asc"})
    return r.json() if r.status_code == 200 else []

def sb_insert(data: dict):
    httpx.post(TABLE_URL, headers=HEADERS, content=json.dumps(data))

def sb_update(id_pratica: str, data: dict):
    httpx.patch(TABLE_URL, headers=HEADERS,
                params={"id_pratica": f"eq.{id_pratica}"},
                content=json.dumps(data))

def db_to_rec(row):
    return {
        "ID":             row.get("id_pratica", ""),
        "Data":           row.get("data", ""),
        "Cliente":        row.get("cliente", ""),
        "Valore":         row.get("valore") or 0,
        "Stato":          row.get("stato", ""),
        "Operatore":      row.get("operatore", ""),
        "Esito":          row.get("esito", ""),
        "Sintesi_AI":     row.get("sintesi_ai") or "",
        "Note":           row.get("note") or "",
        "Assegnato_a":    row.get("assegnato_a") or "",
        "Stato_workflow": row.get("stato_workflow") or "in_elaborazione",
        "PDF_nota":       row.get("pdf_nota") or "",
        "DOCX_bozza":     row.get("docx_bozza") or "",
        "PDF_reclamo":       row.get("pdf_reclamo") or "",
        "Sintesi_reclamo":   row.get("sintesi_reclamo") or "",
        "Sintesi_analisi":   row.get("sintesi_analisi") or "",
        "Proposta_decisione":row.get("proposta_decisione") or "",
        "Bozza_modificata":  row.get("bozza_modificata") or "",
        "Data_archiviazione":row.get("data_archiviazione") or "",
    }

def rec_to_db(rec: dict):
    return {
        "id_pratica":    rec["ID"],
        "data":          rec["Data"],
        "cliente":       rec["Cliente"],
        "valore":        rec["Valore"],
        "stato":         rec["Stato"],
        "operatore":     rec["Operatore"],
        "esito":         rec["Esito"],
        "sintesi_ai":    rec.get("Sintesi_AI", ""),
        "note":          rec.get("Note", ""),
        "assegnato_a":   rec.get("Assegnato_a", ""),
        "stato_workflow":rec.get("Stato_workflow", "in_elaborazione"),
        "pdf_nota":      rec.get("PDF_nota", ""),
        "docx_bozza":    rec.get("DOCX_bozza", ""),
        "pdf_reclamo":   rec.get("PDF_reclamo", ""),
    }

ESEMPI = [
    {"ID":"REC-24-001","Data":"01/03/24","Cliente":"Mario Rossi","Valore":1200,
     "Stato":"Attivo","Operatore":"M. Rossi","Esito":"In analisi",
     "Sintesi_AI":"Il cliente lamenta il mancato rimborso di un'operazione di pagamento non autorizzata di € 1.200,00 su conto corrente, con violazione dei termini previsti dal D.Lgs. 11/2010. L'art. 11 impone il rimborso immediato salvo dolo del pagatore. Tre decisioni ABF recenti (Milano 2023, Roma 2022, Napoli 2023) confermano l'orientamento favorevole al ricorrente.",
     "Note":"","Assegnato_a":"M. Rossi","Stato_workflow":"elaborato",
     "PDF_nota":"#","DOCX_bozza":"#","PDF_reclamo":"#"},
    {"ID":"REC-24-002","Data":"02/03/24","Cliente":"Luigi Bianchi","Valore":8500,
     "Stato":"Attivo","Operatore":"E. Verdi","Esito":"Draft",
     "Sintesi_AI":"","Note":"","Assegnato_a":"E. Verdi","Stato_workflow":"in_elaborazione",
     "PDF_nota":"","DOCX_bozza":"","PDF_reclamo":"#"},
    {"ID":"REC-24-003","Data":"15/02/24","Cliente":"S.P.A. Edilizia Progetti","Valore":15000,
     "Stato":"Archiviato","Operatore":"M. Rossi","Esito":"Rigettato",
     "Sintesi_AI":"Il reclamo concerneva l'applicazione di commissioni su affidamento non pattuite. L'analisi ha evidenziato che le commissioni erano previste nel contratto sottoscritto. Il reclamo è stato rigettato in quanto privo di fondamento contrattuale.",
     "Note":"Cliente informato via PEC in data 20/02/24.","Assegnato_a":"M. Rossi",
     "Stato_workflow":"elaborato","PDF_nota":"#","DOCX_bozza":"#","PDF_reclamo":"#"},
    {"ID":"REC-24-004","Data":"10/02/24","Cliente":"Maria Neri","Valore":450,
     "Stato":"Archiviato","Operatore":"E. Verdi","Esito":"Accolto",
     "Sintesi_AI":"Operazione di pagamento non eseguita con addebito del conto. La banca ha riconosciuto l'errore tecnico. Il rimborso di € 450,00 è stato disposto con accredito immediato.",
     "Note":"Rimborso accreditato il 14/02/24.","Assegnato_a":"E. Verdi",
     "Stato_workflow":"elaborato","PDF_nota":"#","DOCX_bozza":"#","PDF_reclamo":"#"},
]

@st.cache_data(ttl=5)
def get_db():
    rows = sb_get()
    if not rows:
        for e in ESEMPI:
            sb_insert(rec_to_db(e))
        rows = sb_get()
    return [db_to_rec(r) for r in rows]

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600;700&display=swap');

.stApp { background-color: #cbd5e1; }
/* primary buttons = blu RE */
.stButton button[kind="primary"] { background:#3B82F6 !important; border:none !important; }
.stButton button[kind="primary"]:hover { background:#2563eb !important; }
[data-testid="stSidebar"] { background-color: #111827 !important; }
.brand-title { font-family:'Playfair Display',serif; color:#fff; font-size:32px; margin-bottom:0; padding-left:5px; }
.resolva-watermark { position:fixed; top:24px; right:32px; z-index:999; pointer-events:none;
    font-family:'Playfair Display',serif; font-size:18px; letter-spacing:6px; user-select:none; }
.resolva-watermark .wm-re { color:#7B9CC4; opacity:0.4; }
.resolva-watermark .wm-solva { color:#1e293b; opacity:0.12; }
.brand-subtitle { font-family:'Inter',sans-serif; color:#94A3B8; font-size:13px; text-transform:uppercase;
    letter-spacing:2px; margin-top:-5px; margin-bottom:20px; padding-left:5px; }
[data-testid="stSidebar"] .stButton > button {
    background:transparent !important; color:#94A3B8 !important; border:none !important;
    text-align:left !important; font-size:16px !important; font-weight:500 !important;
    padding:8px 10px !important; width:100% !important; box-shadow:none !important; }
[data-testid="stSidebar"] .stButton > button:hover { color:#fff !important; background:#1F2937 !important; }
.header-container { display:flex; align-items:center; margin-bottom:24px; }
.main-title { font-family:'Playfair Display',serif; font-size:26px; font-weight:700; text-transform:uppercase; letter-spacing:.18em; color:#1e293b; margin-right:16px; }
.counter-badge { background:#3B82F6; color:white; border-radius:50%; width:36px; height:36px;
    display:flex; align-items:center; justify-content:center;
    font-family:'Inter',sans-serif; font-size:13px; font-weight:700; box-shadow:0 4px 10px rgba(0,0,0,.15); }
div[data-testid="stSidebar"] .stTextInput input {
    background:#1F2937 !important; color:white !important; border:1px solid #374151 !important; border-radius:4px; }
.sidebar-divider { border-bottom:1px solid #374151; margin:15px 0; }

.pro-table { width:100%; border-collapse:collapse; font-family:'Inter',sans-serif;
    box-shadow:0 2px 12px rgba(0,0,0,.10); border-radius:8px; overflow:hidden; margin-bottom:8px; }
.pro-table thead tr th { background:#1e293b; color:#fff; padding:13px 16px; font-size:11px;
    text-transform:uppercase; letter-spacing:.10em; font-weight:700; text-align:left;
    border-bottom:none; white-space:nowrap; }
.pro-table tbody tr td { padding:13px 16px; font-size:14px; color:#1e293b;
    border-bottom:1px solid #e2e8f0; background:#fff; vertical-align:middle; }
.pro-table tbody tr:last-child td { border-bottom:none; }
.pro-table tbody tr:nth-child(even) td { background:#f8fafc; }
.pro-table tbody tr:hover td { background:#eff6ff; transition:background .12s; }
.pro-table-arch thead tr th { background:#1e293b !important; }
.pro-table-arch tbody tr:nth-child(even) td { background:#fdf2f5; }
.pro-table-arch tbody tr:hover td { background:#fce7ef; transition:background .12s; }
.col-id { font-weight:700; color:#0f172a; white-space:nowrap; }
.col-val { white-space:nowrap; font-variant-numeric:tabular-nums; }
.badge { display:inline-block; padding:4px 11px; border-radius:999px; font-size:12px; font-weight:600; white-space:nowrap; }
.badge-accolto       { background:#dcfce7; color:#15803d; }
.badge-rigettato     { background:#fee2e2; color:#b91c1c; }
.badge-analisi       { background:#dcfce7; color:#166534; }
.badge-draft         { background:#dbeafe; color:#1e40af; }
.badge-responsabile  { background:#16a34a; color:#ffffff; }
.badge-istruttoria   { background:#fef9c3; color:#854d0e; }

.fascicolo-header { background:#1e293b; border-radius:10px; padding:24px 32px; margin-bottom:20px;
    display:flex; align-items:center; justify-content:space-between; }
.fascicolo-id { font-family:'Playfair Display',serif; color:#fff; font-size:28px; margin:0; }
.fascicolo-meta { font-family:'Inter',sans-serif; color:#94A3B8; font-size:13px; margin-top:6px; }
.status-pill { display:inline-block; padding:6px 18px; border-radius:999px;
    font-family:'Inter',sans-serif; font-size:13px; font-weight:700; }
.status-attivo { background:#dbeafe; color:#1d4ed8; }
.status-archiviato { background:#e2e8f0; color:#475569; }

.sec-header { display:flex; align-items:center; gap:10px; background:transparent;
    border:none; padding:0; margin-top:28px; margin-bottom:10px; }
.sec-header.green {}
.sec-header.slate {}
.sec-header.amber {}
.sec-header.red {}
.sec-header.blue .sec-title { color:#3B82F6; }
.sec-header.bordeaux .sec-title { color:#6B1F3A; }
.sec-icon { display:none; }
.sec-title { font-family:'Playfair Display',serif; font-size:15px; font-weight:700;
    text-transform:uppercase; letter-spacing:.18em; color:#1e293b; }
.sec-body { background:white; border-radius:10px; padding:20px 24px;
    margin-bottom:6px; box-shadow:0 2px 12px rgba(0,0,0,.06); }

.ai-summary { font-family:'Inter',sans-serif; font-size:14px; color:#1e293b; line-height:1.85;
    text-align:justify; padding:20px 24px; border-radius:10px;
    background:white; box-shadow:0 2px 12px rgba(0,0,0,.06); margin-bottom:0; }
.ai-label { display:none; }
.doc-card { display:flex; align-items:center; justify-content:space-between;
    background:#1e293b; border-radius:10px; padding:18px 24px; margin-bottom:12px;
    text-decoration:none; transition:background .15s; }
.doc-card:hover { background:#0f172a; }
.doc-card-title { font-family:'Playfair Display',serif; font-size:16px; color:#fff; font-weight:700; }
.doc-card-sub { font-family:'Inter',sans-serif; font-size:12px; color:#94a3b8; margin-top:3px; }
.doc-card-arrow { font-size:20px; color:#3B82F6; }
.workflow-step { display:flex; align-items:flex-start; gap:14px; padding:10px 0; border-bottom:1px solid #f1f5f9; }
.workflow-step:last-child { border-bottom:none; }
.step-icon { width:30px; height:30px; border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:13px; flex-shrink:0; }
.step-done { background:#dcfce7; } .step-pending { background:#fef9c3; } .step-wait { background:#f1f5f9; }
.step-text { font-family:'Inter',sans-serif; font-size:13px; color:#374151; font-weight:500; }
.step-date { font-size:11px; color:#94a3b8; margin-top:2px; }

.fascicolo-header-arch { background:#6B1F3A !important; }
</style>
""", unsafe_allow_html=True)

# ── STATO (deve essere prima dell'autorefresh) ──
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'utente' not in st.session_state:
    st.session_state.utente = ""
if 'ruolo' not in st.session_state:
    st.session_state.ruolo = ""

# ── AUTO REFRESH ogni 20 secondi ──
st_autorefresh(interval=20000, key="autorefresh")

UTENTI = {
    "operatore": {"password": "resolva2026", "ruolo": "Operatore", "nome": "M. Rossi"},
    "responsabile": {"password": "resolva2026", "ruolo": "Responsabile", "nome": "A. Baldaccini"},
}

# ── LOGIN GATE ──
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display:none; }
    .stApp { background:#1e293b; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="margin-top:80px;text-align:center;margin-bottom:40px;">
            <p style="font-family:Playfair Display,serif;font-size:32px;font-weight:700;
            color:white;letter-spacing:.18em;text-transform:uppercase;margin-bottom:4px;">
            <span style="color:#3B82F6;">R E</span>&nbsp;&nbsp;S O L V A</p>
            <p style="font-family:Inter,sans-serif;font-size:12px;color:#64748b;
            letter-spacing:.15em;text-transform:uppercase;">Gestione Reclami Bancari</p>
        </div>
        """, unsafe_allow_html=True)
        
        utente_input = st.text_input("Utente", placeholder="Nome utente", label_visibility="collapsed")
        password_input = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        
        if st.button("Accedi", use_container_width=True, type="primary"):
            u = utente_input.strip().lower()
            if u in UTENTI and UTENTI[u]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.utente = UTENTI[u]["nome"]
                st.session_state.ruolo = UTENTI[u]["ruolo"]
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error("Credenziali non valide.")
        
        st.markdown("""
        <p style="font-family:Inter,sans-serif;font-size:11px;color:#475569;
        text-align:center;margin-top:24px;">
        Demo: <b style="color:#64748b">operatore</b> o <b style="color:#64748b">responsabile</b> · password: resolva2026
        </p>""", unsafe_allow_html=True)
    st.stop()



OPERATORI = ["M. Rossi", "E. Verdi", "F. Bruno", "C. Marino"]

def badge(esito):
    labels = {"In analisi":"Resolva Processing","Draft":"Human Review",
              "Al responsabile":"Pending Approval","In istruttoria":"On Hold"}
    display = labels.get(esito, esito)
    cls = {"In analisi":"badge-analisi","Draft":"badge-draft",
           "Rigettato":"badge-rigettato","Accolto":"badge-accolto",
           "Al responsabile":"badge-responsabile","In istruttoria":"badge-istruttoria"}.get(esito,"")
    return f'<span class="badge {cls}">{display}</span>'

def get_rec(id_, db):
    for r in db:
        if r["ID"] == id_: return r
    return None

def sec(icon, title, color=""):
    st.markdown(f'<div class="sec-header {color}"><span class="sec-icon">{icon}</span>'
                f'<span class="sec-title">{title}</span></div>', unsafe_allow_html=True)

def build_table(data, cols, headers, table_class='pro-table'):
    rows = ""
    for _, row in data.iterrows():
        cells = ""
        for c in cols:
            if c == "Valore":   cells += f'<td class="col-val">€ {row[c]:,}</td>'
            elif c == "ID":     cells += f'<td class="col-id">{row[c]}</td>'
            elif c == "Esito":  cells += f'<td>{badge(row[c])}</td>'
            else:               cells += f'<td>{row[c]}</td>'
        rows += f"<tr>{cells}</tr>"
    ths = "".join(f"<th>{h}</th>" for h in headers)
    return f'<table class="pro-table"><thead><tr>{ths}</tr></thead><tbody>{rows}</tbody></table>'

# ── TOPBAR ──
st.markdown(f"""
<div style="position:fixed;top:0;left:0;right:0;height:48px;background:#1e293b;
    display:flex;align-items:center;justify-content:space-between;
    padding:0 32px;z-index:9999;box-shadow:0 2px 8px rgba(0,0,0,.3);">
    <span style="font-family:Playfair Display,serif;font-size:14px;font-weight:700;
    color:white;text-transform:uppercase;letter-spacing:.15em;">
    <span style="color:#3B82F6;">R E</span>&nbsp;&nbsp;S O L V A</span>
    <span style="font-family:Inter,sans-serif;font-size:12px;color:#94a3b8;">
    {st.session_state.utente} &nbsp;·&nbsp; 
    <span style="color:#3B82F6;">{st.session_state.ruolo}</span></span>
</div>
<div style="height:48px;"></div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<p class="brand-title"><span style="color:#3B82F6;letter-spacing:4px">R E</span><span style="letter-spacing:4px"> &nbsp;S O L V A</span></p><p class="brand-subtitle">Gestione reclami</p>',
                unsafe_allow_html=True)
    if st.button("Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    if st.button("Sincronizzazione pec"): st.toast("Disponibile nella versione completa")
    if st.button("Carica reclamo"): st.session_state.page = "Carica reclamo"; st.rerun()
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    if st.button("Reclami attivi"): st.session_state.page = "Reclami attivi"; st.rerun()
    if st.button("Reclami archiviati"): st.session_state.page = "Reclami archiviati"; st.rerun()
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    if st.button("Statistiche"): st.session_state.page = "Statistiche"; st.rerun()
    st.markdown('<div style="flex:1;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    _u = st.session_state.get("utente","")
    _r = st.session_state.get("ruolo","")
    st.markdown(
        f'<div style="padding:10px 8px 4px 8px;">'
        f'<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;'
        f'color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin:0 0 2px 0;">{_r}</p>'
        f'<p style="font-family:Inter,sans-serif;font-size:14px;font-weight:600;'
        f'color:#e2e8f0;margin:0;">{_u}</p>'
        f'</div>', unsafe_allow_html=True)
    if st.button("Esci", key="logout"):
        st.session_state.logged_in = False
        st.session_state.utente = ""
        st.session_state.ruolo = ""
        st.session_state.page = "Dashboard"
        st.rerun()
    st.markdown("<br>" * 8, unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="Cerca...", key="search_sidebar", label_visibility="collapsed")

# ── DATI ──
db = get_db()
df = pd.DataFrame(db)
if search_query and not df.empty:
    df = df[df['Cliente'].str.contains(search_query, case=False) |
            df['ID'].str.contains(search_query, case=False)]


# ============================================================
# 1. RECLAMI ATTIVI
# ============================================================
# ============================================================
# 0. DASHBOARD
# ============================================================
st.markdown(
    '<div style="position:fixed;top:16px;right:40px;z-index:9999;pointer-events:none;'  
    'font-family:Playfair Display,serif;font-size:17px;letter-spacing:6px;">'
    '<span style="color:#7B9CC4;opacity:0.5;">R E</span>'
    '<span style="color:#94a3b8;opacity:0.3;">&nbsp;&nbsp;S O L V A</span>'
    '</div>', unsafe_allow_html=True)

if st.session_state.page == "Dashboard":
    db_now = get_db()
    df_all = pd.DataFrame(db_now) if get_db() else pd.DataFrame()

    ruolo = st.session_state.ruolo

    # ── dati calcolati ──
    if not df_all.empty:
        attivi_df     = df_all[df_all['Stato'] == 'Attivo']
        archiviati_df = df_all[df_all['Stato'] == 'Archiviato']
        da_assegnare  = attivi_df[attivi_df['Operatore'].isin(['Da assegnare', '', None])] if not attivi_df.empty else pd.DataFrame()
        da_approvare  = attivi_df[attivi_df['Esito'] == 'Al responsabile'] if not attivi_df.empty else pd.DataFrame()
        da_istruttoria = attivi_df[attivi_df['Esito'] == 'In istruttoria'] if not attivi_df.empty else pd.DataFrame()
        accolti_df    = df_all[df_all['Esito'] == 'Accolto']
        rigettati_df  = df_all[df_all['Esito'] == 'Rigettato']
        n_attivi      = len(attivi_df)
        n_archiviate  = len(archiviati_df)
        n_accolti     = len(accolti_df)
        n_rigettati   = len(rigettati_df)
        valore_tot    = int(attivi_df['Valore'].sum()) if not attivi_df.empty else 0
        valore_medio  = int(df_all['Valore'].mean()) if not df_all.empty else 0
        totale_chiuse = max(n_accolti + n_rigettati, 1)
        tasso_accolto = int(n_accolti / totale_chiuse * 100)
        tasso_rigetto = int(n_rigettati / totale_chiuse * 100)
    else:
        attivi_df = da_assegnare = da_approvare = archiviati_df = pd.DataFrame()
        n_attivi = n_archiviate = n_accolti = n_rigettati = valore_tot = valore_medio = 0
        tasso_accolto = tasso_rigetto = 0

    # ══════════════════════════════════════════════
    # DASHBOARD RESPONSABILE
    # ══════════════════════════════════════════════
    if ruolo == "Responsabile":

        # Titolo
        st.markdown(
            '<p style="font-family:Playfair Display,serif;font-size:26px;font-weight:700;'
            'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;margin-bottom:24px;">'
            'Dashboard · Responsabile</p>',
            unsafe_allow_html=True)

        # ── CSS pulsanti rossi ──
        st.markdown("""<style>
        /* hover azzurro sulle card statistiche e PEC */
        .kpi-card, .pec-card { transition: box-shadow .2s, transform .15s; cursor:default; }
        .kpi-card:hover, .pec-card:hover { 
            box-shadow: 0 4px 20px rgba(59,130,246,.25) !important;
            transform: translateY(-2px); }
        /* hover azzurro selettori */
        div[data-baseweb="select"] > div:hover { border-color:#3B82F6 !important; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: white !important;
            border-radius: 14px !important;
            border: 1px solid rgba(203,213,225,0.7) !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important;
            transition: box-shadow 0.2s, transform 0.15s !important;
            padding: 8px 4px !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 6px 24px rgba(59,130,246,0.15) !important;
            transform: translateY(-2px) !important;
        }
        </style>""", unsafe_allow_html=True)

        # ══ TASK 1: SINCRONIZZA PEC ══
        with st.container(border=True):
          st.markdown(
            '<p style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
            'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;margin-bottom:12px;">'
            'Sincronizzazione PEC</p>', unsafe_allow_html=True)
          st.markdown(
            '<div class="pec-card" style="background:#e2e8f0;border-radius:10px;padding:20px 24px;margin-bottom:28px;">'
            '<p style="font-family:Inter,sans-serif;font-size:11px;font-weight:700;color:#64748b;'
            'text-transform:uppercase;letter-spacing:.1em;margin:0 0 6px 0;">Ultima sincronizzazione</p>'
            '<p style="font-family:Playfair Display,serif;font-size:20px;font-weight:700;'
            'color:#1e293b;margin:0;">06/03/2026 &nbsp;·&nbsp; 08:45</p>'
            '</div>', unsafe_allow_html=True)
          _, pec_btn = st.columns([4,1])
          with pec_btn:
            if st.button("Sincronizza", use_container_width=True, type="primary"):
                st.toast("Sincronizzazione PEC disponibile nella versione completa")

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # ══ TASK 2+3+4: GESTIONE PRATICHE ══
        with st.container(border=True):

            # PRATICHE DA ASSEGNARE
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">'
                f'<span style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;">Pratiche da assegnare</span>'
                f'<span style="background:#f59e0b;color:white;font-family:Inter,sans-serif;font-size:12px;'
                f'font-weight:700;border-radius:50%;width:24px;height:24px;display:inline-flex;'
                f'align-items:center;justify-content:center;">{len(da_assegnare)}</span></div>',
                unsafe_allow_html=True)

            if da_assegnare.empty:
                st.info("Nessuna pratica da assegnare.")
            else:
                col_pratica, col_operatore = st.columns([3, 2])
                with col_pratica:
                    labels_ass = [
                        f"{r['ID']}  ·  {r['Cliente']}  ·  € {int(r['Valore']):,}"
                        for _, r in da_assegnare.iterrows()
                    ]
                    pratica_label = st.selectbox("Pratica da assegnare", labels_ass, label_visibility="visible")
                    pratica_id = da_assegnare.iloc[labels_ass.index(pratica_label)]["ID"]
                with col_operatore:
                    op_scelto = st.selectbox("Assegna a", OPERATORI, label_visibility="visible")
                _, btn_ass = st.columns([4, 1])
                with btn_ass:
                    if st.button("Assegna", use_container_width=True, key="assegna_main", type="primary"):
                        sb_update(pratica_id, {"operatore": op_scelto, "assegnato_a": op_scelto})
                        get_db.clear()
                        st.rerun()

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # IN ATTESA DI APPROVAZIONE
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">'
                f'<span style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;">In attesa di approvazione</span>'
                f'<span style="background:#3B82F6;color:white;font-family:Inter,sans-serif;font-size:12px;'
                f'font-weight:700;border-radius:50%;width:24px;height:24px;display:inline-flex;'
                f'align-items:center;justify-content:center;">{len(da_approvare)}</span></div>',
                unsafe_allow_html=True)

            if da_approvare.empty:
                st.info("Nessuna pratica in attesa di approvazione.")
            else:
                labels_appr = [
                    f"{r['ID']}  ·  {r['Cliente']}  ·  € {int(r['Valore']):,}"
                    for _, r in da_approvare.iterrows()
                ]
                appr_label = st.selectbox("Seleziona pratica da revisionare", labels_appr, label_visibility="visible")
                appr_id = da_approvare.iloc[labels_appr.index(appr_label)]["ID"]
                _, btn_appr = st.columns([4, 1])
                with btn_appr:
                    if st.button("Apri", use_container_width=True, key="apri_appr", type="primary"):
                        st.session_state.id_selezionato = appr_id
                        st.session_state.page = "Dettaglio pratica"
                        st.rerun()

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # SUPPLEMENTO ISTRUTTORIO
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">'
                f'<span style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;">Supplemento istruttorio</span>'
                f'<span style="background:#92400e;color:white;font-family:Inter,sans-serif;font-size:12px;'
                f'font-weight:700;border-radius:50%;width:24px;height:24px;display:inline-flex;'
                f'align-items:center;justify-content:center;">{len(da_istruttoria)}</span></div>',
                unsafe_allow_html=True)

            if da_istruttoria.empty:
                st.info("Nessuna pratica in supplemento istruttorio.")
            else:
                labels_istr = [
                    f"{r['ID']}  ·  {r['Cliente']}  ·  {r.get('Note','') or 'nessuna nota'}"
                    for _, r in da_istruttoria.iterrows()
                ]
                istr_label = st.selectbox("Pratica in istruttoria", labels_istr, label_visibility="visible")
                istr_id    = da_istruttoria.iloc[labels_istr.index(istr_label)]["ID"]
                istr_note  = da_istruttoria.iloc[labels_istr.index(istr_label)].get("Note", "") or ""
                if istr_note:
                    st.markdown(
                        f'<div style="background:#fef3c7;border-radius:8px;padding:10px 16px;margin:8px 0;">'
                        f'<p style="font-family:Inter,sans-serif;font-size:11px;font-weight:700;'
                        f'color:#92400e;text-transform:uppercase;letter-spacing:.08em;margin:0 0 4px 0;">'
                        f'Supplemento richiesto</p>'
                        f'<p style="font-family:Inter,sans-serif;font-size:13px;color:#78350f;margin:0;">'
                        f'{istr_note}</p></div>',
                        unsafe_allow_html=True)
                destinatario = st.text_input("Destinatario / Unità competente",
                    placeholder="es. Ufficio tassi, Ufficio titoli, Compliance...",
                    key=f"dest_istr_{istr_id}")
                _, btn_istr = st.columns([4, 1])
                with btn_istr:
                    if st.button("Invia supplemento", use_container_width=True,
                                 key="invia_istr", type="primary"):
                        if destinatario:
                            sb_update(istr_id, {"esito": "In istruttoria",
                                                "stato_workflow": "istruttoria_inviata"})
                            get_db.clear()
                            st.toast(f"Supplemento inviato a {destinatario}")
                            st.rerun()
                        else:
                            st.warning("Inserire il destinatario prima di inviare.")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                # ══ STATISTICHE OPERATIVE ══
        with st.container(border=True):
         st.markdown(
            '<p style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
            'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;margin-bottom:16px;">'
            'Statistiche operative</p>', unsafe_allow_html=True)

        from datetime import datetime, timedelta
        oggi   = datetime.now().date()
        filtri = {"Oggi": oggi, "Settimana": oggi-timedelta(days=7),
                  "Mese": oggi-timedelta(days=30), "Anno": oggi-timedelta(days=365)}
        periodo_sel = st.selectbox("Periodo", list(filtri.keys()), key="periodo_stats", label_visibility="visible")
        data_da = filtri[periodo_sel]

        def parse_data(d):
            try:    return datetime.strptime(str(d), "%d/%m/%y").date()
            except:
                try: return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
                except: return None

        df_all["_data"]  = df_all["Data"].apply(parse_data) if not df_all.empty else None
        df_periodo       = df_all[df_all["_data"] >= data_da] if not df_all.empty else pd.DataFrame()
        arch_periodo     = df_periodo[df_periodo["Stato"] == "Archiviato"] if not df_periodo.empty else pd.DataFrame()
        attivi_periodo   = df_periodo[df_periodo["Stato"] == "Attivo"]     if not df_periodo.empty else pd.DataFrame()
        arch_da_op       = arch_periodo[arch_periodo["Valore"].apply(lambda v: float(v or 0) < 1000)]  if not arch_periodo.empty else pd.DataFrame()
        arch_da_resp     = arch_periodo[arch_periodo["Valore"].apply(lambda v: float(v or 0) >= 1000)] if not arch_periodo.empty else pd.DataFrame()
        arch_accolti     = arch_periodo[arch_periodo["Esito"] == "Accolto"]  if not arch_periodo.empty else pd.DataFrame()
        arch_rigettati   = arch_periodo[arch_periodo["Esito"] == "Rigettato"] if not arch_periodo.empty else pd.DataFrame()
        tot_chiusi       = max(len(arch_accolti) + len(arch_rigettati), 1)
        tasso_acc_p      = int(len(arch_accolti)   / tot_chiusi * 100)
        tasso_rig_p      = int(len(arch_rigettati) / tot_chiusi * 100)
        val_accolti      = int(arch_accolti["Valore"].sum())   if not arch_accolti.empty else 0
        val_rigettati    = int(arch_rigettati["Valore"].sum()) if not arch_rigettati.empty else 0
        n_da_ass  = len(attivi_periodo[attivi_periodo["Operatore"].isin(["Da assegnare","",None])]) if not attivi_periodo.empty else 0
        n_ass     = len(attivi_periodo[~attivi_periodo["Operatore"].isin(["Da assegnare","",None])]) if not attivi_periodo.empty else 0
        n_da_appr = len(attivi_periodo[attivi_periodo["Esito"] == "Al responsabile"]) if not attivi_periodo.empty else 0
        n_istr    = len(attivi_periodo[attivi_periodo["Esito"] == "In istruttoria"])  if not attivi_periodo.empty else 0

        def kpi_stat(col, label, value, sub, bg):
            col.markdown(
                f'<div style="background:{bg};border-radius:10px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,0.07);">'
                f'<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin:0 0 6px 0;">{label}</p>'
                f'<p style="font-family:Playfair Display,serif;font-size:28px;font-weight:700;color:#1e293b;margin:0 0 2px 0;line-height:1;">{value}</p>'
                f'<p style="font-family:Inter,sans-serif;font-size:11px;color:#94a3b8;margin:0;">{sub}</p>'
                f'</div>', unsafe_allow_html=True)

        def kpi_large(col, label, value, sub, bg):
            col.markdown(
                f'<div style="background:{bg};border-radius:10px;padding:20px 28px;box-shadow:0 1px 6px rgba(0,0,0,0.07);">'
                f'<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin:0 0 8px 0;">{label}</p>'
                f'<p style="font-family:Playfair Display,serif;font-size:32px;font-weight:700;color:#1e293b;margin:0 0 4px 0;line-height:1;">{value}</p>'
                f'<p style="font-family:Inter,sans-serif;font-size:12px;color:#94a3b8;margin:0;">{sub}</p>'
                f'</div>', unsafe_allow_html=True)

        st.markdown('<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.12em;margin:8px 0 10px 0;">Portafoglio attivo nel periodo</p>', unsafe_allow_html=True)
        ka1,ka2,ka3,ka4 = st.columns(4)
        kpi_stat(ka1, "Da assegnare",   n_da_ass,  "in attesa",       "#fef9ee")
        kpi_stat(ka2, "In lavorazione", n_ass,     "assegnati",       "#fef9ee")
        kpi_stat(ka3, "Da approvare",   n_da_appr, "al responsabile", "#fef9ee")
        kpi_stat(ka4, "In istruttoria", n_istr,    "supplemento",     "#fef9ee")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.12em;margin:8px 0 10px 0;">Reclami archiviati nel periodo</p>', unsafe_allow_html=True)
        kb1,kb2,kb3,kb4 = st.columns(4)
        kpi_stat(kb1, "Da operatore",       len(arch_da_op),   "risposte inviate",             "#fef3c7")
        kpi_stat(kb2, "Da responsabile",    len(arch_da_resp),  "risposte inviate",             "#fef3c7")
        kpi_stat(kb3, "Tasso accoglimento", f"{tasso_acc_p}%",  f"{len(arch_accolti)} pratiche","#fef3c7")
        kpi_stat(kb4, "Tasso rigetto",      f"{tasso_rig_p}%",  f"{len(arch_rigettati)} pratiche","#fef3c7")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.12em;margin:8px 0 10px 0;">Valore reclami nel periodo</p>', unsafe_allow_html=True)
        kc1, kc2 = st.columns(2)
        kpi_large(kc1, "Valore accolti",   f"€ {val_accolti:,}",   f"{len(arch_accolti)} pratiche accolte",    "#bbf7d0")
        kpi_large(kc2, "Valore rigettati", f"€ {val_rigettati:,}", f"{len(arch_rigettati)} pratiche rigettate", "#fecdd3")

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        _, col_btn_stat = st.columns([3, 1])
        with col_btn_stat:
            if st.button("Invia report statistiche", use_container_width=True, type="primary", key="invia_stats"):
                righe = [
                    "RESOLVA — Report statistiche operative",
                    f"Periodo: {periodo_sel}  |  Generato il {oggi.strftime('%d/%m/%Y')}",
                    "",
                    f"ATTIVI: Da assegnare {n_da_ass} · In lavorazione {n_ass} · Da approvare {n_da_appr} · In istruttoria {n_istr}",
                    f"ARCHIVIATI: Da operatore {len(arch_da_op)} · Da responsabile {len(arch_da_resp)}",
                    f"TASSI: Accoglimento {tasso_acc_p}% · Rigetto {tasso_rig_p}%",
                    f"VALORI: Accolti € {val_accolti:,} · Rigettati € {val_rigettati:,}",
                ]
                st.text_area("Testo report da copiare", value="\n".join(righe), height=160, key="txt_report_stats")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)


    else:
        # ══════════════════════════════════════════════
        # DASHBOARD OPERATORE
        # ══════════════════════════════════════════════
        nome_op = st.session_state.get("utente", "Operatore")

        st.markdown(
            f'<p style="font-family:Playfair Display,serif;font-size:26px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;margin-bottom:4px;">'
            f'Dashboard · Operatore</p>'
            f'<p style="font-family:Inter,sans-serif;font-size:14px;color:#64748b;margin-bottom:28px;">'
            f'Benvenuto, <strong>{nome_op}</strong></p>',
            unsafe_allow_html=True)

        # ── Filtra per operatore corrente ──
        mie_pratiche = attivi_df[attivi_df["Operatore"] == nome_op] if not attivi_df.empty else pd.DataFrame()

        n_processing  = len(mie_pratiche[mie_pratiche["Esito"] == "In analisi"])   if not mie_pratiche.empty else 0
        n_review      = len(mie_pratiche[mie_pratiche["Esito"] == "Draft"])         if not mie_pratiche.empty else 0
        n_approval    = len(mie_pratiche[mie_pratiche["Esito"] == "Al responsabile"]) if not mie_pratiche.empty else 0
        n_onhold      = len(mie_pratiche[mie_pratiche["Esito"] == "In istruttoria"]) if not mie_pratiche.empty else 0
        n_totali      = len(mie_pratiche)
        mie_arch      = archiviati_df[archiviati_df["Operatore"] == nome_op] if not archiviati_df.empty else pd.DataFrame()
        n_chiuse_mese = len(mie_arch)

        # ── KPI row ──
        k1,k2,k3,k4 = st.columns(4)
        def kpi_op(col, label, val, sub, bg, col_val="#1e293b"):
            col.markdown(
                f'<div class="kpi-card" style="background:{bg};border-radius:10px;padding:16px 20px;'
                f'box-shadow:0 2px 12px rgba(0,0,0,.06);text-align:center;">'
                f'<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;color:#64748b;'
                f'text-transform:uppercase;letter-spacing:.1em;margin:0 0 6px 0;">{label}</p>'
                f'<p style="font-family:Playfair Display,serif;font-size:32px;font-weight:700;'
                f'color:{col_val};margin:0 0 4px 0;">{val}</p>'
                f'<p style="font-family:Inter,sans-serif;font-size:11px;color:#94a3b8;margin:0;">{sub}</p>'
                f'</div>',
                unsafe_allow_html=True)

        kpi_op(k1, "Resolva Processing", n_processing, "in elaborazione",  "#dcfce7")
        kpi_op(k2, "Human Review",       n_review,     "da lavorare",       "#86efac")
        kpi_op(k3, "Pending Approval",   n_approval,   "inviate al resp.",  "#16a34a", "#ffffff")
        kpi_op(k4, "On Hold",            n_onhold,     "supplemento",       "#fef9c3")

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # ── KPI personali ──
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;color:#94a3b8;'
            'text-transform:uppercase;letter-spacing:.12em;margin:0 0 12px 0;">Il mio portafoglio</p>',
            unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        kpi_op(p1, "Pratiche aperte",    n_totali,     "totale assegnate",   "#f1f5f9")
        kpi_op(p2, "Chiuse",             n_chiuse_mese,"totale archiviate",  "#f1f5f9")
        kpi_op(p3, "Da lavorare oggi",   n_review,     "Human Review",       "#f1f5f9")

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # ── TASK 1: Human Review ──
        hr_pratiche = mie_pratiche[mie_pratiche["Esito"] == "Draft"] if not mie_pratiche.empty else pd.DataFrame()
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">'
            f'<span style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;">Human Review</span>'
            f'<span style="background:#16a34a;color:white;font-family:Inter,sans-serif;font-size:12px;'
            f'font-weight:700;border-radius:50%;width:24px;height:24px;display:inline-flex;'
            f'align-items:center;justify-content:center;">{len(hr_pratiche)}</span></div>',
            unsafe_allow_html=True)

        if hr_pratiche.empty:
            st.info("Nessuna pratica in attesa di revisione.")
        else:
            labels_hr = [f"{r['ID']}  ·  {r['Cliente']}  ·  € {int(r['Valore']):,}" for _, r in hr_pratiche.iterrows()]
            sel_hr = st.selectbox("Pratica da lavorare", labels_hr, label_visibility="visible", key="op_hr_sel")
            pratica_hr_id = hr_pratiche.iloc[labels_hr.index(sel_hr)]["ID"]
            _, btn_hr = st.columns([4,1])
            with btn_hr:
                if st.button("Apri fascicolo →", key="op_hr_btn", use_container_width=True, type="primary"):
                    st.session_state.selected_id = pratica_hr_id
                    st.session_state.page = "Fascicolo"
                    st.session_state.back_page = "Dashboard"
                    st.rerun()

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # ── TASK 2: Pending Approval ──
        pa_pratiche = mie_pratiche[mie_pratiche["Esito"] == "Al responsabile"] if not mie_pratiche.empty else pd.DataFrame()
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">'
            f'<span style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;">Pending Approval</span>'
            f'<span style="background:#3B82F6;color:white;font-family:Inter,sans-serif;font-size:12px;'
            f'font-weight:700;border-radius:50%;width:24px;height:24px;display:inline-flex;'
            f'align-items:center;justify-content:center;">{len(pa_pratiche)}</span></div>',
            unsafe_allow_html=True)

        if pa_pratiche.empty:
            st.info("Nessuna pratica in attesa di approvazione.")
        else:
            labels_pa = [f"{r['ID']}  ·  {r['Cliente']}  ·  € {int(r['Valore']):,}" for _, r in pa_pratiche.iterrows()]
            st.markdown(
                '<div style="background:#dbeafe;border-radius:8px;padding:14px 18px;">'
                + "".join([f'<p style="font-family:Inter,sans-serif;font-size:13px;color:#1e40af;margin:4px 0;">{l}</p>' for l in labels_pa])
                + '</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # ── TASK 3: On Hold ──
        oh_pratiche = mie_pratiche[mie_pratiche["Esito"] == "In istruttoria"] if not mie_pratiche.empty else pd.DataFrame()
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">'
            f'<span style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;">On Hold</span>'
            f'<span style="background:#d97706;color:white;font-family:Inter,sans-serif;font-size:12px;'
            f'font-weight:700;border-radius:50%;width:24px;height:24px;display:inline-flex;'
            f'align-items:center;justify-content:center;">{len(oh_pratiche)}</span></div>',
            unsafe_allow_html=True)

        if oh_pratiche.empty:
            st.info("Nessuna pratica in supplemento istruttorio.")
        else:
            labels_oh = [f"{r['ID']}  ·  {r['Cliente']}  ·  {r.get('Note','')[:60]}" for _, r in oh_pratiche.iterrows()]
            sel_oh = st.selectbox("Pratica in istruttoria", labels_oh, label_visibility="visible", key="op_oh_sel")
            pratica_oh_id = oh_pratiche.iloc[labels_oh.index(sel_oh)]["ID"]
            _, btn_oh = st.columns([4,1])
            with btn_oh:
                if st.button("Apri fascicolo →", key="op_oh_btn", use_container_width=True, type="primary"):
                    st.session_state.selected_id = pratica_oh_id
                    st.session_state.page = "Fascicolo"
                    st.session_state.back_page = "Dashboard"
                    st.rerun()

        st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

elif st.session_state.page == "Reclami attivi":
    _ruolo_ra = st.session_state.get("ruolo", "")
    _nome_ra  = st.session_state.get("utente", "")
    if _ruolo_ra == "Operatore":
        data_all = df[(df['Stato'] == "Attivo") & (df['Operatore'] == _nome_ra)].reset_index(drop=True)
    else:
        data_all = df[df['Stato'] == "Attivo"].reset_index(drop=True)

    st.markdown("""<style>
    /* selectbox hover */
    div[data-baseweb="select"] > div { transition: border-color .15s, box-shadow .15s; }
    div[data-baseweb="select"] > div:hover { border-color:#3B82F6 !important; box-shadow:0 0 0 2px rgba(59,130,246,.25) !important; }
    div[data-baseweb="select"] > div:focus-within { border-color:#3B82F6 !important; box-shadow:0 0 0 2px rgba(59,130,246,.25) !important; }
    /* text input hover/focus */
    div[data-testid="stTextInput"] input:hover { border-color:#3B82F6 !important; }
    div[data-testid="stTextInput"] input:focus { border-color:#3B82F6 !important; box-shadow:0 0 0 2px rgba(59,130,246,.25) !important; }
    /* align selectbox and button to same height */
    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"],
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] { margin-top:0 !important; padding-top:0 !important; }
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button { height:42px !important; margin-top:0 !important; }
    </style>""", unsafe_allow_html=True)

    # Titolo + cerca sulla stessa riga, allineati
    col_title, col_cerca = st.columns([3, 2])
    with col_title:
        st.markdown(
            f'<div class="header-container">'
            f'<span class="main-title">Reclami attivi</span>'
            f'<div class="counter-badge">{len(data_all)}</div></div>',
            unsafe_allow_html=True)
    with col_cerca:
        cerca = st.text_input("", placeholder="Cerca per nome cliente...", label_visibility="collapsed")

    data_view = data_all.copy()
    if cerca:
        data_view = data_all[data_all["Cliente"].str.contains(cerca, case=False, na=False)].reset_index(drop=True)

    if data_view.empty:
        st.info("Nessun reclamo trovato.")
    else:
        st.markdown(build_table(data_view,
            ["ID","Data","Cliente","Valore","Operatore","Esito"],
            ["ID Pratica","Data","Cliente","Valore (€)","Operatore","Stato"]), unsafe_allow_html=True)
        ids = data_view["ID"].tolist()
        labels = [f"{r['ID']} — {r['Cliente']}" for _, r in data_view.iterrows()]
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            scelta = st.selectbox("Seleziona pratica", labels, label_visibility="collapsed")
        with col_btn:
            st.markdown("""<style>
            div[data-testid="stMainBlockContainer"] button[kind="secondary"] {
                background:#3B82F6 !important; color:white !important;
                border:none !important; font-weight:600 !important;
            }
            div[data-testid="stMainBlockContainer"] button[kind="secondary"]:hover {
                background:#2563eb !important;
            }
            </style>""", unsafe_allow_html=True)
            st.markdown("""<style>
            /* force button same height as selectbox */
            div[data-testid="stHorizontalBlock"]:last-of-type div[data-testid="stButton"] {
                display:flex; align-items:center;
            }
            div[data-testid="stHorizontalBlock"]:last-of-type div[data-testid="stButton"] button {
                height:46px !important; margin-top:0 !important; padding-top:0 !important; padding-bottom:0 !important;
            }
            div[data-testid="stHorizontalBlock"]:last-of-type div[data-baseweb="select"] > div {
                height:46px !important; min-height:46px !important;
            }
            </style>""", unsafe_allow_html=True)
            if st.button("Apri pratica →", use_container_width=True):
                st.session_state.id_selezionato = ids[labels.index(scelta)]
                st.session_state.page = "Dettaglio pratica"
                st.rerun()

# ============================================================
# 2. RECLAMI ARCHIVIATI
# ============================================================
elif st.session_state.page == "Reclami archiviati":
    data_arch = df[df['Stato'] == "Archiviato"].reset_index(drop=True)
    if "Data_archiviazione" not in data_arch.columns:
        data_arch["Data_archiviazione"] = ""

    st.markdown("""<style>
    div[data-baseweb="select"] > div { transition: border-color .15s, box-shadow .15s; }
    div[data-baseweb="select"] > div:hover { border-color:#3B82F6 !important; box-shadow:0 0 0 2px rgba(59,130,246,.25) !important; }
    div[data-baseweb="select"] > div:focus-within { border-color:#3B82F6 !important; box-shadow:0 0 0 2px rgba(59,130,246,.25) !important; }
    div[data-testid="stTextInput"] input:hover { border-color:#3B82F6 !important; }
    div[data-testid="stTextInput"] input:focus { border-color:#3B82F6 !important; box-shadow:0 0 0 2px rgba(59,130,246,.25) !important; }
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button { height:42px !important; margin-top:0 !important; }
    </style>""", unsafe_allow_html=True)

    col_title, col_cerca = st.columns([3, 2])
    with col_title:
        st.markdown(
            f'<div class="header-container">'
            f'<span class="main-title">Reclami archiviati</span>'
            f'<div class="counter-badge" style="background:#64748b;">{len(data_arch)}</div></div>',
            unsafe_allow_html=True)
    with col_cerca:
        cerca_arch = st.text_input("", placeholder="Cerca per nome cliente...",
                                   label_visibility="collapsed", key="cerca_arch")

    data_arch_view = data_arch.copy()
    if cerca_arch:
        data_arch_view = data_arch[data_arch["Cliente"].str.contains(cerca_arch, case=False, na=False)].reset_index(drop=True)

    if data_arch_view.empty:
        st.info("Nessun reclamo archiviato trovato.")
    else:
        st.markdown(build_table(data_arch_view,
            ["ID","Data","Cliente","Valore","Operatore","Esito","Data_archiviazione"],
            ["Fascicolo","Data","Cliente","Valore (€)","Operatore","Esito","Risposta inviata"],
            table_class="pro-table pro-table-arch"),
            unsafe_allow_html=True)

        ids_arch    = data_arch_view["ID"].tolist()
        labels_arch = [f"{r['ID']} — {r['Cliente']} — {r['Esito']}" for _, r in data_arch_view.iterrows()]
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            scelta_arch = st.selectbox("Seleziona pratica archiviata", labels_arch,
                                       label_visibility="collapsed", key="sel_arch")
        with col_btn:
            st.markdown("""<style>
            div[data-testid="stHorizontalBlock"]:last-of-type div[data-testid="stButton"] {
                display:flex; align-items:center;
            }
            div[data-testid="stHorizontalBlock"]:last-of-type div[data-testid="stButton"] button {
                height:46px !important; margin-top:0 !important;
                background:#3B82F6 !important; color:white !important;
                border:none !important; font-weight:600 !important;
            }
            div[data-testid="stHorizontalBlock"]:last-of-type div[data-baseweb="select"] > div {
                height:46px !important; min-height:46px !important;
            }
            </style>""", unsafe_allow_html=True)
            if st.button("Apri fascicolo →", use_container_width=True, key="apri_arch"):
                st.session_state.id_selezionato = ids_arch[labels_arch.index(scelta_arch)]
                st.session_state.page = "Dettaglio pratica"
                st.rerun()


# ============================================================
# 3. STATISTICHE
# ============================================================
elif st.session_state.page == "Statistiche":
    st.markdown('<div class="header-container"><span class="main-title">Statistiche</span></div>',
                unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pratiche evase", "142", "Totale storico")
    m2.metric("Accolti", "89", "62%")
    m3.metric("Rigettati", "53", "38%")
    m4.metric("Valore totale", "€ 42.500")
    st.divider()
    if not df.empty:
        st.write("### Carico di lavoro per operatore")
        fig = px.bar(df, x="Operatore", color="Esito", barmode="group",
                     template="simple_white", color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 4. CARICA RECLAMO
# ============================================================
elif st.session_state.page == "Carica reclamo":
    st.markdown('<div class="header-container"><span class="main-title">Carica reclamo</span></div>',
                unsafe_allow_html=True)

    col_testo, col_pdf = st.columns(2)

    with col_testo:
        st.markdown("""
        <div style="background:#1e293b;border-radius:10px;padding:16px 20px;margin-bottom:8px;">
            <span style="font-family:Inter,sans-serif;font-size:11px;font-weight:700;
            color:#94a3b8;text-transform:uppercase;letter-spacing:.1em;">Testo del reclamo</span>
        </div>""", unsafe_allow_html=True)
        testo = st.text_area("", height=260,
            placeholder="Incolla qui il testo completo del reclamo...",
            label_visibility="collapsed")

    with col_pdf:
        st.markdown("""
        <div style="background:#1e293b;border-radius:10px;padding:16px 20px;margin-bottom:8px;">
            <span style="font-family:Inter,sans-serif;font-size:11px;font-weight:700;
            color:#94a3b8;text-transform:uppercase;letter-spacing:.1em;">Carica PDF reclamo</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:white;border-radius:10px;height:260px;display:flex;flex-direction:column;
            align-items:center;justify-content:center;border:2px dashed #cbd5e1;gap:12px;">
            <span style="font-size:32px;">📎</span>
            <span style="font-family:Inter,sans-serif;font-size:13px;color:#94a3b8;text-align:center;">
            Trascina il PDF qui<br>
            <span style="font-size:11px;color:#cbd5e1;">Disponibile nella versione completa</span>
            </span>
        </div>""", unsafe_allow_html=True)

    # Pulsante a destra sotto i due box
    _, col_btn = st.columns([3, 1])
    with col_btn:
        st.markdown("""<style>
        div[data-testid="stMainBlockContainer"] button[kind="secondaryFormSubmit"],
        div[data-testid="stMainBlockContainer"] button[kind="secondary"] {
            background:#3B82F6 !important; color:white !important;
            border:none !important; font-weight:600 !important;
            font-family:Inter,sans-serif !important; font-size:13px !important;
        }
        div[data-testid="stMainBlockContainer"] button[kind="secondaryFormSubmit"]:hover,
        div[data-testid="stMainBlockContainer"] button[kind="secondary"]:hover {
            background:#2563eb !important;
        }
        </style>""", unsafe_allow_html=True)
        if st.button("Avvia l'analisi Resolva →", use_container_width=True, key="avvia"):
            if testo:
                try:
                    httpx.post(
                        "https://aldobaldaccini.app.n8n.cloud/webhook/1d0bc646-e0d3-486f-b4a3-c58e01dac7b7",
                        json={"testo_reclamo": testo},
                        timeout=10
                    )
                    get_db.clear()
                    st.success("✅ Reclamo inviato. La pratica apparirà tra i reclami attivi a breve.")
                    st.session_state.page = "Reclami attivi"
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore nell'invio: {e}")
            else:
                st.warning("Incolla il testo del reclamo prima di procedere.")

# ============================================================
# 5. DETTAGLIO PRATICA
# ============================================================
elif st.session_state.page == "Dettaglio pratica":
    rec = get_rec(st.session_state.get("id_selezionato",""), db)
    if not rec:
        st.error("Pratica non trovata.")
        st.markdown(
            '<a style="font-family:Inter,sans-serif;font-size:13px;color:#64748b;'
            'text-decoration:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;">',
            unsafe_allow_html=True)
        if st.button("← Reclami attivi"):
            st.session_state.page = "Reclami attivi"; st.rerun()
    else:
        _stato_rec = rec.get("Stato", "Attivo")
        _back_label = "← Reclami archiviati" if _stato_rec == "Archiviato" else "← Reclami attivi"
        _back_page  = "Reclami archiviati"   if _stato_rec == "Archiviato" else "Reclami attivi"
        if st.button(_back_label):
            st.session_state.page = _back_page; st.rerun()

        stato_cls   = "status-attivo" if rec["Stato"] == "Attivo" else "status-archiviato"
        header_cls  = "fascicolo-header" if rec["Stato"] == "Attivo" else "fascicolo-header fascicolo-header-arch"
        meta_color  = "#94a3b8" if rec["Stato"] == "Attivo" else "#f0b8c8"
        st.markdown(f"""<div class="{header_cls}">
            <div>
                <div class="fascicolo-id">Fascicolo {rec['ID']}</div>
                <div class="fascicolo-meta">
                    <span style="color:{meta_color};">{rec['Cliente']} &nbsp;·&nbsp; Ricevuto il {rec['Data']}
                    &nbsp;·&nbsp; Valore: <strong style="color:white;">€ {rec['Valore']:,}</strong>
                    &nbsp;·&nbsp; Operatore: {rec['Assegnato_a']}</span>
                </div>
            </div>
            <span class="status-pill {stato_cls}">{rec['Stato'].upper()}</span>
        </div>""", unsafe_allow_html=True)

        if rec.get("Stato","") == "Archiviato":
            operatore_val = rec.get("Operatore","") or rec.get("Assegnato_a","") or "—"
            data_arch_val = rec.get("Data_archiviazione","")
            url_nota  = rec.get("PDF_nota","") or "#"
            url_bozza = rec.get("DOCX_bozza","") or "#"
            bozza_mod_val = rec.get("Bozza_modificata","")
            has_bozza_mod = bool(bozza_mod_val and bozza_mod_val.strip())

            st.markdown(
                '<p style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
                'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;margin:24px 0 16px 0;">'
                'Documenti reclamo archiviato</p>',
                unsafe_allow_html=True)

            def doc_card(title, sub, url=None):
                if url and url != "#":
                    st.markdown(
                        f'<a href="{url}" target="_blank" style="text-decoration:none;color:inherit;">'
                        f'<div style="background:#1e293b;border-radius:10px;padding:18px 24px;'
                        f'display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
                        f'<div><div style="font-family:Playfair Display,serif;font-size:16px;'
                        f'color:#fff;font-weight:700;">{title}</div>'
                        f'<div style="font-family:Inter,sans-serif;font-size:12px;'
                        f'color:#94a3b8;margin-top:4px;">{sub}</div></div>'
                        f'<span style="font-size:22px;color:#3B82F6;font-weight:300;">&#x2192;</span>'
                        f'</div></a>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div style="background:#1e293b;border-radius:10px;padding:18px 24px;'
                        f'display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
                        f'<div><div style="font-family:Playfair Display,serif;font-size:16px;'
                        f'color:#fff;font-weight:700;">{title}</div>'
                        f'<div style="font-family:Inter,sans-serif;font-size:12px;'
                        f'color:#94a3b8;margin-top:4px;">{sub}</div></div>'
                        f'<span style="font-size:22px;color:#3B82F6;font-weight:300;">&#x2192;</span>'
                        f'</div>', unsafe_allow_html=True)

            doc_card("Reclamo integrale", "Documento PDF originale · disponibile nella versione completa")
            doc_card("Nota Tecnica", "Parere giuridico · Riferimenti normativi · Decisioni ABF", url_nota)
            doc_card("Bozza Resolva", "Bozza risposta generata da Resolva", url_bozza)
            resp_sub = "Bozza modificata · post-demo" if has_bozza_mod else "Coincide con la bozza Resolva · post-demo"
            doc_card("Risposta inviata", resp_sub)

            info_parts = []
            if data_arch_val:
                info_parts.append(f"Risposta inviata il {data_arch_val}")
            info_parts.append(f"Operatore: <strong>{operatore_val}</strong>")
            st.markdown(
                '<div style="text-align:right;margin-top:12px;margin-bottom:8px;">' +
                ' &nbsp;·&nbsp; '.join(
                    f'<span style="font-family:Inter,sans-serif;font-size:12px;color:#64748b;">{p}</span>'
                    for p in info_parts) +
                '</div>', unsafe_allow_html=True)

        else:
            col_main, col_side = st.columns([2, 1], gap="large")
            wf = rec.get("Stato_workflow", "in_elaborazione")

            with col_main:
                import re

                # ── SINTESI DEL RECLAMO ──
                sec("", "Il reclamo del cliente")
                sintesi_src = rec.get("Sintesi_reclamo") or rec.get("Sintesi_AI") or ""
                if wf == "elaborato" and sintesi_src:
                    sintesi_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', sintesi_src)
                    sintesi_html = re.sub(r'\*(.+?)\*', r'<strong>\1</strong>', sintesi_html)
                    st.markdown(f'<div class="ai-summary">{sintesi_html}</div>', unsafe_allow_html=True)
                else:
                    st.warning("⏳ Elaborazione in corso. La sintesi sarà disponibile a breve.")

                # Reclamo integrale — card scura statica (click post-demo)
                st.markdown(
                    '<div style="background:#1e293b;border-radius:10px;padding:18px 24px;'
                    'display:flex;align-items:center;justify-content:space-between;margin-top:12px;">'
                    '<div>'
                    '<div style="font-family:Playfair Display,serif;font-size:16px;'
                    'color:#fff;font-weight:700;">Reclamo integrale</div>'
                    '<div style="font-family:Inter,sans-serif;font-size:12px;'
                    'color:#94a3b8;margin-top:4px;">Documento PDF</div>'
                    '</div>'
                    '<span style="font-size:22px;color:#3B82F6;font-weight:300;">&#x2192;</span>'
                    '</div>',
                    unsafe_allow_html=True)

                # Divisore
                st.markdown(
                    '<div style="height:2px;background:linear-gradient(90deg,#3B82F6,#1e293b);' +
                    'border-radius:2px;margin:24px 0;"></div>',
                    unsafe_allow_html=True)

                # ── ANALISI RESOLVA ──
                sec("", "Resolva", "bordeaux")

                # Sintesi dell'analisi — primo elemento, stesso stile titolo sezione
                sintesi_analisi = rec.get("Sintesi_analisi") or ""
                if sintesi_analisi:
                    for _label in ["Reclamo:","Valutazione:","Norma principale applicabile:","Orientamento ABF prevalente:","Esito suggerito:","Motivazione:"]:
                        sintesi_analisi = sintesi_analisi.replace(_label, f"<strong>{_label}</strong>")
                    import re as _re2
                    for _term in ["Infondato","Fondato","Parzialmente fondato","Rigettare","Accogliere","Supplemento istruttorio","Strong Customer Authentication","colpa grave","onere della prova"]:
                        sintesi_analisi = _re2.sub(rf"(?<![>\w]){_re2.escape(_term)}(?![\w<])", f"<strong>{_term}</strong>", sintesi_analisi)
                    sintesi_analisi = sintesi_analisi.replace("\n", "<br>")
                if wf == "elaborato":
                    if sintesi_analisi:
                        analisi_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', sintesi_analisi)
                        analisi_html = re.sub(r'\*(.+?)\*', r'<strong>\1</strong>', analisi_html)
                        st.markdown(f'<div class="ai-summary">{analisi_html}</div>', unsafe_allow_html=True)
                    else:
                        esito_attuale = rec.get("Esito", "")
                        badge_color = {"Accolto":"#d1fae5","Rigettato":"#fce7f3",
                                       "In analisi":"#e2e8f0","Draft":"#e2e8f0"}.get(esito_attuale,"#e2e8f0")
                        badge_txt   = {"Accolto":"#065f46","Rigettato":"#9d174d",
                                       "In analisi":"#475569","Draft":"#475569"}.get(esito_attuale,"#475569")
                        st.markdown(
                            f'<div class="ai-summary">' +
                            (f'<span style="background:{badge_color};color:{badge_txt};' +
                             f'font-family:Inter,sans-serif;font-size:11px;font-weight:700;' +
                             f'padding:3px 10px;border-radius:20px;">{esito_attuale}</span>' if esito_attuale else "") +
                            + (f'<p style="font-family:Inter,sans-serif;font-size:13px;color:#475569;margin:8px 0 0 0;">'
                               f'{sintesi_an}</p>' if sintesi_an else
                               f'<p style="font-family:Inter,sans-serif;font-size:13px;color:#94a3b8;margin:8px 0 0 0;">'  
                               f'Elaborazione in corso...</p>') +
                            f'</div>',
                            unsafe_allow_html=True)

                    # Nota Tecnica + Bozza di Risposta
                    pdf_link  = rec.get("PDF_nota",   "#")
                    docx_link = rec.get("DOCX_bozza", "#")
                    st.markdown(
                        f'<div style="display:flex;flex-direction:column;gap:12px;margin-top:12px;">' +
                        f'<a href="{pdf_link}" target="_blank" style="display:flex;align-items:center;' +
                        f'justify-content:space-between;background:#1e293b;border-radius:10px;' +
                        f'padding:18px 24px;text-decoration:none;">' +
                        f'<div><div style="font-family:Playfair Display,serif;font-size:16px;' +
                        f'color:#fff;font-weight:700;">Nota Tecnica</div>' +
                        f'<div style="font-family:Inter,sans-serif;font-size:12px;' +
                        f'color:#94a3b8;margin-top:4px;">Parere giuridico · Riferimenti normativi · Decisioni ABF</div>' +
                        f'</div><span style="font-size:22px;color:#3B82F6;font-weight:300;">→</span></a>' +
                        f'<a href="{docx_link}" target="_blank" style="display:flex;align-items:center;' +
                        f'justify-content:space-between;background:#1e293b;border-radius:10px;' +
                        f'padding:18px 24px;text-decoration:none;">' +
                        f'<div><div style="font-family:Playfair Display,serif;font-size:16px;' +
                        f'color:#fff;font-weight:700;">Bozza di Risposta</div>' +
                        f'<div style="font-family:Inter,sans-serif;font-size:12px;' +
                        f'color:#94a3b8;margin-top:4px;">Documento editabile · Pronto per revisione e invio</div>' +
                        f'</div><span style="font-size:22px;color:#3B82F6;font-weight:300;">→</span></a>' +
                        f'</div>',
                        unsafe_allow_html=True)
                else:
                    st.info("I documenti saranno disponibili al termine dell'elaborazione.")
            with col_side:
                sec("", "Stato della pratica")
                steps = ([("✅","step-done","Reclamo ricevuto",rec['Data']),
                          ("✅","step-done","Analisi AI completata","oggi"),
                          ("✅","step-done","Nota tecnica generata","oggi"),
                          ("✅","step-done","Bozza risposta generata","oggi"),
                          ("⏳","step-pending","Valutazioni operatore","in attesa"),
                          ("🔒","step-wait","Invio al responsabile","—")]
                         if wf == "elaborato" else
                         [("✅","step-done","Reclamo ricevuto",rec['Data']),
                          ("⏳","step-pending","Analisi AI in corso","in corso..."),
                          ("🔒","step-wait","Nota tecnica","—"),
                          ("🔒","step-wait","Bozza risposta","—"),
                          ("🔒","step-wait","Valutazioni operatore","—"),
                          ("🔒","step-wait","Invio al responsabile","—")])
                st.markdown(
                    '<div class="sec-body">' +
                    "".join(f'<div class="workflow-step"><div class="step-icon {cls}">{icon}</div>'
                            f'<div><div class="step-text">{label}</div>'
                            f'<div class="step-date">{date}</div></div></div>'
                            for icon, cls, label, date in steps) +
                    '</div>', unsafe_allow_html=True)

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown(
                    f'<div style="background:#f1f5f9;border-radius:8px;padding:12px 16px;">'
                    f'<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;'
                    f'color:#94a3b8;text-transform:uppercase;letter-spacing:.1em;margin:0 0 4px 0;">'
                    f'Assegnato a</p>'
                    f'<p style="font-family:Inter,sans-serif;font-size:14px;font-weight:600;'
                    f'color:#1e293b;margin:0;">{rec.get("Assegnato_a", "—")}</p>'
                    f'</div>', unsafe_allow_html=True)

            # ══ VALUTAZIONI DELL'OPERATORE ══
            ruolo_corrente = st.session_state.get("ruolo", "Operatore")
            esito_corrente = rec.get("Esito", "")
            vista_resp     = (ruolo_corrente == "Responsabile" and
                              esito_corrente in ["Al responsabile", "In istruttoria"])

            st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div style="height:3px;background:linear-gradient(90deg,#3B82F6,#1e293b);'
                'border-radius:2px;margin-bottom:20px;"></div>',
                unsafe_allow_html=True)
            st.markdown(
                '<p style="font-family:Playfair Display,serif;font-size:15px;font-weight:700;'
                'text-transform:uppercase;letter-spacing:.18em;color:#1e293b;margin-bottom:20px;">'
                "Valutazioni dell\'Operatore</p>",
                unsafe_allow_html=True)

            col_val, col_act = st.columns([2, 1], gap="large")

            proposta_corrente = rec.get("Proposta_decisione", "")
            proposte          = ["Accogliere", "Rigettare", "Supplemento istruttorio"]
            proposta_idx      = proposte.index(proposta_corrente) if proposta_corrente in proposte else 2
            note_correnti     = rec.get("Note", "")
            bozza_corrente    = rec.get("Bozza_modificata", "")

            with col_val:
                st.markdown(
                    '<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;'
                    'color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin:0 0 10px 0;">'
                    'Proposta di decisione</p>', unsafe_allow_html=True)
                if vista_resp:
                    _bc = {"Accogliere":"#d1fae5","Rigettare":"#fee2e2",
                           "Supplemento istruttorio":"#fef3c7"}.get(proposta_corrente,"#e2e8f0")
                    _tc = {"Accogliere":"#065f46","Rigettare":"#b91c1c",
                           "Supplemento istruttorio":"#92400e"}.get(proposta_corrente,"#475569")
                    st.markdown(
                        f'<span style="background:{_bc};color:{_tc};font-family:Inter,sans-serif;'
                        f'font-size:13px;font-weight:700;padding:6px 16px;border-radius:20px;">'
                        f'{proposta_corrente or "Non compilata"}</span>',
                        unsafe_allow_html=True)
                    proposta_sel = proposta_corrente
                else:
                    proposta_sel = st.radio("Proposta", proposte, index=proposta_idx,
                        key=f"proposta_{rec['ID']}", label_visibility="collapsed", horizontal=True)

                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                st.markdown(
                    '<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;'
                    'color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin:0 0 8px 0;">'
                    'Note operative</p>', unsafe_allow_html=True)
                if vista_resp:
                    st.markdown(
                        f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;'
                        f'padding:12px 16px;min-height:60px;">'
                        f'<p style="font-family:Inter,sans-serif;font-size:13px;color:#475569;margin:0;">'
                        f'{note_correnti or "<em>Nessuna nota</em>"}</p></div>',
                        unsafe_allow_html=True)
                    note_val = note_correnti
                else:
                    note_val = st.text_area("Note", value=note_correnti, height=100,
                        key=f"note_{rec['ID']}", label_visibility="collapsed",
                        placeholder="Note interne, supplemento istruttorio richiesto, osservazioni...")

                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                st.markdown(
                    '<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;'
                    'color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin:0 0 4px 0;">'
                    'Bozza risposta modificata &nbsp;'
                    '<span style="font-weight:400;color:#94a3b8;">'
                    '(caricare solo se modificata rispetto alla bozza Resolva)</span></p>',
                    unsafe_allow_html=True)
                if vista_resp:
                    bozza_mod = st.text_area("Bozza risposta", value=bozza_corrente,
                        height=120, key=f"bozza_resp_{rec['ID']}", label_visibility="collapsed",
                        placeholder="Modifica qui il testo della bozza risposta prima di inviare...")
                else:
                    bozza_mod = bozza_corrente
                    uploaded = st.file_uploader("Carica bozza modificata", type=["docx","pdf"],
                        key=f"upload_{rec['ID']}", label_visibility="collapsed")
                    if uploaded is not None:
                        bozza_mod = f"[file caricato: {uploaded.name}]"
                        st.markdown(
                            f'<div style="background:#e2e8f0;border-radius:8px;padding:10px 14px;margin-top:6px;">'
                            f'<p style="font-family:Inter,sans-serif;font-size:12px;color:#1e293b;margin:0;">'
                            f'📎 <strong>{uploaded.name}</strong> &nbsp;·&nbsp; '
                            f'<span style="color:#64748b;">{round(uploaded.size/1024,1)} KB</span></p>'
                            f'</div>',
                            unsafe_allow_html=True)

            with col_act:
                st.markdown(
                    '<p style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;'
                    'color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin:0 0 16px 0;">'
                    'Azioni</p>', unsafe_allow_html=True)

                valore_pratica = float(rec.get("Valore", 0) or 0)
                soglia = 1000.0

                if not vista_resp and st.button("Salva valutazioni", key=f"salva_val_{rec['ID']}",
                             use_container_width=True):
                    sb_update(rec["ID"], {
                        "note": note_val,
                        "proposta_decisione": proposta_sel,
                        "bozza_modificata": bozza_mod
                    })
                    get_db.clear()
                    st.success("Valutazioni salvate.")

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                # Invia al responsabile — solo per operatore
                if not vista_resp and st.button("Invia al responsabile", key=f"resp_{rec['ID']}",
                             use_container_width=True):
                    esito_resp = "In istruttoria" if proposta_sel == "Supplemento istruttorio" else "Al responsabile"
                    sb_update(rec["ID"], {
                        "stato_workflow": "elaborato",
                        "esito": esito_resp,
                        "note": note_val,
                        "proposta_decisione": proposta_sel,
                        "bozza_modificata": bozza_mod
                    })
                    get_db.clear()
                    st.success("✅ Pratica inviata al responsabile.")
                    st.rerun()

                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

                # Invia risposta
                ruolo_corrente = st.session_state.get("ruolo", "Operatore")
                can_send = (ruolo_corrente == "Responsabile") or (valore_pratica < soglia)
                if can_send:
                    if st.button("Invia risposta", key=f"invia_{rec['ID']}",
                                 use_container_width=True, type="primary"):
                        esito_out = proposta_sel if proposta_sel in ["Accogliere","Rigettare"] else "Draft"
                        if esito_out == "Accogliere": esito_out = "Accolto"
                        if esito_out == "Rigettare":  esito_out = "Rigettato"
                        from datetime import datetime as _dt
                        sb_update(rec["ID"], {
                            "stato": "Archiviato",
                            "esito": esito_out,
                            "note": note_val,
                            "proposta_decisione": proposta_sel,
                            "bozza_modificata": bozza_mod,
                            "data_archiviazione": _dt.now().strftime("%d/%m/%Y")
                        })
                        get_db.clear()
                        st.success("Risposta inviata. Reclamo archiviato.")
                        st.rerun()
                else:
                    st.markdown(
                        '<div style="background:#e2e8f0;border-radius:8px;padding:10px 14px;'
                        'margin-top:2px;">'
                        '<p style="font-family:Inter,sans-serif;font-size:11px;'
                        'color:#475569;margin:0;">'
                        'Invio risposta disattivato · Valore superiore a € 1.000</p>'
                        '</div>',
                        unsafe_allow_html=True)
