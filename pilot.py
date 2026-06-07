"""
Thailand Data Center Site Suitability — PILOT (3 provinces)
ระยอง · ลำพูน · นครราชสีมา
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json, os

# ────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="DC Site Selection | Pilot",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────────
# CSS
# ────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 0rem; padding-bottom: 0.5rem;}

.topnav {
    background: #0A1628;
    color: white;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #1A9B6C;
    margin-bottom: 0;
}
.topnav-title {font-size: 1rem; font-weight: 700; color: #fff; letter-spacing:.5px}
.topnav-links {display:flex; gap:18px; font-size:.85rem; color:#9DC3E6; cursor:pointer}

.section-header {
    font-size:.72rem; font-weight:700; color:#1A9B6C;
    text-transform:uppercase; letter-spacing:.08em;
    margin-bottom:6px; margin-top:10px;
}

.filter-panel {
    background:#F5F8FC; border-radius:10px;
    padding:14px 16px; border:1px solid #D0DFF0;
}

.score-box {
    background: linear-gradient(135deg,#0D2137 0%,#1A3A5C 100%);
    border-radius:12px; padding:16px 20px;
    margin-bottom:10px; border:1px solid #2E75B6;
}
.score-big {font-size:3rem; font-weight:800; color:#fff; line-height:1}
.score-label {font-size:.72rem; color:#9DC3E6; margin-bottom:4px; text-transform:uppercase; letter-spacing:.06em}

.gate-pass   {display:inline-block; background:#1A9B6C; color:white; padding:4px 14px; border-radius:6px; font-size:.82rem; font-weight:700;}
.gate-review {display:inline-block; background:#FFC000; color:#000;  padding:4px 14px; border-radius:6px; font-size:.82rem; font-weight:700;}
.gate-no     {display:inline-block; background:#E04040; color:white; padding:4px 14px; border-radius:6px; font-size:.82rem; font-weight:700;}

.chip-green  {background:#E6F7EF; color:#1A9B6C; border:1px solid #1A9B6C; padding:3px 10px; border-radius:12px; font-size:.78rem; margin:2px; display:inline-block}
.chip-red    {background:#FFF0F0; color:#E04040; border:1px solid #E04040; padding:3px 10px; border-radius:12px; font-size:.78rem; margin:2px; display:inline-block}
.chip-orange {background:#FFF8E6; color:#E07B00; border:1px solid #E07B00; padding:3px 10px; border-radius:12px; font-size:.78rem; margin:2px; display:inline-block}

.welcome-box {
    background: linear-gradient(135deg,#F0F7FF 0%,#E6F4FF 100%);
    border-radius:14px; padding:36px 28px; text-align:center;
    border:2px dashed #9DC3E6; margin-top:8px;
}
.welcome-icon {font-size:3rem; margin-bottom:12px}
.welcome-title {font-size:1.15rem; font-weight:700; color:#0A1628; margin-bottom:8px}
.welcome-desc  {font-size:.88rem; color:#555; line-height:1.6}

.province-card {
    background:white; border-radius:10px; padding:12px 14px;
    border:1px solid #D0DFF0; cursor:pointer;
    transition: all .2s;
}
.province-card:hover {border-color:#1A9B6C; box-shadow:0 2px 8px rgba(26,155,108,.15)}

.feat-card {
    background:#F5F8FC; border-radius:10px; padding:14px;
    border-left:4px solid #1A9B6C; text-align:center;
}
.feat-icon  {font-size:1.8rem; margin-bottom:6px}
.feat-title {font-weight:700; color:#0A1628; font-size:.9rem}
.feat-desc  {font-size:.78rem; color:#555; margin-top:4px; line-height:1.4}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# CONSTANTS
# ────────────────────────────────────────────────
BASE      = os.path.dirname(__file__)
DATA_CSV  = os.path.join(BASE, "data", "province_scores.csv")
GEO_FILE  = os.path.join(BASE, "thailand.json")

PILOT_TH  = ["ระยอง", "ลำพูน", "นครราชสีมา"]
PILOT_EN  = {"ระยอง":"Rayong", "ลำพูน":"Lamphun", "นครราชสีมา":"Nakhon Ratchasima"}
PILOT_GEO = {"ระยอง":"Rayong", "ลำพูน":"Lamphun", "นครราชสีมา":"Nakhon Ratchasima"}

DIM_KEYS   = ["energy_score","water_score","talent_score","business_score","infrastructure_score","risk_score"]
DIM_MAX    = {"energy_score":35,"water_score":20,"talent_score":20,"business_score":7.5,"infrastructure_score":7.5,"risk_score":10}
DIM_LABELS = {"energy_score":"⚡ Energy","water_score":"💧 Water","talent_score":"🎓 Talent",
              "business_score":"🏢 Business","infrastructure_score":"🏭 Infrastructure","risk_score":"🛡️ Risk"}
DIM_COLORS = {"energy_score":"#1A9B6C","water_score":"#2E75B6","talent_score":"#7B4FBF",
              "business_score":"#E07B00","infrastructure_score":"#1F7A8C","risk_score":"#C0392B"}

TIER_FILL  = {"Tier 1 – Prime":"#1A9B6C","Tier 2 – Strong":"#5BB8A4",
              "Tier 3 – Moderate":"#F0C040","Tier 4 – Emerging":"#BBBBBB"}
GRADE_COLOR = {"A":"#1A9B6C","B":"#2E75B6","C":"#FFC000","D":"#E04040"}
GATE_HTML   = {"Recommended":"<span class='gate-pass'>✅ Gate Pass</span>",
               "Under Review":"<span class='gate-review'>⏳ Under Review</span>",
               "Not Recommended":"<span class='gate-no'>❌ Not Recommended</span>"}

PILOT_COORDS = {"ระยอง":(12.68,101.28), "ลำพูน":(18.58,99.00), "นครราชสีมา":(14.97,102.10)}

# ────────────────────────────────────────────────
# DATA
# ────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(DATA_CSV, encoding="utf-8-sig")
    df["EEC"]       = df["EEC"].astype(bool)
    df["Strategic"] = df["Strategic"].astype(bool)
    # เติม _pct ถ้ายังไม่มี
    for k, mx in DIM_MAX.items():
        if f"{k}_pct" not in df.columns:
            df[f"{k}_pct"] = (df[k] / mx * 100).round(1)
    return df

@st.cache_data
def load_all_provinces():
    """โหลด 77 จังหวัดตามลำดับจาก CSV"""
    df = pd.read_csv(DATA_CSV, encoding="utf-8-sig")
    return df["province_name_th"].dropna().tolist()

@st.cache_data
def load_geo():
    with open(GEO_FILE) as f:
        return json.load(f)

# ────────────────────────────────────────────────
# MAP
# ────────────────────────────────────────────────
def build_map(df_all, geo, selected_th):
    m = folium.Map(location=[13.5, 101.0], zoom_start=6,
                   tiles="CartoDB positron", prefer_canvas=True)

    # Build lookup: EN name → pilot row
    pilot_en_lookup = {row["province_name_en"]: row
                       for _, row in df_all[df_all["province_name_th"].isin(PILOT_TH)].iterrows()}

    # EN name of selected province (if any)
    sel_en = PILOT_GEO.get(selected_th) if selected_th else None

    def style_fn(feat):
        name = feat["properties"]["name"]
        # Selected province → bright highlight
        if name == sel_en:
            row   = pilot_en_lookup[name]
            color = TIER_FILL.get(row["tier"], "#1A9B6C")
            return {"fillColor": color, "color": "#0A1628", "weight": 3.0, "fillOpacity": 0.90}
        # Other pilot provinces → subtle tint (no text/marker)
        if name in pilot_en_lookup and selected_th is None:
            return {"fillColor": "#C8E6C9", "color": "#888", "weight": 1.0, "fillOpacity": 0.35}
        # All other provinces → light gray
        return {"fillColor": "#E4ECF5", "color": "#BBBBBB", "weight": 0.4, "fillOpacity": 0.35}

    def hl_fn(feat):
        return {"weight": 2.5, "color": "#2E75B6", "fillOpacity": 0.6}

    folium.GeoJson(
        geo, style_function=style_fn, highlight_function=hl_fn,
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["จังหวัด:"]),
    ).add_to(m)

    # Marker เฉพาะจังหวัดที่เลือก เท่านั้น
    if selected_th and selected_th in PILOT_COORDS:
        lat, lon = PILOT_COORDS[selected_th]
        row = df_all[df_all["province_name_th"] == selected_th].iloc[0]
        popup_html = f"""
        <div style="font-family:sans-serif;min-width:210px">
          <b style="font-size:1rem;color:#0A1628">{selected_th}</b>&nbsp;
          <span style="color:#888;font-size:.8rem">{PILOT_EN[selected_th]}</span>
          <hr style="margin:5px 0">
          <div style="font-size:1.5rem;font-weight:800;color:#1A9B6C">{row['overall_score']:.2f}</div>
          <div style="font-size:.78rem;color:#555;margin-bottom:4px">Overall Score</div>
          <span style="background:{TIER_FILL.get(row['tier'],'#888')};color:white;
                       padding:2px 10px;border-radius:12px;font-size:.78rem;font-weight:700">
            {row['tier']}
          </span>&nbsp;
          <span style="font-size:.78rem;color:#333">Grade <b>{row['grade']}</b></span>
        </div>"""
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"★ {selected_th}  {row['overall_score']:.2f}",
            icon=folium.Icon(color="darkgreen", icon="star"),
        ).add_to(m)

    # Legend (แสดงเฉพาะเมื่อมีการเลือก)
    if selected_th:
        row = df_all[df_all["province_name_th"] == selected_th].iloc[0]
        tier_color = TIER_FILL.get(row["tier"], "#888")
        legend = f"""
        <div style="position:fixed;bottom:24px;left:24px;z-index:1000;background:white;
                    padding:10px 14px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);
                    font-family:sans-serif;font-size:.82rem">
          <b style="color:#0A1628">จังหวัดที่เลือก</b><br>
          <span style="color:{tier_color}">■</span>
          <b>{selected_th}</b> · {row['tier']}<br>
          <span style="font-size:.75rem;color:#888">Overall Score: {row['overall_score']:.2f}</span>
        </div>"""
    else:
        legend = """
        <div style="position:fixed;bottom:24px;left:24px;z-index:1000;background:white;
                    padding:10px 14px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);
                    font-family:sans-serif;font-size:.82rem;color:#555">
          <b style="color:#0A1628">แผนที่จังหวัดไทย</b><br>
          เลือกจังหวัดจาก Dropdown<br>เพื่อ Highlight บนแผนที่
        </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m

