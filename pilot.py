"""
Thailand Data Center Site Suitability Dashboard
แสดง Gate Criteria และ 6D Assessment ของจังหวัดที่เลือกพร้อมกัน (ไม่แยก Step)
ข้อมูล: มิ.ย. 2569 (v3 — After Defense)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json, os, copy

# ────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="DC Site Selection | Thailand",
    page_icon="🗺️",
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
/* คืน font icon ของ Streamlit (ลูกศร expander ฯลฯ) ไม่ให้โดน override จนกลายเป็นตัวอักษรซ้อน */
[data-testid="stIconMaterial"], [data-testid*="Icon"], span[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 0rem; padding-bottom: 0.5rem;}

/* ── Top Nav ── */
.topnav {
    background:#0A1628; color:white; padding:14px 28px;
    display:flex; align-items:center; justify-content:space-between;
    border-bottom:3px solid #1A9B6C; margin-bottom:6px;
}
.topnav-title {font-size:1.4rem; font-weight:700; color:#fff; letter-spacing:.3px}
.topnav-sub   {font-size:1.02rem; color:#9DC3E6; margin-top:2px}

/* ── Section header ── */
.section-header {
    font-size:1.08rem; font-weight:700; color:#1A9B6C;
    text-transform:uppercase; letter-spacing:.06em;
    border-left:4px solid #1A9B6C; padding-left:10px;
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

/* ── Side-by-side result cards ── */
.result-card {
    background:white; border-radius:16px; padding:20px 22px;
    border:2px solid #E4ECF5; height:100%;
}
.result-card-gate { border-top:5px solid #1A9B6C; }
.result-card-6d   { border-top:5px solid #2E75B6; }

/* ── Score card box ── */
.score-box {
    background:linear-gradient(135deg,#0D2137 0%,#1A3A5C 100%);
    border-radius:14px; padding:22px 26px; margin-bottom:14px;
    border:1px solid #2E75B6;
}
.score-big  {font-size:4rem; font-weight:800; color:#fff; line-height:1}
.score-label{font-size:1.08rem; color:#9DC3E6; margin-bottom:4px; font-weight:600}

/* ── Gate badges ── */
.gate-pass  {display:inline-block;background:#1A9B6C;color:white;
             padding:7px 20px;border-radius:22px;font-size:1.08rem;font-weight:700;}
.gate-review{display:inline-block;background:#FFC000;color:#000;
             padding:7px 20px;border-radius:22px;font-size:1.08rem;font-weight:700;}
.gate-no    {display:inline-block;background:#E04040;color:white;
             padding:7px 20px;border-radius:22px;font-size:1.08rem;font-weight:700;}

/* ── Chips ── */
.chip-green {background:#E6F7EF;color:#1A9B6C;border:1px solid #B2DFD1;
             padding:6px 16px;border-radius:22px;font-size:1.05rem;margin:3px;display:inline-block}
.chip-red   {background:#FFF0F0;color:#C0392B;border:1px solid #F5B5B5;
             padding:6px 16px;border-radius:22px;font-size:1.05rem;margin:3px;display:inline-block}
.chip-orange{background:#FFF8E6;color:#D0700A;border:1px solid #FACEAA;
             padding:6px 16px;border-radius:22px;font-size:1.05rem;margin:3px;display:inline-block}

/* ── Welcome box ── */
.welcome-box {
    background:linear-gradient(135deg,#EBF4FF 0%,#E2F4ED 100%);
    border-radius:16px; padding:34px 26px; text-align:center;
    border:2px dashed #9DC3E6; margin-top:10px;
    font-size:1.08rem;
}

/* ── Bar label text ── */
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

# ────────────────────────────────────────────────
# DATA
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
# MAP — combined: สีตาม Tier (Tier 5 = ไม่ผ่าน Gate)
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
            feat["properties"]["province_th"]   = str(row["province_name_th"])
            feat["properties"]["overall_score"] = f"{row['overall_score']:.2f}"
            feat["properties"]["grade"]         = str(row["grade"])
            feat["properties"]["gate_status_th"]= "✅ ผ่าน Gate Criteria"
        elif row is not None:
            feat["properties"]["province_th"]   = str(row["province_name_th"])
            feat["properties"]["overall_score"] = "ไม่ผ่าน Gate Criteria"
            feat["properties"]["grade"]         = "-"
            feat["properties"]["gate_status_th"]= "❌ ไม่ผ่าน Gate Criteria"
        else:
            feat["properties"]["province_th"]   = en_name
            feat["properties"]["overall_score"] = "N/A"
            feat["properties"]["grade"]         = "-"
            feat["properties"]["gate_status_th"]= "-"

    def style_fn(feat):
        name = feat["properties"]["name"]
        row  = en_lookup.get(name)
        if row is None:
            return {"fillColor":"#E4ECF5","color":"#BBBBBB","weight":0.4,"fillOpacity":0.3}
        # ไม่อยู่ในตัวกรองปัจจุบัน → จางเป็นสีเทาแทบมองไม่เห็น
        if visible_set is not None and row["province_name_th"] not in visible_set:
            return {"fillColor":"#EDEDED","color":"#DADADA","weight":0.4,"fillOpacity":0.18}
        color = tier_color(row["tier"]) if row["passed_gate"] else "#F5B5B5"
        if name == sel_en:
            return {"fillColor": color, "color":"#0A1628","weight":3.2,"fillOpacity":0.92}
        return {"fillColor": color, "color":"#777","weight":0.5,
                "fillOpacity":0.45 if row["passed_gate"] else 0.25}

    def hl_fn(feat):
        return {"weight":2.5,"color":"#0A1628","fillOpacity":0.75}

    tooltip = folium.GeoJsonTooltip(
        fields=["province_th","gate_status_th","overall_score","grade"],
        aliases=["จังหวัด","Gate Criteria","คะแนนรวม","Grade"],
        localize=True, sticky=False,
        style="""
            background-color:#0A1628;color:white;font-family:'Sarabun',sans-serif;
            font-size:16px;font-weight:600;padding:10px 16px;border-radius:10px;
            border:2px solid #1A9B6C;line-height:1.8;
        """,
        max_width=230,
    )
    popup = folium.GeoJsonPopup(
        fields=["province_th","gate_status_th","overall_score","grade"],
        aliases=["🏙️ จังหวัด","🔒 Gate Criteria","⭐ คะแนนรวม","Grade"],
        localize=True,
        style="font-family:'Sarabun',sans-serif;font-size:15px;line-height:1.9;min-width:200px;",
        max_width=260,
    )

    folium.GeoJson(geo_enriched, style_function=style_fn, highlight_function=hl_fn,
                   tooltip=tooltip, popup=popup).add_to(m)

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
# GATE CARD
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
# 6D CARD
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
      <div class="panel-title">📊 6D Assessment</div>
      <div style="font-size:1.05rem;color:#555;margin-bottom:10px">
        อันดับ <b>#{rank}</b> จาก {passed_total} จังหวัดที่ผ่าน Gate
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
      <div class="score-label">คะแนนรวม (Overall Score)</div>
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
            <div style="width:{max(pct,2)}%;background:{color};height:100%;border-radius:8px;
                        transition:width .4s ease"></div>
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


def render_welcome(df_gate, df_passed):
    n_pass = (df_gate["gate_status"]=="PASS").sum()
    st.markdown(f"""
    <div class="welcome-box">
      <div style="font-size:3.2rem;margin-bottom:12px">🗺️</div>
      <div style="font-size:1.4rem;font-weight:800;color:#0A1628;margin-bottom:10px">
        เลือกจังหวัดเพื่อดูผล Gate Criteria และ 6D Assessment พร้อมกัน
      </div>
      <div style="font-size:1.1rem;color:#555;line-height:1.9">
        เลือกจากช่อง Dropdown ด้านซ้าย หรือคลิก/ชี้เม้าส์บนแผนที่<br>
        ผ่าน Gate ทั้งหมด <b>{n_pass} / 77</b> จังหวัด · มีคะแนน 6D <b>{len(df_passed)}</b> จังหวัด
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:18px">🏆 Top 5 จังหวัด (6D Score)</div>',
                unsafe_allow_html=True)
    top5 = df_passed.sort_values("overall_score", ascending=False).head(5)
    clicked = None
    for _, row in top5.iterrows():
        tc = tier_color(row["tier"])
        gc = GRADE_COLOR.get(str(row["grade"]).strip(),"#888")
        col_info, col_btn = st.columns([3,1])
        with col_info:
            st.markdown(f"""
            <div style="padding:10px 4px;border-bottom:1px solid #E8EEF4">
              <div style="font-size:1.18rem;font-weight:700;color:#0A1628">
                #{int(row['rank_overall'])} {row['province_name_th']}
                <span style="font-size:1.02rem;color:#888;font-weight:400"> {row['province_name_en']}</span>
              </div>
              <div style="margin-top:4px">
                <span style="font-size:1.35rem;font-weight:800;color:{tc}">{row['overall_score']:.2f}</span>
                <span style="background:{gc};color:white;padding:3px 11px;border-radius:12px;
                             font-size:1rem;font-weight:700;margin-left:8px">Grade {row['grade']}</span>
              </div>
            </div>""", unsafe_allow_html=True)
        with col_btn:
            if st.button("เลือก", key=f"top5_{row['province_name_th']}", use_container_width=True):
                clicked = row["province_name_th"]
    return clicked


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
# MAIN
# ────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="topnav">
      <div>
        <div class="topnav-title">🗺️ Data Center Site Selection · Thailand</div>
        <div class="topnav-sub">Gate Criteria + 6D Assessment แสดงพร้อมกัน · 77 จังหวัด</div>
      </div>
    </div>""", unsafe_allow_html=True)

    try:
        df_gate = load_gate()
        df_6d   = load_6d()
        geo     = load_geo()
    except FileNotFoundError as e:
        st.error(f"❌ ไม่พบไฟล์: {e}"); st.stop()

    df_passed = df_6d[df_6d["passed_gate"]].copy()

    if "selected"     not in st.session_state: st.session_state.selected     = None
    if "compare_list" not in st.session_state: st.session_state.compare_list = []

    col_left, col_map = st.columns([1.8, 6.0])

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
            <div style="font-size:.92rem;color:#555">ผ่าน Gate Criteria</div>
          </div>
          <div style="flex:1;background:#FFF0F0;border-radius:10px;padding:12px;text-align:center">
            <div style="font-size:1.6rem;font-weight:800;color:#E04040">{n_fail}</div>
            <div style="font-size:.92rem;color:#555">ไม่ผ่าน</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">คะแนนขั้นต่ำ (6D)</div>', unsafe_allow_html=True)
        min_score = st.slider("", 0, 80, 0, key="score_slider", label_visibility="collapsed")

        eec_only   = st.checkbox("EEC Zone เท่านั้น", key="eec_cb")
        strat_only = st.checkbox("Strategic Digital Province เท่านั้น", key="strat_cb")

        if st.button("🔄 รีเซ็ตตัวกรอง", use_container_width=True, key="reset_btn"):
            st.session_state.selected = None
            st.session_state.compare_list = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### ⚖️ เปรียบเทียบจังหวัด (เฉพาะที่ผ่าน Gate)")
        prov_list = df_passed.sort_values("overall_score", ascending=False)["province_name_th"].tolist()
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

    # ═══════ CENTER — MAP ═══════
    with col_map:
        df_filtered = df_6d.merge(df_gate[["province_name_th","gate_status"]], on="province_name_th", how="left")
        if gate_filter == "✅ ผ่าน Gate Criteria":
            df_filtered = df_filtered[df_filtered["gate_status"]=="PASS"]
        elif gate_filter == "❌ ไม่ผ่าน Gate Criteria":
            df_filtered = df_filtered[df_filtered["gate_status"]=="FAIL"]
        df_filtered = df_filtered[df_filtered["overall_score"].fillna(0) >= min_score]
        if eec_only:   df_filtered = df_filtered[df_filtered["EEC"]]
        if strat_only: df_filtered = df_filtered[df_filtered["Strategic"]]

        st.markdown(
            f'<div style="font-size:1.02rem;color:#888;margin-bottom:6px">'
            f'🗺️ แสดง <b>{len(df_filtered)}</b> จาก 77 จังหวัด · '
            f'คลิกบนแผนที่ หรือเลือกจาก Dropdown เพื่อดูผลทั้ง 2 ส่วน</div>',
            unsafe_allow_html=True)

        visible_set = set(df_filtered["province_name_th"].tolist())
        m = build_map(df_6d, geo, st.session_state.selected, visible_set=visible_set)
        map_data = st_folium(m, width="100%", height=440,
                             key="main_map", returned_objects=["last_object_clicked_popup"])

        if map_data and map_data.get("last_object_clicked_popup"):
            popup_text = map_data["last_object_clicked_popup"] or ""
            for th in df_6d["province_name_th"].tolist():
                if th in popup_text:
                    if st.session_state.selected != th:
                        st.session_state.selected = th
                        st.rerun()

        # ═══════ ผลลัพธ์ — อยู่ใต้แผนที่ในคอลัมน์เดียวกัน ═══════
        st.markdown("---")
        sel = st.session_state.selected
        if sel and sel in df_gate["province_name_th"].values:
            gate_row = df_gate[df_gate["province_name_th"]==sel].iloc[0]
            d6_row   = df_6d[df_6d["province_name_th"]==sel].iloc[0]

            st.markdown(f"""
            <div style="font-size:1.6rem;font-weight:800;color:#0A1628;margin-bottom:4px">
              📍 {sel} <span style="font-size:1.05rem;color:#888;font-weight:400">{gate_row['province_name_en']} · {gate_row['region']}</span>
            </div>""", unsafe_allow_html=True)

            col_gate, col_6d = st.columns(2)
            with col_gate:
                render_gate_card(gate_row)
            with col_6d:
                render_6d_card(d6_row, len(df_passed))
        else:
            clicked = render_welcome(df_gate, df_passed)
            if clicked:
                st.session_state.selected = clicked
                st.rerun()

    st.markdown("""
    <div style="background:#F0F7FF;border-radius:8px;padding:12px 20px;margin-top:16px;
                border-left:4px solid #2E75B6;font-size:1.04rem;color:#333">
      💡 <b>แนวทางการใช้งาน:</b> เลือกจังหวัดเพื่อดูผล <b>Gate Criteria</b> และ <b>6D Assessment</b> พร้อมกันด้านล่าง
      &nbsp;|&nbsp; พลังงาน 35% + น้ำ 20% + บุคลากร 20% + BOI 7.5% + นิคม 7.5% + ความเสี่ยง 10%
      &nbsp;|&nbsp; เกณฑ์ Gate ผ่าน: ≥ 3 ใน 6 ข้อ
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
