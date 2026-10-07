"""
Thailand Data Center Site Suitability Dashboard — Version 2
V1: Gate Criteria + 6D Assessment (Readiness Score)
V2: + Opportunity Score → Balance Score + Balance Quadrant
ข้อมูล: มิ.ย. 2569 (v3 — After Defense)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import json, os, copy

# ────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="DC Site Selection V2 | Thailand",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────────
# CSS
# ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700;800&display=swap');
html { font-size: 21px; }
*, body, .stApp, [class*="st-"], [data-testid] {
    font-family: 'DB Heavent', 'Sarabun', 'Noto Sans Thai', sans-serif !important;
}
[data-testid="stIconMaterial"], [data-testid*="Icon"], span[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 0rem; padding-bottom: 0.5rem;}

/* ── Top Nav ── */
.topnav {
    background:#0A1628; color:white; padding:14px 28px;
    display:flex; align-items:center; justify-content:space-between;
    border-bottom:3px solid #6C47FF; margin-bottom:6px;
}
.topnav-title {font-size:1.4rem; font-weight:700; color:#fff; letter-spacing:.3px}
.topnav-sub   {font-size:1.02rem; color:#C4B5FD; margin-top:2px}
.version-badge {
    background:#6C47FF; color:white; padding:4px 14px; border-radius:20px;
    font-size:1rem; font-weight:700; letter-spacing:.5px;
}

/* ── Section header ── */
.section-header {
    font-size:1.08rem; font-weight:700; color:#1A9B6C;
    text-transform:uppercase; letter-spacing:.06em;
    border-left:4px solid #1A9B6C; padding-left:10px;
    margin-bottom:10px; margin-top:16px;
}
.section-header-v2 {
    font-size:1.08rem; font-weight:700; color:#6C47FF;
    text-transform:uppercase; letter-spacing:.06em;
    border-left:4px solid #6C47FF; padding-left:10px;
    margin-bottom:10px; margin-top:16px;
}
.panel-title {
    font-size:1.25rem; font-weight:800; color:#0A1628;
    display:flex; align-items:center; gap:8px; margin-bottom:6px;
}

/* ── Filter panel ── */
.filter-panel {
    background:#F5F8FC; border-radius:12px;
    padding:18px 20px; border:1px solid #D0DFF0;
    font-size:1.05rem;
}

/* ── Cards ── */
.result-card {
    background:white; border-radius:16px; padding:20px 22px;
    border:2px solid #E4ECF5; height:100%;
}
.result-card-gate    { border-top:5px solid #1A9B6C; }
.result-card-6d      { border-top:5px solid #2E75B6; }
.result-card-oppty   { border-top:5px solid #6C47FF; }
.result-card-balance { border-top:5px solid #E07B00; }

/* ── Score boxes ── */
.score-box {
    background:linear-gradient(135deg,#0D2137 0%,#1A3A5C 100%);
    border-radius:14px; padding:22px 26px; margin-bottom:14px;
    border:1px solid #2E75B6;
}
.score-box-v2 {
    background:linear-gradient(135deg,#1A0A37 0%,#3A1A6C 100%);
    border-radius:14px; padding:22px 26px; margin-bottom:14px;
    border:1px solid #6C47FF;
}
.score-box-balance {
    background:linear-gradient(135deg,#1A0D00 0%,#3D2100 100%);
    border-radius:14px; padding:22px 26px; margin-bottom:14px;
    border:1px solid #E07B00;
}
.score-big  {font-size:4rem; font-weight:800; color:#fff; line-height:1}
.score-label{font-size:1.08rem; color:#9DC3E6; margin-bottom:4px; font-weight:600}
.score-label-v2{font-size:1.08rem; color:#C4B5FD; margin-bottom:4px; font-weight:600}
.score-label-bal{font-size:1.08rem; color:#FFC080; margin-bottom:4px; font-weight:600}

/* ── Gate badges ── */
.gate-pass  {display:inline-block;background:#1A9B6C;color:white;
             padding:7px 20px;border-radius:22px;font-size:1.08rem;font-weight:700;}
.gate-no    {display:inline-block;background:#E04040;color:white;
             padding:7px 20px;border-radius:22px;font-size:1.08rem;font-weight:700;}

/* ── Chips ── */
.chip-green  {background:#E6F7EF;color:#1A9B6C;border:1px solid #B2DFD1;
              padding:6px 16px;border-radius:22px;font-size:1.05rem;margin:3px;display:inline-block}
.chip-purple {background:#F3EEFF;color:#6C47FF;border:1px solid #C4B5FD;
              padding:6px 16px;border-radius:22px;font-size:1.05rem;margin:3px;display:inline-block}
.chip-orange {background:#FFF8E6;color:#D0700A;border:1px solid #FACEAA;
              padding:6px 16px;border-radius:22px;font-size:1.05rem;margin:3px;display:inline-block}
.chip-red    {background:#FFF0F0;color:#C0392B;border:1px solid #F5B5B5;
              padding:6px 16px;border-radius:22px;font-size:1.05rem;margin:3px;display:inline-block}

/* ── Welcome box ── */
.welcome-box {
    background:linear-gradient(135deg,#EBF4FF 0%,#F0EBFF 100%);
    border-radius:16px; padding:34px 26px; text-align:center;
    border:2px dashed #9DC3E6; margin-top:10px;
    font-size:1.08rem;
}

/* ── Bar labels ── */
.dim-label {font-size:1.12rem; font-weight:600; color:#222}
.dim-value {font-size:1.12rem; font-weight:700}
.dim-sub   {font-size:.94rem; color:#999; text-align:right}

/* ── Gate checklist row ── */
.gate-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:12px 16px; margin-bottom:8px; border-radius:10px;
    background:#F5F8FC; border:1px solid #E4ECF5;
}
.gate-row-pass {border-left:5px solid #1A9B6C;}
.gate-row-fail {border-left:5px solid #E04040;}
.gate-row-na   {border-left:5px solid #BBBBBB;}
.gate-crit-label {font-size:1.08rem; font-weight:600; color:#222}
.gate-crit-value {font-size:.98rem; color:#888}

/* ── Quadrant info box ── */
.quad-info {
    border-radius:10px; padding:12px 16px; margin-bottom:8px;
    border:1px solid #E4ECF5; font-size:1.02rem;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# CONSTANTS
# ────────────────────────────────────────────────
BASE     = os.path.dirname(__file__)
GATE_CSV = os.path.join(BASE, "data", "gate_criteria.csv")
SIXD_CSV = os.path.join(BASE, "data", "six_d_assessment.csv")
GEO_FILE = os.path.join(BASE, "thailand.json")

DIM_KEYS   = ["energy_score","water_score","talent_score","business_score","infrastructure_score","risk_score"]
DIM_MAX    = {"energy_score":35,"water_score":20,"talent_score":20,"business_score":7.5,"infrastructure_score":7.5,"risk_score":10}
DIM_LABELS = {"energy_score":"⚡ Energy","water_score":"💧 Water","talent_score":"🎓 Talent",
              "business_score":"🏢 Business","infrastructure_score":"🏭 Infrastructure","risk_score":"🛡️ Risk"}
DIM_COLORS = {"energy_score":"#1A9B6C","water_score":"#2E75B6","talent_score":"#7B4FBF",
              "business_score":"#E07B00","infrastructure_score":"#1F7A8C","risk_score":"#C0392B"}
GRADE_COLOR= {"A":"#1A9B6C","B":"#2E75B6","C":"#FFC000","D":"#E04040","F":"#9B2226"}

GATE_LABELS = {
    "g1_energy":     "⚡ G1 — กำลังผลิตไฟฟ้า ≥ 100 MW",
    "g2_water":      "💧 G2 — แหล่งน้ำผิวดิน ≥ 1 แหล่ง",
    "g3_population": "👥 G3 — ประชากร ≥ 500,000 คน",
    "g4_education":  "🎓 G4 — สถาบันการศึกษา ≥ 3 แห่ง",
    "g5_flood":      "🌊 G5 — โซนน้ำท่วม ต่ำ–ปานกลาง",
    "g6_industrial": "🏭 G6 — มีนิคมอุตสาหกรรม/โครงการ BOI",
}
GATE_RAW_LABELS = {
    "g1_energy":     ("raw_mw", "MW", 1),
    "g2_water":      ("raw_water_sources", "แหล่ง", 0),
    "g3_population": ("raw_population", "คน", 0),
    "g4_education":  ("raw_education", "แห่ง", 0),
    "g5_flood":      ("raw_flood_zone", "", None),
    "g6_industrial": ("raw_industrial", "นิคม", 0),
}

# V2 Opportunity Score weights (must sum to 100)
OPP_WEIGHTS = {
    "opp_energy":   30,   # Renewable energy potential (installed_mw)
    "opp_water":    25,   # Water resource availability (storage_mcm)
    "opp_talent":   20,   # Workforce development pipeline (univ + voc)
    "opp_business": 15,   # Economic activity & investment (BOI + IEAT)
    "opp_policy":   10,   # Strategic policy bonus (EEC + Strategic)
}
OPP_LABELS = {
    "opp_energy":   "⚡ Energy Opportunity",
    "opp_water":    "💧 Water Opportunity",
    "opp_talent":   "🎓 Talent Pipeline",
    "opp_business": "🏢 Business & Investment",
    "opp_policy":   "🏛️ Policy & Strategic",
}
OPP_COLORS = {
    "opp_energy":   "#7B2FBE",
    "opp_water":    "#4F46E5",
    "opp_talent":   "#9333EA",
    "opp_business": "#7C3AED",
    "opp_policy":   "#6D28D9",
}

BALANCE_WEIGHT_READINESS   = 0.6
BALANCE_WEIGHT_OPPORTUNITY = 0.4

# Quadrant definitions: (x>=50, y>=50) etc.
QUADRANT_LABELS = {
    (True,  True):  ("PRIME OPPORTUNITY",         "High upside · Low burden",           "#E6FFF5", "#1A9B6C"),
    (False, True):  ("HIGH POTENTIAL, HIGH BURDEN","High upside · High burden",          "#FFF3CD", "#D0700A"),
    (True,  False): ("LIMITED UPSIDE",             "Low upside · Low burden",            "#EEF2FF", "#4F46E5"),
    (False, False): ("BURDEN TRAP",                "Low upside · High burden",           "#FFF0F0", "#E04040"),
}

GEO_NAME_FIX = {
    "Bangkok":      "Bangkok Metropolis",
    "Chonburi":     "Chon Buri",
    "Chainat":      "Chai Nat",
    "Lopburi":      "Lop Buri",
    "Phang Nga":    "Phangnga",
    "Prachinburi":  "Prachin Buri",
}
def to_geo_name(en_name):
    return GEO_NAME_FIX.get(en_name, en_name)

def tier_color(tier_str):
    t = str(tier_str)
    if t.startswith("Tier 1"): return "#1A9B6C"
    if t.startswith("Tier 2"): return "#5BB8A4"
    if t.startswith("Tier 3"): return "#F0C040"
    if t.startswith("Tier 4"): return "#BBBBBB"
    if t.startswith("Tier 5"): return "#8B2E2E"
    return "#888888"

def tier_short(tier_str):
    return str(tier_str).split("(")[0].strip()


# ────────────────────────────────────────────────
# DATA LOADING
# ────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_gate():
    return pd.read_csv(GATE_CSV, encoding="utf-8-sig")

@st.cache_data(ttl=300)
def load_6d():
    df = pd.read_csv(SIXD_CSV, encoding="utf-8-sig")
    df["EEC"]       = df["EEC"].astype(bool)
    df["Strategic"] = df["Strategic"].astype(bool)
    df["passed_gate"] = df["passed_gate"].astype(bool)
    for k, mx in DIM_MAX.items():
        if f"{k}_pct" not in df.columns:
            df[f"{k}_pct"] = (df[k] / mx * 100).round(1)
    return df

@st.cache_data
def load_geo():
    with open(GEO_FILE) as f:
        return json.load(f)


# ────────────────────────────────────────────────
# V2: COMPUTE OPPORTUNITY SCORE (all 77 provinces)
# ────────────────────────────────────────────────
def percentile_norm(series):
    """Normalize using percentile rank (0–100). Robust to outliers."""
    return (series.rank(pct=True, method="average") * 100).round(2)

@st.cache_data(ttl=300)
def compute_opportunity(df_6d: pd.DataFrame) -> pd.DataFrame:
    df = df_6d.copy()

    # Raw components
    talent_raw   = df["univ_count"] + df["voc_count"]
    business_raw = df["boi_projects"] + df["ieat_count"]
    policy_raw   = (df["EEC"].astype(float) * 70 + df["Strategic"].astype(float) * 30)

    df["opp_energy_raw"]   = df["installed_mw"]
    df["opp_water_raw"]    = df["storage_mcm"]
    df["opp_talent_raw"]   = talent_raw
    df["opp_business_raw"] = business_raw
    df["opp_policy_raw"]   = policy_raw

    # Normalize each component to 0–100 via percentile rank (robust to outliers)
    df["opp_energy_pct"]   = percentile_norm(df["opp_energy_raw"])
    df["opp_water_pct"]    = percentile_norm(df["opp_water_raw"])
    df["opp_talent_pct"]   = percentile_norm(df["opp_talent_raw"])
    df["opp_business_pct"] = percentile_norm(df["opp_business_raw"])
    df["opp_policy_pct"]   = percentile_norm(df["opp_policy_raw"])

    # Weighted opportunity score (0–100)
    df["opportunity_score"] = (
        df["opp_energy_pct"]   * OPP_WEIGHTS["opp_energy"]   / 100 +
        df["opp_water_pct"]    * OPP_WEIGHTS["opp_water"]    / 100 +
        df["opp_talent_pct"]   * OPP_WEIGHTS["opp_talent"]   / 100 +
        df["opp_business_pct"] * OPP_WEIGHTS["opp_business"] / 100 +
        df["opp_policy_pct"]   * OPP_WEIGHTS["opp_policy"]   / 100
    ).round(2)

    # Readiness = V1 overall_score (0–100); for Tier 5 use 0
    df["readiness_score"] = df["overall_score"].fillna(0).round(2)

    # Balance Score = weighted combo
    df["balance_score"] = (
        df["readiness_score"]   * BALANCE_WEIGHT_READINESS +
        df["opportunity_score"] * BALANCE_WEIGHT_OPPORTUNITY
    ).round(2)

    # Quadrant label
    def quadrant(row):
        hi_opp     = row["opportunity_score"] >= 50
        lo_burden  = row["readiness_score"]   >= 50   # higher readiness = lower burden
        key = (lo_burden, hi_opp)
        return QUADRANT_LABELS[key][0]

    df["quadrant"] = df.apply(quadrant, axis=1)

    # Opportunity grade
    def opp_grade(s):
        if s >= 75: return "A"
        if s >= 60: return "B"
        if s >= 45: return "C"
        if s >= 30: return "D"
        return "F"

    df["opp_grade"]     = df["opportunity_score"].apply(opp_grade)
    df["opp_rank"]      = df["opportunity_score"].rank(ascending=False, method="min").astype(int)
    df["balance_rank"]  = df["balance_score"].rank(ascending=False, method="min").astype(int)

    return df


# ────────────────────────────────────────────────
# MAP (same as V1 — color by Tier)
# ────────────────────────────────────────────────
def build_map(df_6d, geo, selected_th, visible_set=None):
    m = folium.Map(location=[13.0, 101.5], zoom_start=6,
                   tiles="CartoDB positron", prefer_canvas=True)

    en_lookup = {}
    for _, row in df_6d.iterrows():
        en = to_geo_name(str(row["province_name_en"]))
        en_lookup[en] = row

    sel_en = None
    if selected_th:
        r = df_6d[df_6d["province_name_th"] == selected_th]
        if len(r):
            sel_en = to_geo_name(str(r.iloc[0]["province_name_en"]))

    geo_enriched = copy.deepcopy(geo)
    for feat in geo_enriched["features"]:
        en_name = feat["properties"].get("name","")
        row = en_lookup.get(en_name)
        if row is not None and row["passed_gate"]:
            feat["properties"]["province_th"]    = str(row["province_name_th"])
            feat["properties"]["overall_score"]  = f"{row['overall_score']:.2f}"
            feat["properties"]["grade"]          = str(row["grade"])
            feat["properties"]["gate_status_th"] = "✅ ผ่าน Gate Criteria"
        elif row is not None:
            feat["properties"]["province_th"]    = str(row["province_name_th"])
            feat["properties"]["overall_score"]  = "ไม่ผ่าน Gate Criteria"
            feat["properties"]["grade"]          = "-"
            feat["properties"]["gate_status_th"] = "❌ ไม่ผ่าน Gate Criteria"
        else:
            feat["properties"]["province_th"]    = en_name
            feat["properties"]["overall_score"]  = "N/A"
            feat["properties"]["grade"]          = "-"
            feat["properties"]["gate_status_th"] = "-"

    def style_fn(feat):
        name = feat["properties"]["name"]
        row  = en_lookup.get(name)
        if row is None:
            return {"fillColor":"#E4ECF5","color":"#BBBBBB","weight":0.4,"fillOpacity":0.3}
        if visible_set is not None and row["province_name_th"] not in visible_set:
            return {"fillColor":"#EDEDED","color":"#DADADA","weight":0.4,"fillOpacity":0.18}
        color = tier_color(row["tier"]) if row["passed_gate"] else "#F5B5B5"
        if name == sel_en:
            return {"fillColor": color, "color":"#0A1628","weight":3.2,"fillOpacity":0.92}
        return {"fillColor": color, "color":"#777","weight":0.5,
                "fillOpacity":0.45 if row["passed_gate"] else 0.25}

    folium.GeoJson(
        geo_enriched,
        style_function=style_fn,
        highlight_function=lambda _: {"weight":2.5,"color":"#0A1628","fillOpacity":0.75},
        tooltip=folium.GeoJsonTooltip(
            fields=["province_th","gate_status_th","overall_score","grade"],
            aliases=["จังหวัด","Gate Criteria","คะแนนรวม","Grade"],
            localize=True, sticky=False,
            style="""
                background-color:#0A1628;color:white;font-family:'Sarabun',sans-serif;
                font-size:16px;font-weight:600;padding:10px 16px;border-radius:10px;
                border:2px solid #1A9B6C;line-height:1.8;
            """,
            max_width=230,
        ),
        popup=folium.GeoJsonPopup(
            fields=["province_th","gate_status_th","overall_score","grade"],
            aliases=["🏙️ จังหวัด","🔒 Gate Criteria","⭐ คะแนนรวม","Grade"],
            localize=True,
            style="font-family:'Sarabun',sans-serif;font-size:15px;line-height:1.9;min-width:200px;",
            max_width=260,
        ),
    ).add_to(m)

    leg = """<div style="position:fixed;bottom:24px;left:24px;z-index:1000;background:white;
                padding:12px 16px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);
                font-family:sans-serif;font-size:1rem">
              <b style="color:#0A1628">ระดับศักยภาพ</b><br>
              <span style="color:#1A9B6C">■</span> Tier 1 – Prime<br>
              <span style="color:#5BB8A4">■</span> Tier 2 – Suitable<br>
              <span style="color:#F0C040">■</span> Tier 3 – Conditional<br>
              <span style="color:#BBBBBB">■</span> Tier 4 – Not Recommended<br>
              <span style="color:#F5B5B5">■</span> Tier 5 – ไม่ผ่าน Gate Criteria
            </div>"""
    m.get_root().html.add_child(folium.Element(leg))
    return m


# ────────────────────────────────────────────────
# GATE CARD (V1 — unchanged)
# ────────────────────────────────────────────────
def render_gate_card(row):
    passed = row["gate_status"] == "PASS"
    cnt    = int(row["gate_passed_count"])
    badge  = "<span class='gate-pass'>✅ ผ่าน Gate Criteria</span>" if passed \
             else "<span class='gate-no'>❌ ไม่ผ่าน Gate Criteria</span>"

    st.markdown(f"""
    <div class="result-card result-card-gate">
      <div class="panel-title">🔒 Gate Criteria</div>
      <div style="margin-bottom:10px">{badge}</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
      <div class="score-label">ผ่านเกณฑ์</div>
      <div style="display:flex;align-items:flex-end;gap:10px">
        <div class="score-big">{cnt}</div>
        <div style="font-size:1.5rem;color:#9DC3E6;padding-bottom:10px">/ 6 ข้อ</div>
      </div>
      <div style="font-size:.98rem;color:#9DC3E6;margin-top:4px">เกณฑ์ผ่าน: ต้องผ่านอย่างน้อย 3 ใน 6 ข้อ</div>
    </div>""", unsafe_allow_html=True)

    for gkey, label in GATE_LABELS.items():
        val = row.get(gkey)
        raw_key, unit, dec = GATE_RAW_LABELS[gkey]
        raw_val = row.get(raw_key, "-")
        if pd.notna(val) and int(val) == 1:
            cls, icon, txt = "gate-row-pass", "✅", "ผ่าน"
        elif pd.notna(val) and int(val) == 0:
            cls, icon, txt = "gate-row-fail", "❌", "ไม่ผ่าน"
        else:
            cls, icon, txt = "gate-row-na", "⚠️", "ไม่มีข้อมูล"
        if unit and dec is not None and isinstance(raw_val, (int,float)):
            raw_str = f"{raw_val:,.{dec}f} {unit}"
        else:
            raw_str = f"{raw_val}"
        st.markdown(f"""
        <div class="gate-row {cls}">
          <div class="gate-crit-label">{icon} {label}</div>
          <div style="text-align:right">
            <div class="gate-crit-value">ค่าจริง: {raw_str}</div>
            <div style="font-weight:700;color:{'#1A9B6C' if icon=='✅' else ('#E04040' if icon=='❌' else '#999')}">{txt}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="gate-row gate-row-pass">
      <div class="gate-crit-label">🛣️ G7 — ทางหลวงแผ่นดิน</div>
      <div style="text-align:right">
        <div class="gate-crit-value">ค่าจริง: มี</div>
        <div style="font-weight:700;color:#1A9B6C">✅ ผ่าน</div>
      </div>
    </div>
    </div>""", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# 6D CARD (V1 — unchanged)
# ────────────────────────────────────────────────
def render_6d_card(row, passed_total):
    if not row["passed_gate"]:
        st.markdown("""
        <div class="result-card result-card-6d">
          <div class="panel-title">📊 6D Assessment</div>
          <div style="background:#FFF0F0;border-radius:12px;padding:24px;text-align:center;
                      border:1px dashed #E04040;margin-top:10px">
            <div style="font-size:2rem;margin-bottom:8px">🚫</div>
            <div style="font-size:1.15rem;font-weight:700;color:#C0392B;margin-bottom:6px">
              ไม่มีคะแนน 6D Assessment
            </div>
            <div style="font-size:1rem;color:#888">
              จังหวัดนี้ไม่ผ่าน Gate Criteria (&lt; 3/6 ข้อ)<br>จัดเป็น <b>Tier 5</b> โดยอัตโนมัติ
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        return

    score = row["overall_score"]
    grade = str(row["grade"]).strip()
    tier  = row["tier"]
    rank  = int(row["rank_overall"]) if pd.notna(row["rank_overall"]) else None
    tc    = tier_color(tier)
    gc    = GRADE_COLOR.get(grade,"#888")

    st.markdown(f"""
    <div class="result-card result-card-6d">
      <div class="panel-title">📊 6D Assessment (V1 — Readiness)</div>
      <div style="font-size:1.05rem;color:#555;margin-bottom:10px">
        อันดับ <b>#{rank}</b> จาก {passed_total} จังหวัดที่ผ่าน Gate
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
      <div class="score-label">คะแนน Readiness (Overall Score)</div>
      <div style="display:flex;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-top:4px">
        <div class="score-big">{score:.2f}</div>
        <div style="padding-bottom:6px;display:flex;flex-direction:column;gap:6px">
          <span style="background:{tc};color:white;padding:6px 18px;border-radius:22px;
                       font-size:1.08rem;font-weight:700">{tier_short(tier)}</span>
          <span style="background:{gc};color:white;padding:5px 16px;border-radius:22px;
                       font-size:1.05rem;font-weight:700">Grade {grade}</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    badges = []
    if row["EEC"]:       badges.append("✅ EEC Zone")
    if row["Strategic"]: badges.append("🌐 Strategic Province")
    if badges:
        st.markdown(" ".join([f'<span class="chip-green">{b}</span>' for b in badges]),
                    unsafe_allow_html=True)

    st.markdown('<div class="section-header">คะแนนรายมิติ (6D)</div>', unsafe_allow_html=True)
    for k in DIM_KEYS:
        pct   = float(row[f"{k}_pct"])
        raw_w = float(row[k])
        mx    = DIM_MAX[k]
        color = DIM_COLORS[k]
        label = DIM_LABELS[k]
        st.markdown(f"""
        <div style="margin-bottom:12px">
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span class="dim-label">{label}</span>
            <span class="dim-value" style="color:{color}">{pct:.0f} <span style="font-size:1rem;color:#aaa">/ 100</span></span>
          </div>
          <div style="background:#E4ECF5;border-radius:8px;height:13px;overflow:hidden">
            <div style="width:{max(pct,2)}%;background:{color};height:100%;border-radius:8px"></div>
          </div>
          <div class="dim-sub">น้ำหนักคะแนน: {raw_w:.2f} / {mx}</div>
        </div>""", unsafe_allow_html=True)

    with st.expander("📋 ข้อมูลดิบ"):
        raw_items = {
            "พลังงานติดตั้งรวม (MW)":         f"{float(row.get('installed_mw',0)):,.1f}",
            "ความจุกักเก็บน้ำ (ล้าน ลบ.ม.)":  f"{float(row.get('storage_mcm',0)):,.1f}",
            "มหาวิทยาลัย (วิทยาเขต)":         f"{int(row.get('univ_count',0))} แห่ง",
            "วิทยาลัยอาชีวศึกษา":             f"{int(row.get('voc_count',0))} แห่ง",
            "โครงการ BOI DC":                 f"{int(row.get('boi_projects',0))} โครงการ",
            "นิคมอุตสาหกรรม (IEAT)":          f"{int(row.get('ieat_count',0))} แห่ง",
            "DC IT Load (MW)":                f"{float(row.get('dc_it_load_mw',0)):.1f}",
            "Flood Risk":                     f"{float(row.get('flood_risk',0)):.1f} / 100",
            "Seismic Risk":                   f"{float(row.get('seismic_risk',0)):.1f} / 100",
            "EEC Zone":                       "✅ ใช่" if row["EEC"] else "❌ ไม่ใช่",
            "Strategic Digital Province":     "✅ ใช่" if row["Strategic"] else "❌ ไม่ใช่",
        }
        st.table(pd.DataFrame(list(raw_items.items()), columns=["ตัวชี้วัด","ค่า"]))

    st.markdown("</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# V2: OPPORTUNITY CARD
# ────────────────────────────────────────────────
def render_opportunity_card(row):
    opp_score = float(row["opportunity_score"])
    opp_grade = str(row["opp_grade"])
    opp_rank  = int(row["opp_rank"])
    gc        = GRADE_COLOR.get(opp_grade, "#888")

    st.markdown(f"""
    <div class="result-card result-card-oppty">
      <div class="panel-title">🔮 Opportunity Score (V2)</div>
      <div style="font-size:1.05rem;color:#555;margin-bottom:10px">
        อันดับ <b>#{opp_rank}</b> จาก 77 จังหวัด (ทุกจังหวัดมีคะแนน)
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box-v2">
      <div class="score-label-v2">คะแนน Opportunity Score</div>
      <div style="display:flex;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-top:4px">
        <div class="score-big">{opp_score:.2f}</div>
        <div style="padding-bottom:6px">
          <span style="background:{gc};color:white;padding:6px 18px;border-radius:22px;
                       font-size:1.08rem;font-weight:700">Grade {opp_grade}</span>
        </div>
      </div>
      <div style="font-size:.95rem;color:#C4B5FD;margin-top:6px">
        พลังงาน 30% · น้ำ 25% · บุคลากร 20% · ธุรกิจ 15% · นโยบาย 10%
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header-v2">คะแนนรายมิติ (Opportunity)</div>', unsafe_allow_html=True)
    for k in OPP_WEIGHTS:
        pct   = float(row[f"{k}_pct"])
        color = OPP_COLORS[k]
        label = OPP_LABELS[k]
        wt    = OPP_WEIGHTS[k]
        st.markdown(f"""
        <div style="margin-bottom:12px">
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span class="dim-label">{label}</span>
            <span class="dim-value" style="color:{color}">{pct:.0f} <span style="font-size:1rem;color:#aaa">/ 100</span></span>
          </div>
          <div style="background:#EEE8FF;border-radius:8px;height:13px;overflow:hidden">
            <div style="width:{max(pct,2)}%;background:{color};height:100%;border-radius:8px"></div>
          </div>
          <div class="dim-sub">น้ำหนัก: {wt}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# V2: BALANCE SCORE CARD
# ────────────────────────────────────────────────
def render_balance_card(row):
    balance   = float(row["balance_score"])
    readiness = float(row["readiness_score"])
    opp       = float(row["opportunity_score"])
    b_rank    = int(row["balance_rank"])
    quad      = row["quadrant"]

    # Quadrant color and label
    hi_opp    = opp    >= 50
    lo_burden = readiness >= 50
    key = (lo_burden, hi_opp)
    q_name, q_sub, q_bg, q_color = QUADRANT_LABELS[key]

    st.markdown(f"""
    <div class="result-card result-card-balance">
      <div class="panel-title">⚖️ Balance Score (V2)</div>
      <div style="margin-bottom:10px">
        <span style="background:{q_color};color:white;padding:7px 18px;border-radius:22px;
                     font-size:1.05rem;font-weight:700">{q_name}</span>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box-balance">
      <div class="score-label-bal">Balance Score (อันดับ #{b_rank} / 77)</div>
      <div style="display:flex;align-items:flex-end;gap:8px;margin-top:4px">
        <div class="score-big">{balance:.2f}</div>
      </div>
      <div style="font-size:.95rem;color:#FFC080;margin-top:6px">
        Readiness {BALANCE_WEIGHT_READINESS*100:.0f}% × {readiness:.1f}
        + Opportunity {BALANCE_WEIGHT_OPPORTUNITY*100:.0f}% × {opp:.1f}
      </div>
    </div>""", unsafe_allow_html=True)

    # Sub description
    st.markdown(f"""
    <div class="quad-info" style="background:{q_bg};border-color:{q_color}40">
      <b style="color:{q_color}">{q_sub}</b><br>
      <span style="font-size:.95rem;color:#555">
        Readiness: <b>{readiness:.1f}</b> &nbsp;|&nbsp; Opportunity: <b>{opp:.1f}</b>
      </span>
    </div>""", unsafe_allow_html=True)

    # Mini comparison bars
    for label, val, color in [
        ("📊 Readiness Score (V1)", readiness, "#2E75B6"),
        ("🔮 Opportunity Score (V2)", opp, "#6C47FF"),
        ("⚖️ Balance Score", balance, "#E07B00"),
    ]:
        st.markdown(f"""
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span style="font-size:1.05rem;font-weight:600">{label}</span>
            <span style="font-size:1.1rem;font-weight:700;color:{color}">{val:.1f}</span>
          </div>
          <div style="background:#F0F0F0;border-radius:8px;height:11px;overflow:hidden">
            <div style="width:{max(val,2)}%;background:{color};height:100%;border-radius:8px"></div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# V2: BALANCE QUADRANT CHART
# ────────────────────────────────────────────────
def render_balance_quadrant(df_all: pd.DataFrame, highlight_th: str | None = None):
    """Scatter plot: X = Readiness, Y = Opportunity. 4-quadrant background."""

    # Quadrant background shapes
    shapes = [
        # Top-right: PRIME OPPORTUNITY (green)
        dict(type="rect", x0=50, x1=100, y0=50, y1=100,
             fillcolor="rgba(26,155,108,0.08)", line_width=0),
        # Top-left: HIGH POTENTIAL / HIGH BURDEN (orange)
        dict(type="rect", x0=0, x1=50, y0=50, y1=100,
             fillcolor="rgba(208,112,10,0.08)", line_width=0),
        # Bottom-right: LIMITED UPSIDE (blue)
        dict(type="rect", x0=50, x1=100, y0=0, y1=50,
             fillcolor="rgba(79,70,229,0.06)", line_width=0),
        # Bottom-left: BURDEN TRAP (red)
        dict(type="rect", x0=0, x1=50, y0=0, y1=50,
             fillcolor="rgba(224,64,64,0.06)", line_width=0),
    ]
    annotations = [
        dict(x=75, y=97, text="<b>PRIME OPPORTUNITY</b>", showarrow=False,
             font=dict(size=13, color="#1A9B6C"), xanchor="center"),
        dict(x=25, y=97, text="<b>HIGH POTENTIAL,<br>HIGH BURDEN</b>", showarrow=False,
             font=dict(size=12, color="#D0700A"), xanchor="center"),
        dict(x=75, y=3,  text="<b>LIMITED UPSIDE</b>", showarrow=False,
             font=dict(size=13, color="#4F46E5"), xanchor="center"),
        dict(x=25, y=3,  text="<b>BURDEN TRAP</b>", showarrow=False,
             font=dict(size=13, color="#E04040"), xanchor="center"),
    ]

    color_map = {
        "Tier 1": "#1A9B6C", "Tier 2": "#5BB8A4",
        "Tier 3": "#F0C040", "Tier 4": "#BBBBBB", "Tier 5": "#E04040",
    }

    def get_tier_group(t):
        for k in color_map:
            if str(t).startswith(k):
                return k
        return "Tier 5"

    df_all = df_all.copy()
    df_all["tier_group"] = df_all["tier"].apply(get_tier_group)

    fig = go.Figure()

    # Draw each tier as a separate trace for legend
    for tier_key, color in color_map.items():
        subset = df_all[df_all["tier_group"] == tier_key]
        if subset.empty:
            continue
        is_hl = subset["province_name_th"] == highlight_th if highlight_th else pd.Series(False, index=subset.index)
        # Non-highlighted
        sub_normal = subset[~is_hl]
        if not sub_normal.empty:
            fig.add_trace(go.Scatter(
                x=sub_normal["readiness_score"],
                y=sub_normal["opportunity_score"],
                mode="markers",
                name=tier_key,
                marker=dict(color=color, size=10, opacity=0.7,
                            line=dict(width=0.5, color="white")),
                text=sub_normal["province_name_th"],
                customdata=sub_normal[["province_name_en","readiness_score",
                                       "opportunity_score","balance_score","quadrant"]].values,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Readiness: %{customdata[1]:.1f}<br>"
                    "Opportunity: %{customdata[2]:.1f}<br>"
                    "Balance: %{customdata[3]:.1f}<br>"
                    "Quadrant: %{customdata[4]}<extra></extra>"
                ),
                showlegend=True,
                legendgroup=tier_key,
            ))

    # Highlighted province
    if highlight_th:
        hl = df_all[df_all["province_name_th"] == highlight_th]
        if not hl.empty:
            row = hl.iloc[0]
            tc = color_map.get(row["tier_group"], "#888")
            fig.add_trace(go.Scatter(
                x=[row["readiness_score"]],
                y=[row["opportunity_score"]],
                mode="markers+text",
                name="เลือกอยู่",
                marker=dict(color=tc, size=20, opacity=1,
                            line=dict(width=2.5, color="#0A1628"),
                            symbol="star"),
                text=[row["province_name_th"]],
                textposition="top center",
                textfont=dict(size=13, color="#0A1628"),
                hovertemplate=(
                    f"<b>{row['province_name_th']}</b><br>"
                    f"Readiness: {row['readiness_score']:.1f}<br>"
                    f"Opportunity: {row['opportunity_score']:.1f}<br>"
                    f"Balance: {row['balance_score']:.1f}<extra></extra>"
                ),
                showlegend=True,
                legendgroup="selected",
            ))

    all_shapes = shapes + [
        dict(type="line", x0=50, x1=50, y0=0, y1=100,
             line=dict(color="#AAAAAA", width=1.5, dash="dash")),
        dict(type="line", x0=0, x1=100, y0=50, y1=50,
             line=dict(color="#AAAAAA", width=1.5, dash="dash")),
    ]
    fig.update_layout(
        shapes=all_shapes,
        annotations=annotations,
        xaxis=dict(title="Readiness Score (0–100)  ← V1 6D Score →",
                   range=[0,100], zeroline=False, gridcolor="#EEEEEE",
                   tickfont=dict(size=12)),
        yaxis=dict(title="Opportunity Score (0–100)  ← V2 →",
                   range=[0,100], zeroline=False, gridcolor="#EEEEEE",
                   tickfont=dict(size=12)),
        legend=dict(orientation="h", y=-0.15, font=dict(size=12)),
        height=520,
        margin=dict(l=60, r=20, t=40, b=80),
        plot_bgcolor="#FAFAFA",
        paper_bgcolor="white",
        hovermode="closest",
        font=dict(family="Sarabun, sans-serif"),
    )
    return fig


# ────────────────────────────────────────────────
# RADAR CHART (for comparison)
# ────────────────────────────────────────────────
def render_radar(df_sel):
    colors = ["#1A9B6C","#2E75B6","#E07B00","#7B4FBF","#C0392B"]
    fig = go.Figure()
    labels = [DIM_LABELS[k] for k in DIM_KEYS]
    for i, (_, row) in enumerate(df_sel.iterrows()):
        vals = [float(row[f"{k}_pct"]) for k in DIM_KEYS] + [float(row[f"{DIM_KEYS[0]}_pct"])]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=labels+[labels[0]], fill="toself",
            name=row["province_name_th"], line_color=colors[i%len(colors)], opacity=0.85,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100],
                                   tickfont=dict(size=10), gridcolor="#DDD"),
                   angularaxis=dict(tickfont=dict(size=11))),
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, font=dict(size=11)),
        height=290, margin=dict(l=24,r=24,t=16,b=60),
        paper_bgcolor="#F5F8FC",
    )
    return fig


