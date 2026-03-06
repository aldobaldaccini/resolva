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
        "PDF_reclamo":    row.get("pdf_reclamo") or "",
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
[data-testid="stSidebar"] { background-color: #111827 !important; }
.brand-title { font-family:'Playfair Display',serif; color:#fff; font-size:32px; margin-bottom:0; padding-left:5px; }
.brand-subtitle { font-family:'Inter',sans-serif; color:#94A3B8; font-size:13px; text-transform:uppercase;
    letter-spacing:2px; margin-top:-5px; margin-bottom:20px; padding-left:5px; }
[data-testid="stSidebar"] .stButton > button {
    background:transparent !important; color:#94A3B8 !important; border:none !important;
    text-align:left !important; font-size:16px !important; font-weight:500 !important;
    padding:8px 10px !important; width:100% !important; box-shadow:none !important; }
[data-testid="stSidebar"] .stButton > button:hover { color:#fff !important; background:#1F2937 !important; }
.header-container { display:flex; align-items:center; margin-bottom:24px; }
.main-title { font-family:'Playfair Display',serif; font-size:42px; color:#111827; margin-right:25px; }
.counter-badge { background:#3B82F6; color:white; border-radius:50%; width:65px; height:65px;
    display:flex; align-items:center; justify-content:center;
    font-family:'Inter',sans-serif; font-size:28px; font-weight:700; box-shadow:0 4px 10px rgba(0,0,0,.15); }
div[data-testid="stSidebar"] .stTextInput input {
    background:#1F2937 !important; color:white !important; border:1px solid #374151 !important; border-radius:4px; }
.sidebar-divider { border-bottom:1px solid #374151; margin:15px 0; }

.pro-table { width:100%; border-collapse:collapse; font-family:'Inter',sans-serif;
    box-shadow:0 2px 12px rgba(0,0,0,.10); border-radius:8px; overflow:hidden; margin-bottom:8px; }
.pro-table thead tr th { background:#1e293b; color:#fff; padding:13px 16px; font-size:11px;
    text-transform:uppercase; letter-spacing:.10em; font-weight:700; text-align:left;
    border-bottom:2px solid #3B82F6; white-space:nowrap; }
.pro-table tbody tr td { padding:13px 16px; font-size:14px; color:#1e293b;
    border-bottom:1px solid #e2e8f0; background:#fff; vertical-align:middle; }
.pro-table tbody tr:last-child td { border-bottom:none; }
.pro-table tbody tr:nth-child(even) td { background:#f8fafc; }
.pro-table tbody tr:hover td { background:#eff6ff; transition:background .12s; }
.col-id { font-weight:700; color:#0f172a; white-space:nowrap; }
.col-val { white-space:nowrap; font-variant-numeric:tabular-nums; }
.badge { display:inline-block; padding:4px 11px; border-radius:999px; font-size:12px; font-weight:600; white-space:nowrap; }
.badge-accolto   { background:#dcfce7; color:#15803d; }
.badge-rigettato { background:#fee2e2; color:#b91c1c; }
.badge-analisi   { background:#dbeafe; color:#1d4ed8; }
.badge-draft     { background:#fef9c3; color:#92400e; }

.fascicolo-header { background:#1e293b; border-radius:10px; padding:24px 32px; margin-bottom:20px;
    display:flex; align-items:center; justify-content:space-between; }
.fascicolo-id { font-family:'Playfair Display',serif; color:#fff; font-size:28px; margin:0; }
.fascicolo-meta { font-family:'Inter',sans-serif; color:#94A3B8; font-size:13px; margin-top:6px; }
.status-pill { display:inline-block; padding:6px 18px; border-radius:999px;
    font-family:'Inter',sans-serif; font-size:13px; font-weight:700; }
.status-attivo { background:#dbeafe; color:#1d4ed8; }
.status-archiviato { background:#e2e8f0; color:#475569; }

.sec-header { display:flex; align-items:center; gap:10px; background:white;
    border-left:4px solid #3B82F6; border-radius:0 8px 0 0; padding:12px 18px;
    margin-top:20px; margin-bottom:0; box-shadow:0 1px 4px rgba(0,0,0,.06); }
.sec-header.green  { border-color:#10b981; }
.sec-header.slate  { border-color:#64748b; }
.sec-header.amber  { border-color:#f59e0b; }
.sec-header.red    { border-color:#ef4444; }
.sec-icon { font-size:18px; line-height:1; }
.sec-title { font-family:'Inter',sans-serif; font-size:13px; font-weight:700;
    text-transform:uppercase; letter-spacing:.10em; color:#1e293b; }
.sec-body { background:white; border-radius:0 0 8px 8px; padding:18px 20px 20px 20px;
    margin-bottom:6px; box-shadow:0 2px 8px rgba(0,0,0,.06); }

.ai-summary { font-family:'Inter',sans-serif; font-size:14px; color:#1e293b; line-height:1.75;
    background:#f0f7ff; border-left:3px solid #3B82F6; padding:16px 20px;
    border-radius:0 6px 6px 0; margin-bottom:14px; }
.ai-label { font-family:'Inter',sans-serif; font-size:11px; font-weight:700;
    color:#3B82F6; text-transform:uppercase; letter-spacing:.1em; margin-bottom:8px; }
.workflow-step { display:flex; align-items:flex-start; gap:14px; padding:10px 0; border-bottom:1px solid #f1f5f9; }
.workflow-step:last-child { border-bottom:none; }
.step-icon { width:30px; height:30px; border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:13px; flex-shrink:0; }
.step-done { background:#dcfce7; } .step-pending { background:#fef9c3; } .step-wait { background:#f1f5f9; }
.step-text { font-family:'Inter',sans-serif; font-size:13px; color:#374151; font-weight:500; }
.step-date { font-size:11px; color:#94a3b8; margin-top:2px; }
.dl-link { display:inline-flex; align-items:center; gap:8px; padding:9px 18px; border-radius:6px;
    font-family:'Inter',sans-serif; font-size:13px; font-weight:700; text-decoration:none; margin-top:6px; }
.dl-pdf  { background:#fee2e2; color:#b91c1c; }
.dl-docx { background:#dbeafe; color:#1d4ed8; }
.dl-orig { background:#f1f5f9; color:#334155; border:1px solid #cbd5e1; }
</style>
""", unsafe_allow_html=True)

# ── AUTO REFRESH ogni 20 secondi ──
st_autorefresh(interval=20000, key="autorefresh")

# ── STATO ──
if 'page' not in st.session_state:
    st.session_state.page = "Reclami attivi"

OPERATORI = ["M. Rossi", "E. Verdi", "F. Bruno", "C. Marino"]

def badge(esito):
    cls = {"In analisi":"badge-analisi","Draft":"badge-draft",
           "Rigettato":"badge-rigettato","Accolto":"badge-accolto"}.get(esito,"")
    return f'<span class="badge {cls}">{esito}</span>'

def get_rec(id_, db):
    for r in db:
        if r["ID"] == id_: return r
    return None

def sec(icon, title, color=""):
    st.markdown(f'<div class="sec-header {color}"><span class="sec-icon">{icon}</span>'
                f'<span class="sec-title">{title}</span></div>', unsafe_allow_html=True)

def build_table(data, cols, headers):
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

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<p class="brand-title"><span style="color:#3B82F6;letter-spacing:4px">R E</span><span style="letter-spacing:4px"> &nbsp;S O L V A</span></p><p class="brand-subtitle">Gestione reclami</p>',
                unsafe_allow_html=True)
    if st.button("Sincronizzazione pec"): st.toast("Disponibile nella versione completa")
    if st.button("Carica reclamo"): st.session_state.page = "Carica reclamo"; st.rerun()
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    if st.button("Reclami attivi"): st.session_state.page = "Reclami attivi"; st.rerun()
    if st.button("Reclami archiviati"): st.session_state.page = "Reclami archiviati"; st.rerun()
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    if st.button("Statistiche"): st.session_state.page = "Statistiche"; st.rerun()
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
if st.session_state.page == "Reclami attivi":
    data_view = df[df['Stato'] == "Attivo"].reset_index(drop=True)
    st.markdown(f'<div class="header-container"><span class="main-title">Reclami attivi</span>'
                f'<div class="counter-badge">{len(data_view)}</div></div>', unsafe_allow_html=True)
    if data_view.empty:
        st.info("Nessun reclamo attivo.")
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
            if st.button("Apri pratica →", use_container_width=True):
                st.session_state.id_selezionato = ids[labels.index(scelta)]
                st.session_state.page = "Dettaglio pratica"
                st.rerun()

# ============================================================
# 2. RECLAMI ARCHIVIATI
# ============================================================
elif st.session_state.page == "Reclami archiviati":
    data_view = df[df['Stato'] == "Archiviato"].reset_index(drop=True)
    st.markdown(f'<div class="header-container"><span class="main-title">Reclami archiviati</span>'
                f'<div class="counter-badge" style="background:#64748b;">{len(data_view)}</div></div>',
                unsafe_allow_html=True)
    if data_view.empty:
        st.info("Nessun reclamo archiviato.")
    else:
        st.markdown(build_table(data_view,
            ["ID","Data","Cliente","Valore","Operatore","Esito"],
            ["ID Pratica","Data","Cliente","Valore (€)","Operatore","Esito"]), unsafe_allow_html=True)

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
    st.info("Incolla il testo del reclamo. Il sistema AI estrarrà automaticamente i dati e genererà nota tecnica e bozza di risposta.")
    with st.form("manual"):
        testo = st.text_area("Testo del reclamo *", height=280,
                             placeholder="Incolla qui il testo completo del reclamo...")
        submitted = st.form_submit_button("🚀 Invia al flusso AI")
    if submitted and testo:
        try:
            risposta = httpx.post(
                "https://aldobaldaccini.app.n8n.cloud/webhook/avvia-reclamo",
                json={"testo_reclamo": testo},
                timeout=10
            )
            get_db.clear()
            st.success("✅ Reclamo inviato. La pratica apparirà tra i reclami attivi a breve.")
            st.session_state.page = "Reclami attivi"
            st.rerun()
        except Exception as e:
            st.error(f"Errore nell'invio: {e}")

# ============================================================
# 5. DETTAGLIO PRATICA
# ============================================================
elif st.session_state.page == "Dettaglio pratica":
    rec = get_rec(st.session_state.get("id_selezionato",""), db)
    if not rec:
        st.error("Pratica non trovata.")
        if st.button("← Torna alla lista"):
            st.session_state.page = "Reclami attivi"; st.rerun()
    else:
        if st.button("← Torna alla lista"):
            st.session_state.page = "Reclami attivi"; st.rerun()

        stato_cls = "status-attivo" if rec["Stato"] == "Attivo" else "status-archiviato"
        st.markdown(f"""<div class="fascicolo-header">
            <div>
                <div class="fascicolo-id">Fascicolo {rec['ID']}</div>
                <div class="fascicolo-meta">
                    {rec['Cliente']} &nbsp;·&nbsp; Ricevuto il {rec['Data']}
                    &nbsp;·&nbsp; Valore: <strong style="color:white;">€ {rec['Valore']:,}</strong>
                    &nbsp;·&nbsp; Operatore: {rec['Assegnato_a']}
                </div>
            </div>
            <span class="status-pill {stato_cls}">{rec['Stato'].upper()}</span>
        </div>""", unsafe_allow_html=True)

        col_main, col_side = st.columns([2, 1], gap="large")
        wf = rec.get("Stato_workflow", "in_elaborazione")

        with col_main:
            sec("📄", "Il reclamo")
            if wf == "elaborato" and rec.get("Sintesi_AI"):
                st.markdown(f'<div class="ai-label">🤖 Sintesi Banksolving AI</div>'
                            f'<div class="ai-summary">{rec["Sintesi_AI"]}</div>', unsafe_allow_html=True)
            else:
                st.warning("⏳ Elaborazione AI in corso. La sintesi sarà disponibile a breve.")
            if rec.get("PDF_reclamo"):
                st.markdown('<br><a href="#" class="dl-link dl-orig">📎 &nbsp; Apri PDF reclamo originale</a>',
                            unsafe_allow_html=True)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            sec("🧠", "Documenti generati da Banksolving", "green")
            if wf == "elaborato":
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown("**Nota tecnica**")
                    st.caption("Analisi giuridica con riferimenti normativi e decisioni ABF.")
                    if rec.get("PDF_nota"):
                        st.link_button("⬇ Apri nota tecnica (PDF)", rec["PDF_nota"], use_container_width=True)
                with d2:
                    st.markdown("**Bozza di risposta**")
                    st.caption("Documento editabile pronto per revisione e invio.")
                    if rec.get("DOCX_bozza"):
                        st.link_button("⬇ Apri bozza risposta (Docs)", rec["DOCX_bozza"], use_container_width=True)
            else:
                st.info("I documenti saranno disponibili al termine dell'elaborazione AI.")
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            sec("📝", "Note operative", "amber")
            note_val = st.text_area("Note", value=rec.get("Note",""), height=110,
                key=f"note_{rec['ID']}", label_visibility="collapsed",
                placeholder="Note interne non visibili al cliente...")
            if st.button("💾 Salva note", key=f"save_note_{rec['ID']}"):
                sb_update(rec["ID"], {"note": note_val})
                get_db.clear()
                st.success("Note salvate.")

        with col_side:
            sec("⚙️", "Stato del flusso")
            steps = ([("✅","step-done","Reclamo ricevuto",rec['Data']),
                      ("✅","step-done","Analisi AI completata","oggi"),
                      ("✅","step-done","Nota tecnica generata","oggi"),
                      ("✅","step-done","Bozza risposta generata","oggi"),
                      ("⏳","step-pending","Revisione operatore","in attesa"),
                      ("🔒","step-wait","Invio al decisore finale","—")]
                     if wf == "elaborato" else
                     [("✅","step-done","Reclamo ricevuto",rec['Data']),
                      ("⏳","step-pending","Analisi AI in corso","in corso..."),
                      ("🔒","step-wait","Generazione nota tecnica","—"),
                      ("🔒","step-wait","Generazione bozza risposta","—"),
                      ("🔒","step-wait","Revisione operatore","—"),
                      ("🔒","step-wait","Invio al decisore finale","—")])
            st.markdown(
                '<div class="sec-body">' +
                "".join(f'<div class="workflow-step"><div class="step-icon {cls}">{icon}</div>'
                        f'<div><div class="step-text">{label}</div>'
                        f'<div class="step-date">{date}</div></div></div>'
                        for icon, cls, label, date in steps) +
                '</div>', unsafe_allow_html=True)

            sec("👤", "Assegnazione", "slate")
            idx_op = OPERATORI.index(rec["Assegnato_a"]) if rec["Assegnato_a"] in OPERATORI else 0
            nuovo_op = st.selectbox("Operatore", OPERATORI, index=idx_op, key=f"op_{rec['ID']}")
            if st.button("Aggiorna assegnazione", key=f"save_op_{rec['ID']}"):
                sb_update(rec["ID"], {"assegnato_a": nuovo_op, "operatore": nuovo_op})
                get_db.clear()
                st.success(f"Assegnato a {nuovo_op}.")
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            if wf == "elaborato":
                sec("⚖️", "Decisione finale", "red")
                esiti = ["In analisi","Draft","Accolto","Rigettato"]
                esito_corrente = rec.get("Esito","In analisi")
                esito_idx = esiti.index(esito_corrente) if esito_corrente in esiti else 0
                esito_sel = st.radio("Esito", esiti,
                    index=esito_idx, key=f"esito_{rec['ID']}")
                if st.button("📨 Invia al decisore finale", key=f"send_{rec['ID']}", type="primary"):
                    nuovo_stato = "Archiviato" if esito_sel in ["Accolto","Rigettato"] else "Attivo"
                    sb_update(rec["ID"], {"esito": esito_sel, "stato": nuovo_stato})
                    get_db.clear()
                    st.success("Pratica inviata al decisore.")
                    st.rerun()