# ────────────────────────────────────────────────
# SCORECARD (right panel)
# ────────────────────────────────────────────────
def render_scorecard(row):
    th    = row["province_name_th"]
    en    = row["province_name_en"]
    score = row["overall_score"]
    grade = row["grade"]
    tier  = row["tier"]
    gate  = row["gate_status"]
    rank  = row["rank_overall"]

    tier_color  = TIER_FILL.get(tier, "#888")
    grade_color = GRADE_COLOR.get(grade, "#888")

    # Header row: province name + gate badge
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
      <div>
        <div style="font-size:.68rem;color:#888;text-transform:uppercase;letter-spacing:.08em">Province Scorecard</div>
        <div style="font-size:1.7rem;font-weight:800;color:#0A1628;line-height:1.1">{th}</div>
        <div style="font-size:.82rem;color:#555">{en} · อันดับ <b>#{rank}</b> จาก 77 จังหวัด</div>
      </div>
      <div style="text-align:right;padding-top:4px">
        {GATE_HTML.get(gate,'')}
      </div>
    </div>""", unsafe_allow_html=True)

    # Score + Tier box
    st.markdown(f"""
    <div class="score-box">
      <div class="score-label">Overall Score</div>
      <div style="display:flex;align-items:flex-end;gap:14px;flex-wrap:wrap">
        <div class="score-big">{score:.2f}</div>
        <div style="padding-bottom:6px">
          <span style="background:{tier_color};color:white;padding:4px 13px;border-radius:20px;
                       font-size:.82rem;font-weight:700;display:inline-block">{tier}</span><br>
          <span style="background:{grade_color};color:white;padding:2px 10px;border-radius:12px;
                       font-size:.78rem;font-weight:700;display:inline-block;margin-top:5px">Grade {grade}</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # EEC / Strategic badges
    badges = []
    if row["EEC"]:
        badges.append("✅ EEC Zone")
    if row["Strategic"]:
        badges.append("🌐 Strategic Digital Province")
    if badges:
        badge_html = "&nbsp;".join([f'<span class="chip-green">{b}</span>' for b in badges])
        st.markdown(f'<div style="margin-bottom:8px">{badge_html}</div>', unsafe_allow_html=True)

    # Dimension score bars
    st.markdown('<div class="section-header">คะแนนรายมิติ (% จากคะแนนสูงสุด)</div>', unsafe_allow_html=True)
    for k in DIM_KEYS:
        pct   = row[f"{k}_pct"]
        raw   = row[k]
        mx    = DIM_MAX[k]
        color = DIM_COLORS[k]
        label = DIM_LABELS[k]
        bar_w = max(pct, 3)
        st.markdown(f"""
        <div style="margin-bottom:7px">
          <div style="display:flex;justify-content:space-between;margin-bottom:2px">
            <span style="font-size:.83rem;font-weight:600;color:#222">{label}</span>
            <span style="font-size:.83rem;font-weight:700;color:{color}">{pct:.1f}</span>
          </div>
          <div style="background:#E4ECF5;border-radius:6px;height:10px;overflow:hidden">
            <div style="width:{bar_w}%;background:{color};height:100%;border-radius:6px"></div>
          </div>
          <div style="font-size:.68rem;color:#999;text-align:right">{raw:.2f} / {mx}</div>
        </div>""", unsafe_allow_html=True)

    # Strengths / weaknesses
    st.markdown('<div class="section-header">จุดแข็ง / จุดอ่อน</div>', unsafe_allow_html=True)
    strengths  = [s.strip() for s in str(row.get("strengths","")).split(",") if s.strip() and s.strip() != "nan"]
    weaknesses = [w.strip() for w in str(row.get("weaknesses","")).split(",") if w.strip() and w.strip() != "nan"]

    if strengths:
        chips = " ".join([f'<span class="chip-green">💪 {s}</span>' for s in strengths])
        st.markdown(f'<div><b style="font-size:.72rem;color:#1A9B6C">จุดแข็ง</b><br>{chips}</div>', unsafe_allow_html=True)
    if weaknesses:
        chips = " ".join([f'<span class="chip-red">⚠️ {w}</span>' for w in weaknesses])
        st.markdown(f'<div style="margin-top:4px"><b style="font-size:.72rem;color:#E04040">จุดอ่อน</b><br>{chips}</div>', unsafe_allow_html=True)

    note = str(row.get("analyst_note","")).strip()
    if note and note != "nan":
        st.markdown(f'<div style="margin-top:6px"><span class="chip-orange">📝 {note}</span></div>',
                    unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:8px">
      <span class="chip-orange">⚠️ ข้อจำกัด: Risk ใช้ข้อมูล GIS เบื้องต้น · Infrastructure ใช้จำนวน DC</span>
    </div>""", unsafe_allow_html=True)

    # Raw data
    with st.expander("📋 ข้อมูลดิบ (Raw Data)"):
        raw_data = {
            "พลังงานติดตั้งรวม (MW)":        f"{row['installed_mw']:,.0f}",
            "สัดส่วนพลังงานหมุนเวียน":       f"{row['renewable_pct']*100:.1f}%",
            "ความจุกักเก็บน้ำ (ล้าน ลบ.ม.)": f"{row['storage_mcm']:,.0f}",
            "มหาวิทยาลัย":                   f"{int(row['univ_count'])} แห่ง",
            "วิทยาลัยอาชีวศึกษา":            f"{int(row['voc_count'])} แห่ง",
            "ประชากรวัยทำงาน (15-59 ปี)":    f"{row['working_age']:,.0f} คน",
            "โครงการ BOI (Data Center)":      f"{int(row['boi_projects'])} โครงการ",
            "Data Center ปัจจุบัน":           f"{int(row['dc_count'])} แห่ง",
            "EEC Zone":                       "✅ ใช่" if row["EEC"] else "❌ ไม่ใช่",
            "Strategic Digital Province":     "✅ ใช่" if row["Strategic"] else "❌ ไม่ใช่",
        }
        st.table(pd.DataFrame(list(raw_data.items()), columns=["ตัวชี้วัด","ค่า"]))


def render_welcome_panel():
    """แสดงก่อนที่ผู้ใช้เลือกจังหวัด"""
    st.markdown("""
    <div class="welcome-box">
      <div class="welcome-icon">🗺️</div>
      <div class="welcome-title">เลือกจังหวัดเพื่อดู Scorecard</div>
      <div class="welcome-desc">
        คลิก Marker บนแผนที่<br>
        หรือเลือกจังหวัดจากตาราง / Dropdown ด้านซ้าย<br><br>
        <span style="color:#1A9B6C;font-weight:600">Pilot 3 จังหวัด:</span><br>
        ระยอง · ลำพูน · นครราชสีมา
      </div>
    </div>""", unsafe_allow_html=True)

    # Province quick-pick cards
    st.markdown('<div class="section-header" style="margin-top:14px">เลือกจังหวัดด่วน</div>',
                unsafe_allow_html=True)

    # We return the button clicks — handled outside
    c1, c2, c3 = st.columns(3)
    clicked = None
    province_info = {
        "ระยอง":       ("🏭","84.58","Tier 1 – Prime","Grade A","#1A9B6C"),
        "ลำพูน":       ("🏔️","74.73","Tier 1 – Prime","Grade B","#2E75B6"),
        "นครราชสีมา":  ("🏛️","68.19","Tier 2 – Strong","Grade B","#5BB8A4"),
    }
    for col, th in zip([c1, c2, c3], PILOT_TH):
        icon, score, tier, grade, color = province_info[th]
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:12px;border:1px solid #D0DFF0;
                        text-align:center;margin-bottom:4px">
              <div style="font-size:1.6rem">{icon}</div>
              <div style="font-weight:700;color:#0A1628;font-size:.95rem">{th}</div>
              <div style="font-size:1.3rem;font-weight:800;color:{color}">{score}</div>
              <div style="font-size:.72rem;color:#888">{tier}<br>{grade}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"เลือก {th}", key=f"quick_{th}", use_container_width=True):
                clicked = th
    return clicked


# ────────────────────────────────────────────────
# RADAR — เปรียบเทียบ
# ────────────────────────────────────────────────
def render_radar(df_pilot):
    colors = ["#1A9B6C","#2E75B6","#E07B00"]
    fig = go.Figure()
    labels = [DIM_LABELS[k] for k in DIM_KEYS]
    for i, (_, row) in enumerate(df_pilot.iterrows()):
        vals = [row[f"{k}_pct"] for k in DIM_KEYS] + [row[f"{DIM_KEYS[0]}_pct"]]
        lbls = labels + [labels[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=lbls, fill="toself",
            name=row["province_name_th"],
            line_color=colors[i % len(colors)],
            opacity=0.85,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100],
                                   tickfont=dict(size=8), gridcolor="#DDD"),
                   angularaxis=dict(tickfont=dict(size=9))),
        showlegend=True,
        legend=dict(orientation="h", y=-0.18, font=dict(size=10)),
        height=280,
        margin=dict(l=24,r=24,t=16,b=56),
        paper_bgcolor="#F5F8FC",
    )
    return fig


# ────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────
def main():
    # ── Top Navbar ──
    st.markdown("""
    <div class="topnav">
      <div class="topnav-title">🗺️ Data Center Site Selection</div>
      <div class="topnav-links">
        <span>📖 คู่มือการใช้งาน</span>
        <span>📤 ส่งออกข้อมูล</span>
        <span>👤 ผู้ใช้งาน</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Load data ──
    try:
        df_all        = load_data()
        geo           = load_geo()
        all_provinces = load_all_provinces()
    except FileNotFoundError as e:
        st.error(f"❌ ไม่พบไฟล์: {e}")
        st.stop()

    df_pilot = df_all[df_all["province_name_th"].isin(PILOT_TH)].copy()

    # ── Session state: selected = None หมายถึงยังไม่ได้เลือก ──
    if "selected" not in st.session_state:
        st.session_state.selected = None
    if "tier_filter" not in st.session_state:
        st.session_state.tier_filter = "ทั้งหมด"
    if "score_min" not in st.session_state:
        st.session_state.score_min = 0

    # ──────── 3-COLUMN LAYOUT ────────
    col_left, col_map, col_right = st.columns([2.0, 4.2, 2.6])

    # ═══════ LEFT PANEL ═══════
    with col_left:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown("#### 🔎 ค้นหาและกรองข้อมูล")
        st.caption("Pilot: 3 จังหวัด")

        # Province dropdown — 77 จังหวัด พร้อม label แสดง Pilot
        def fmt_option(prov):
            if prov == "— กรุณาเลือกจังหวัด —":
                return prov
            if prov in PILOT_TH:
                return f"★ {prov}  (มีข้อมูล)"
            return prov

        province_options = ["— กรุณาเลือกจังหวัด —"] + all_provinces
        current_idx = 0
        if st.session_state.selected in all_provinces:
            current_idx = all_provinces.index(st.session_state.selected) + 1

        sel_dd = st.selectbox(
            "เลือกจังหวัด (77 จังหวัด)",
            options=province_options,
            index=current_idx,
            format_func=fmt_option,
            key="prov_dd",
        )
        if sel_dd != "— กรุณาเลือกจังหวัด —":
            st.session_state.selected = sel_dd

        st.markdown("---")
        st.markdown('<div class="section-header">Tier</div>', unsafe_allow_html=True)
        tier_opts = ["ทั้งหมด", "Tier 1 – Prime", "Tier 2 – Strong", "Tier 3 – Moderate", "Constraint"]
        tier_sel = st.radio("", tier_opts, horizontal=True,
                            label_visibility="collapsed", key="tier_radio")
        st.session_state.tier_filter = tier_sel

        st.markdown('<div class="section-header">คะแนนขั้นต่ำ</div>', unsafe_allow_html=True)
        min_score = st.slider("", 0, 100, st.session_state.score_min,
                              key="score_slider", label_visibility="collapsed")
        st.session_state.score_min = min_score

        st.markdown('<div class="section-header">มิติข้อมูล (เปิด/ปิดการพิจารณา)</div>',
                    unsafe_allow_html=True)
        dim_icons = {
            "energy_score":         "⚡ พลังงาน",
            "water_score":          "💧 น้ำ",
            "talent_score":         "🎓 บุคลากร",
            "business_score":       "🏢 ธุรกิจ",
            "infrastructure_score": "🏭 โครงสร้างพื้นฐาน",
            "risk_score":           "🛡️ ความเสี่ยง",
        }
        for k, lbl in dim_icons.items():
            c1, c2 = st.columns([3,1])
            with c1:
                st.markdown(f'<small style="color:#333">{lbl}</small>', unsafe_allow_html=True)
            with c2:
                st.toggle("", value=True, key=f"tog_{k}", label_visibility="collapsed")

        if st.button("🔄 รีเซ็ตตัวกรอง", use_container_width=True):
            st.session_state.tier_filter  = "ทั้งหมด"
            st.session_state.score_min    = 0
            st.session_state.selected     = None
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Radar comparison (always visible)
        st.markdown("---")
        st.markdown("##### ⚖️ เปรียบเทียบ 3 จังหวัด")
        st.plotly_chart(render_radar(df_pilot), use_container_width=True)

    # ═══════ CENTER — MAP ═══════
    with col_map:
        st.markdown(
            '<div style="font-size:.75rem;color:#888;margin-bottom:4px">'
            '🗺️ คลิก <b>Marker</b> บนแผนที่เพื่อเลือกจังหวัดและดู Scorecard</div>',
            unsafe_allow_html=True
        )

        m        = build_map(df_all, geo, st.session_state.selected)
        map_data = st_folium(m, width="100%", height=510,
                             returned_objects=["last_object_clicked_popup"])

        # Detect click from map popup
        if map_data and map_data.get("last_object_clicked_popup"):
            popup_text = map_data["last_object_clicked_popup"] or ""
            for th in PILOT_TH:
                if th in popup_text:
                    if st.session_state.selected != th:
                        st.session_state.selected = th
                        st.rerun()

        # แสดงสรุปเฉพาะจังหวัดที่เลือก
        sel = st.session_state.selected
        if sel and sel in PILOT_TH:
            row_s = df_pilot[df_pilot["province_name_th"] == sel].iloc[0]
            tier_color  = TIER_FILL.get(row_s["tier"], "#888")
            grade_color = GRADE_COLOR.get(row_s["grade"], "#888")
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:14px 16px;
                        border:2px solid {tier_color};margin-top:4px">
              <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
                <div>
                  <div style="font-size:1.1rem;font-weight:800;color:#0A1628">{sel}
                    <span style="font-size:.8rem;font-weight:400;color:#888">
                      &nbsp;{row_s['province_name_en']}
                    </span>
                  </div>
                  <div style="font-size:.78rem;color:#555;margin-top:2px">
                    อันดับ <b>#{int(row_s['rank_overall'])}</b> จาก 77 จังหวัด
                  </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px">
                  <div style="text-align:center">
                    <div style="font-size:1.6rem;font-weight:800;color:{tier_color};line-height:1">{row_s['overall_score']:.2f}</div>
                    <div style="font-size:.68rem;color:#888">Overall</div>
                  </div>
                  <div style="display:flex;flex-direction:column;gap:4px">
                    <span style="background:{grade_color};color:white;padding:2px 10px;
                                 border-radius:10px;font-size:.78rem;font-weight:700;text-align:center">
                      Grade {row_s['grade']}
                    </span>
                    <span style="background:{tier_color};color:white;padding:2px 10px;
                                 border-radius:10px;font-size:.72rem;font-weight:600;text-align:center">
                      {row_s['tier']}
                    </span>
                  </div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
        elif sel and sel not in PILOT_TH:
            st.markdown(f"""
            <div style="background:#FFF8F0;border-radius:10px;padding:12px 16px;
                        border:1px dashed #E07B00;margin-top:4px;font-size:.85rem;color:#555">
              <b style="color:#E07B00">⚠️ {sel}</b> — ยังไม่มีข้อมูลใน Pilot Phase 1
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#F5F8FC;border-radius:10px;padding:12px 16px;
                        border:1px dashed #9DC3E6;margin-top:4px;font-size:.85rem;
                        color:#888;text-align:center">
              เลือกจังหวัดเพื่อดูข้อมูลสรุป
            </div>""", unsafe_allow_html=True)

    # ═══════ RIGHT — SCORECARD (เฉพาะเมื่อเลือกแล้ว) ═══════
    with col_right:
        sel = st.session_state.selected
        if sel and sel in PILOT_TH:
            # ✅ Pilot province — แสดง Scorecard เต็ม
            sel_row = df_pilot[df_pilot["province_name_th"] == sel].iloc[0]
            render_scorecard(sel_row)
        elif sel and sel not in PILOT_TH:
            # ⚠️ เลือกจังหวัดที่ยังไม่มีข้อมูล
            st.markdown(f"""
            <div style="background:#FFF8F0;border-radius:14px;padding:28px 24px;
                        border:2px dashed #E07B00;margin-top:8px;text-align:center">
              <div style="font-size:2rem;margin-bottom:8px">🔍</div>
              <div style="font-size:1.15rem;font-weight:700;color:#0A1628;margin-bottom:6px">
                {sel}
              </div>
              <div style="font-size:.88rem;color:#E07B00;font-weight:600;margin-bottom:10px">
                ⚠️ อยู่นอกเหนือ Pilot Phase 1
              </div>
              <div style="font-size:.83rem;color:#555;line-height:1.6">
                จังหวัดนี้ยังไม่มีข้อมูลในระบบ<br>
                จะเพิ่มใน Phase 2 (74 จังหวัดที่เหลือ)<br><br>
                <b>Pilot ปัจจุบันมีข้อมูล:</b>
              </div>
              <div style="margin-top:10px">
                {"".join([f'<div style="background:#E6F7EF;border-radius:8px;padding:6px 12px;margin:4px auto;width:fit-content;font-weight:600;color:#1A9B6C;cursor:pointer">★ {p}</div>' for p in PILOT_TH])}
              </div>
            </div>""", unsafe_allow_html=True)
            # ปุ่ม quick switch ไป pilot provinces
            st.markdown('<div style="margin-top:10px"></div>', unsafe_allow_html=True)
            for th in PILOT_TH:
                if st.button(f"★ ดูข้อมูล {th}", key=f"switch_{th}", use_container_width=True):
                    st.session_state.selected = th
                    st.rerun()
        else:
            # ยังไม่ได้เลือกเลย — Welcome panel
            clicked = render_welcome_panel()
            if clicked:
                st.session_state.selected = clicked
                st.rerun()

    # ──────── BOTTOM FEATURE CARDS ────────
    st.divider()
    feat_cols = st.columns(4)
    feats = [
        ("🔍","ค้นหาและเลือกพื้นที่",
         "ค้นหาจังหวัด กรองตาม Tier และคะแนนขั้นต่ำ คัดกรองพื้นที่ที่สนใจได้รวดเร็ว"),
        ("📊","เปรียบเทียบคะแนนรายมิติ",
         "Radar Chart 6 มิติ เปรียบเทียบจุดแข็งและจุดที่ต้องพัฒนาระหว่างจังหวัด"),
        ("🗺️","แสดงผลบนแผนที่เชิงโต้ตอบ",
         "แผนที่ Choropleth พร้อมระดับศักยภาพรายจังหวัด คลิก Marker เพื่อดูรายละเอียด"),
        ("📋","สนับสนุนการตัดสินใจเบื้องต้น",
         "สรุปคะแนนรวม จุดแข็ง จุดอ่อน และข้อจำกัดข้อมูล เพื่อการลงทุนอย่างมีข้อมูล"),
    ]
    for col, (icon, title, desc) in zip(feat_cols, feats):
        col.markdown(f"""
        <div class="feat-card">
          <div class="feat-icon">{icon}</div>
          <div class="feat-title">{title}</div>
          <div class="feat-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

    # ──────── BOTTOM TIP ────────
    st.markdown("""
    <div style="background:#F0F7FF;border-radius:8px;padding:10px 18px;margin-top:10px;
                border-left:4px solid #2E75B6;font-size:.85rem;color:#333">
      💡 <b>แนวทางการใช้งาน:</b>
      คลิก Marker บนแผนที่ หรือเลือกจังหวัดจาก Dropdown / ปุ่มด้านล่างตาราง
      เพื่อดู Scorecard รายมิติ จุดแข็ง และข้อมูลประกอบการตัดสินใจ
      &nbsp;|&nbsp; <b>Pilot Phase 1</b> · ระยอง · ลำพูน · นครราชสีมา · ข้อมูล: พ.ค. 2569
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