# ────────────────────────────────────────────────
# WELCOME / DEFAULT STATE
# ────────────────────────────────────────────────
def render_welcome(df_gate, df_passed):
    n_pass = (df_gate["gate_status"]=="PASS").sum()
    st.markdown(f"""
    <div class="welcome-box">
      <div style="font-size:3.2rem;margin-bottom:12px">⚖️</div>
      <div style="font-size:1.4rem;font-weight:800;color:#0A1628;margin-bottom:10px">
        เลือกจังหวัดเพื่อดูผล Gate Criteria · 6D · Opportunity · Balance Score
      </div>
      <div style="font-size:1.1rem;color:#555;line-height:1.9">
        เลือกจาก Dropdown ด้านซ้าย หรือคลิกบนแผนที่ · หรือดู Balance Quadrant ของทุกจังหวัด<br>
        ผ่าน Gate ทั้งหมด <b>{n_pass} / 77</b> จังหวัด · มีคะแนน 6D <b>{len(df_passed)}</b> จังหวัด
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:18px">🏆 Top 5 Balance Score (V2)</div>',
                unsafe_allow_html=True)
    top5 = df_passed.sort_values("balance_score", ascending=False).head(5)
    clicked = None
    for _, row in top5.iterrows():
        tc = tier_color(row["tier"])
        col_info, col_btn = st.columns([3,1])
        with col_info:
            q_name, q_sub, q_bg, q_color = QUADRANT_LABELS[
                (row["readiness_score"] >= 50, row["opportunity_score"] >= 50)
            ]
            st.markdown(f"""
            <div style="padding:10px 4px;border-bottom:1px solid #E8EEF4">
              <div style="font-size:1.18rem;font-weight:700;color:#0A1628">
                #{int(row['balance_rank'])} {row['province_name_th']}
                <span style="font-size:1.02rem;color:#888;font-weight:400"> {row['province_name_en']}</span>
              </div>
              <div style="margin-top:4px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                <span style="font-size:1.2rem;font-weight:800;color:{tc}">{row['balance_score']:.2f}</span>
                <span style="font-size:.92rem;color:#777">Readiness {row['readiness_score']:.0f} · Opp {row['opportunity_score']:.0f}</span>
                <span style="background:{q_color};color:white;padding:2px 10px;border-radius:10px;font-size:.88rem;font-weight:700">{q_name}</span>
              </div>
            </div>""", unsafe_allow_html=True)
        with col_btn:
            if st.button("เลือก", key=f"top5b_{row['province_name_th']}", use_container_width=True):
                clicked = row["province_name_th"]
    return clicked


# ────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="topnav">
      <div>
        <div class="topnav-title">🗺️ Data Center Site Selection · Thailand</div>
        <div class="topnav-sub">Gate Criteria · 6D Readiness · Opportunity Score · Balance Quadrant</div>
      </div>
      <div class="version-badge">V 2.0</div>
    </div>""", unsafe_allow_html=True)

    try:
        df_gate = load_gate()
        df_6d   = load_6d()
        geo     = load_geo()
    except FileNotFoundError as e:
        st.error(f"❌ ไม่พบไฟล์: {e}"); st.stop()

    df_all    = compute_opportunity(df_6d)
    df_passed = df_all[df_all["passed_gate"]].copy()

    if "selected"     not in st.session_state: st.session_state.selected     = None
    if "compare_list" not in st.session_state: st.session_state.compare_list = []

    col_left, col_main = st.columns([1.8, 6.0])

    # ═══════ LEFT — FILTER ═══════
    with col_left:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown("#### 🔎 ค้นหาจังหวัด")
        all_provinces = ["— กรุณาเลือกจังหวัด —"] + df_gate["province_name_th"].tolist()
        cur_idx = 0
        if st.session_state.selected in df_gate["province_name_th"].tolist():
            cur_idx = df_gate["province_name_th"].tolist().index(st.session_state.selected) + 1
        sel_dd = st.selectbox("เลือกจังหวัด (77 จังหวัด)", options=all_provinces,
                              index=cur_idx, key="prov_dd")
        if sel_dd != "— กรุณาเลือกจังหวัด —":
            st.session_state.selected = sel_dd

        st.markdown("---")
        st.markdown('<div class="section-header">สถานะ Gate Criteria</div>', unsafe_allow_html=True)
        gate_filter = st.radio("", ["ทั้งหมด","✅ ผ่าน Gate Criteria","❌ ไม่ผ่าน Gate Criteria"],
                               label_visibility="collapsed", key="gate_status_radio")
        n_pass = (df_gate["gate_status"]=="PASS").sum()
        n_fail = len(df_gate) - n_pass
        st.markdown(f"""
        <div style="display:flex;gap:10px;margin-top:10px;margin-bottom:6px">
          <div style="flex:1;background:#E6F7EF;border-radius:10px;padding:12px;text-align:center">
            <div style="font-size:1.6rem;font-weight:800;color:#1A9B6C">{n_pass}</div>
            <div style="font-size:.92rem;color:#555">ผ่าน Gate</div>
          </div>
          <div style="flex:1;background:#FFF0F0;border-radius:10px;padding:12px;text-align:center">
            <div style="font-size:1.6rem;font-weight:800;color:#E04040">{n_fail}</div>
            <div style="font-size:.92rem;color:#555">ไม่ผ่าน</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">คะแนนขั้นต่ำ (6D)</div>', unsafe_allow_html=True)
        min_score = st.slider("", 0, 80, 0, key="score_slider", label_visibility="collapsed")

        eec_only   = st.checkbox("EEC Zone เท่านั้น",               key="eec_cb")
        strat_only = st.checkbox("Strategic Digital Province เท่านั้น", key="strat_cb")

        if st.button("🔄 รีเซ็ตตัวกรอง", use_container_width=True, key="reset_btn"):
            st.session_state.selected     = None
            st.session_state.compare_list = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### ⚖️ เปรียบเทียบ (เฉพาะที่ผ่าน Gate)")
        prov_list  = df_passed.sort_values("balance_score", ascending=False)["province_name_th"].tolist()
        compare_sel = st.multiselect(
            "เลือกสูงสุด 5 จังหวัด", prov_list,
            default=st.session_state.compare_list[:5],
            max_selections=5, key="compare_ms", label_visibility="collapsed",
        )
        st.session_state.compare_list = compare_sel
        if len(compare_sel) >= 2:
            df_cmp = df_passed[df_passed["province_name_th"].isin(compare_sel)]
            st.plotly_chart(render_radar(df_cmp), use_container_width=True)
        else:
            st.caption("เลือกอย่างน้อย 2 จังหวัดเพื่อดู Radar")

    # ═══════ MAIN — TABS ═══════
    with col_main:
        tab_map, tab_quad, tab_rank = st.tabs([
            "🗺️ แผนที่ + Province Detail",
            "⚖️ Balance Quadrant (V2)",
            "🏆 Balance Ranking (V2)",
        ])

        # ─── TAB 1: MAP + PROVINCE DETAIL ───
        with tab_map:
            df_filtered = df_all.merge(df_gate[["province_name_th","gate_status"]],
                                       on="province_name_th", how="left", suffixes=("","_g"))
            if gate_filter == "✅ ผ่าน Gate Criteria":
                df_filtered = df_filtered[df_filtered["gate_status_g"]=="PASS"]
            elif gate_filter == "❌ ไม่ผ่าน Gate Criteria":
                df_filtered = df_filtered[df_filtered["gate_status_g"]=="FAIL"]
            df_filtered = df_filtered[df_filtered["overall_score"].fillna(0) >= min_score]
            if eec_only:   df_filtered = df_filtered[df_filtered["EEC"]]
            if strat_only: df_filtered = df_filtered[df_filtered["Strategic"]]

            st.markdown(
                f'<div style="font-size:1.02rem;color:#888;margin-bottom:6px">'
                f'🗺️ แสดง <b>{len(df_filtered)}</b> จาก 77 จังหวัด · '
                f'คลิกบนแผนที่ หรือเลือก Dropdown เพื่อดูผล</div>',
                unsafe_allow_html=True)

            visible_set = set(df_filtered["province_name_th"].tolist())
            m = build_map(df_all, geo, st.session_state.selected, visible_set=visible_set)
            map_data = st_folium(m, width="100%", height=440,
                                 key="main_map", returned_objects=["last_object_clicked_popup"])

            if map_data and map_data.get("last_object_clicked_popup"):
                popup_text = map_data["last_object_clicked_popup"] or ""
                for th in df_all["province_name_th"].tolist():
                    if th in popup_text:
                        if st.session_state.selected != th:
                            st.session_state.selected = th
                            st.rerun()

            st.markdown("---")
            sel = st.session_state.selected
            if sel and sel in df_gate["province_name_th"].values:
                gate_row = df_gate[df_gate["province_name_th"]==sel].iloc[0]
                d6_row   = df_all[df_all["province_name_th"]==sel].iloc[0]

                st.markdown(f"""
                <div style="font-size:1.6rem;font-weight:800;color:#0A1628;margin-bottom:4px">
                  📍 {sel} <span style="font-size:1.05rem;color:#888;font-weight:400">
                  {gate_row['province_name_en']} · {gate_row['region']}</span>
                </div>""", unsafe_allow_html=True)

                # Row 1: Gate + 6D (V1)
                col_gate, col_6d = st.columns(2)
                with col_gate:
                    render_gate_card(gate_row)
                with col_6d:
                    render_6d_card(d6_row, len(df_passed))

                st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

                # Row 2: Opportunity + Balance (V2)
                col_opp, col_bal = st.columns(2)
                with col_opp:
                    render_opportunity_card(d6_row)
                with col_bal:
                    render_balance_card(d6_row)

            else:
                clicked = render_welcome(df_gate, df_passed)
                if clicked:
                    st.session_state.selected = clicked
                    st.rerun()

        # ─── TAB 2: BALANCE QUADRANT ───
        with tab_quad:
            st.markdown("""
            <div style="background:#F3EEFF;border-radius:12px;padding:14px 20px;
                        border-left:4px solid #6C47FF;margin-bottom:16px;font-size:1.05rem">
              <b style="color:#6C47FF">⚖️ Balance Quadrant (V2 Concept)</b><br>
              <span style="color:#444">
                แกน X = Readiness Score (6D, V1) — ยิ่งสูง ยิ่งพร้อม ภาระน้อย<br>
                แกน Y = Opportunity Score (V2) — ยิ่งสูง ยิ่งมีโอกาสเติบโต<br>
                จุดกึ่งกลาง = 50 คะแนน · ★ = จังหวัดที่เลือกอยู่
              </span>
            </div>""", unsafe_allow_html=True)

            # Quadrant filter
            quad_filter = st.selectbox(
                "กรองตาม Quadrant",
                ["ทุก Quadrant"] + [v[0] for v in QUADRANT_LABELS.values()],
                key="quad_filter",
                label_visibility="visible",
            )
            df_quad = df_all.copy()
            if quad_filter != "ทุก Quadrant":
                df_quad = df_quad[df_quad["quadrant"] == quad_filter]

            fig = render_balance_quadrant(df_quad, highlight_th=st.session_state.selected)
            st.plotly_chart(fig, use_container_width=True)

            # Quadrant summary stats
            st.markdown('<div class="section-header-v2">สรุปจำนวนจังหวัดในแต่ละ Quadrant</div>',
                        unsafe_allow_html=True)
            q_counts = df_all.groupby("quadrant").size().reset_index(name="count")
            col1, col2, col3, col4 = st.columns(4)
            for col, (key, (name, sub, bg, color)) in zip(
                [col1, col2, col3, col4], QUADRANT_LABELS.items()
            ):
                cnt = q_counts[q_counts["quadrant"]==name]["count"].sum() if name in q_counts["quadrant"].values else 0
                with col:
                    st.markdown(f"""
                    <div style="background:{bg};border:2px solid {color}40;border-radius:12px;
                                padding:14px;text-align:center">
                      <div style="font-size:2.2rem;font-weight:800;color:{color}">{int(cnt)}</div>
                      <div style="font-size:.95rem;font-weight:700;color:{color};margin-bottom:2px">{name}</div>
                      <div style="font-size:.88rem;color:#666">{sub}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("""
            <div style="background:#FFFBF0;border-left:3px solid #D0700A;border-radius:6px;
                        padding:10px 16px;margin-top:14px;font-size:.95rem;color:#555">
              ⚠️ <b>หมายเหตุ:</b> Opportunity Score คำนวณจากข้อมูล proxy (ติดตั้ง MW, กักเก็บน้ำ,
              สถาบันการศึกษา, BOI/IEAT, EEC) — เป็นตัวชี้วัดเชิงแนวคิด (V2 Concept)
              ตามกรอบของ Teachavorasinskun (2025) ยังไม่ใช่ผลวิเคราะห์จริง
            </div>""", unsafe_allow_html=True)

        # ─── TAB 3: BALANCE RANKING ───
        with tab_rank:
            st.markdown("""
            <div style="background:#FFF8F0;border-radius:12px;padding:14px 20px;
                        border-left:4px solid #E07B00;margin-bottom:16px;font-size:1.05rem">
              <b style="color:#E07B00">🏆 Balance Score Ranking</b> — อันดับจังหวัดตาม Balance Score (V2)<br>
              <span style="color:#444">Balance Score = Readiness {:.0f}% + Opportunity {:.0f}%</span>
            </div>""".format(BALANCE_WEIGHT_READINESS*100, BALANCE_WEIGHT_OPPORTUNITY*100),
            unsafe_allow_html=True)

            sort_by = st.radio("เรียงลำดับตาม",
                               ["⚖️ Balance Score","📊 Readiness Score","🔮 Opportunity Score"],
                               horizontal=True, key="rank_sort")
            sort_col = {"⚖️ Balance Score":"balance_score",
                        "📊 Readiness Score":"readiness_score",
                        "🔮 Opportunity Score":"opportunity_score"}[sort_by]

            show_tier5 = st.checkbox("แสดงจังหวัดที่ไม่ผ่าน Gate (Tier 5) ด้วย", value=False, key="show_t5")
            df_rank = df_all if show_tier5 else df_passed
            df_rank = df_rank.sort_values(sort_col, ascending=False).reset_index(drop=True)

            for i, (_, row) in enumerate(df_rank.iterrows()):
                tc    = tier_color(row["tier"])
                q_name, q_sub, q_bg, q_color = QUADRANT_LABELS[
                    (row["readiness_score"] >= 50, row["opportunity_score"] >= 50)
                ]
                rank_n = i + 1
                col_r, col_btn = st.columns([5, 1])
                with col_r:
                    st.markdown(f"""
                    <div style="padding:10px 6px;border-bottom:1px solid #EEEEEE;
                                display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                      <div style="font-size:1.3rem;font-weight:800;color:#CCC;min-width:32px">
                        #{rank_n}
                      </div>
                      <div style="flex:1;min-width:120px">
                        <div style="font-size:1.12rem;font-weight:700;color:#0A1628">
                          {row['province_name_th']}
                          <span style="font-size:.95rem;color:#888;font-weight:400"> {row['province_name_en']}</span>
                        </div>
                        <div style="margin-top:3px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                          <span style="font-size:.92rem;color:#777">Balance <b style="color:#E07B00">{row['balance_score']:.1f}</b></span>
                          <span style="font-size:.92rem;color:#777">Readiness <b style="color:#2E75B6">{row['readiness_score']:.1f}</b></span>
                          <span style="font-size:.92rem;color:#777">Opp <b style="color:#6C47FF">{row['opportunity_score']:.1f}</b></span>
                        </div>
                      </div>
                      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
                        <span style="background:{tc};color:white;padding:3px 12px;border-radius:10px;font-size:.88rem;font-weight:700">{tier_short(row['tier'])}</span>
                        <span style="background:{q_color};color:white;padding:3px 10px;border-radius:10px;font-size:.82rem;font-weight:700">{q_name}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                with col_btn:
                    if st.button("เลือก", key=f"rank_{row['province_name_th']}", use_container_width=True):
                        st.session_state.selected = row["province_name_th"]
                        st.rerun()

    st.markdown("""
    <div style="background:#F3EEFF;border-radius:8px;padding:12px 20px;margin-top:16px;
                border-left:4px solid #6C47FF;font-size:1.04rem;color:#333">
      💡 <b>V2 — Balance Score</b> = Readiness (6D) × 60% + Opportunity × 40%
      &nbsp;|&nbsp; Opportunity = พลังงาน 30% + น้ำ 25% + บุคลากร 20% + ธุรกิจ 15% + นโยบาย 10%
      &nbsp;|&nbsp; <b>แนวคิดตาม Teachavorasinskun (2025) Chapter 6</b>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
