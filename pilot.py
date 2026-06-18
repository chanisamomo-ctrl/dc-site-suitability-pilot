"""
Thailand Data Center Site Suitability Dashboard
ข้อมูล 77 จังหวัด | เกณฑ์ v2.0 | ข้อมูล: มิ.ย. 2569
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
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 0rem; padding-bottom: 0.5rem;}
.topnav {
    background:#0A1628; color:white; padding:10px 24px;
    display:flex; align-items:center; justify-content:space-between;
    border-bottom:2px solid #1A9B6C;
}
.topnav-title {font-size:1rem; font-weight:700; color:#fff; letter-spacing:.5px}
.topnav-links {display:flex; gap:18px; font-size:.85rem; color:#9DC3E6; cursor:pointer}
.section-header {
    font-size:.72rem; font-weight:700; color:#1A9B6C;
    text-transform:uppercase; letter-spacing:.08em;
    margin-bottom:6px; margin-top:10px;
}
.filter-panel {background:#F5F8FC; border-radius:10px; padding:14px 16px; border:1px solid #D0DFF0;}
.score-box {
    background:linear-gradient(135deg,#0D2137 0%,#1A3A5C 100%);
    border-radius:12px; padding:16px 20px; margin-bottom:10px; border:1px solid #2E75B6;
}
.score-big  {font-size:3rem; font-weight:800; color:#fff; line-height:1}
.score-label{font-size:.72rem; color:#9DC3E6; margin-bottom:4px; text-transform:uppercase; letter-spacing:.06em}
.gate-pass  {display:inline-block;background:#1A9B6C;color:white;padding:4px 14px;border-radius:6px;font-size:.82rem;font-weight:700;}
.gate-review{display:inline-block;background:#FFC000;color:#000; padding:4px 14px;border-radius:6px;font-size:.82rem;font-weight:700;}
.gate-no    {display:inline-block;background:#E04040;color:white;padding:4px 14px;border-radius:6px;font-size:.82rem;font-weight:700;}
.chip-green {background:#E6F7EF;color:#1A9B6C;border:1px solid #1A9B6C;padding:3px 10px;border-radius:12px;font-size:.78rem;margin:2px;display:inline-block}
.chip-red   {background:#FFF0F0;color:#E04040;border:1px solid #E04040;padding:3px 10px;border-radius:12px;font-size:.78rem;margin:2px;display:inline-block}
.chip-orange{background:#FFF8E6;color:#E07B00;border:1px solid #E07B00;padding:3px 10px;border-radius:12px;font-size:.78rem;margin:2px;display:inline-block}
.welcome-box {
    background:linear-gradient(135deg,#F0F7FF 0%,#E6F4FF 100%);
    border-radius:14px; padding:28px 24px; text-align:center;
    border:2px dashed #9DC3E6; margin-top:8px;
}
.feat-card {background:#F5F8FC;border-radius:10px;padding:14px;border-left:4px solid #1A9B6C;text-align:center;}
.feat-icon  {font-size:1.8rem;margin-bottom:6px}
.feat-title {font-weight:700;color:#0A1628;font-size:.9rem}
.feat-desc  {font-size:.78rem;color:#555;margin-top:4px;line-height:1.4}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# CONSTANTS
# ────────────────────────────────────────────────
BASE     = os.path.dirname(__file__)
DATA_CSV = os.path.join(BASE, "data", "province_scores.csv")
GEO_FILE = os.path.join(BASE, "thailand.json")

DIM_KEYS   = ["energy_score","water_score","talent_score","business_score","infrastructure_score","risk_score"]
DIM_MAX    = {"energy_score":35,"water_score":20,"talent_score":20,"business_score":7.5,"infrastructure_score":7.5,"risk_score":10}
DIM_LABELS = {"energy_score":"⚡ Energy","water_score":"💧 Water","talent_score":"🎓 Talent",
              "business_score":"🏢 Business","infrastructure_score":"🏭 Infrastructure","risk_score":"🛡️ Risk"}
DIM_COLORS = {"energy_score":"#1A9B6C","water_score":"#2E75B6","talent_score":"#7B4FBF",
              "business_score":"#E07B00","infrastructure_score":"#1F7A8C","risk_score":"#C0392B"}
TIER_FILL  = {"Tier 1 – Prime":"#1A9B6C","Tier 2 – Suitable":"#5BB8A4",
              "Tier 3 – Conditional":"#F0C040","Tier 4 – Not Recommended":"#BBBBBB"}
GRADE_COLOR= {"A":"#1A9B6C","B":"#2E75B6","C":"#FFC000","D":"#E04040"}
GATE_HTML  = {"Recommended":"<span class='gate-pass'>✅ Gate Pass</span>",
              "Under Review":"<span class='gate-review'>⏳ Under Review</span>",
              "Not Recommended":"<span class='gate-no'>❌ Not Recommended</span>"}

# ────────────────────────────────────────────────
# DATA
# ────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(DATA_CSV, encoding="utf-8-sig")
    df["EEC"]       = df["EEC"].astype(bool)
    df["Strategic"] = df["Strategic"].astype(bool)
    for k, mx in DIM_MAX.items():
        if f"{k}_pct" not in df.columns:
            df[f"{k}_pct"] = (df[k] / mx * 100).round(1)
    return df

@st.cache_data
def load_geo():
    with open(GEO_FILE) as f:
        return json.load(f)

# ────────────────────────────────────────────────
# MAP
# ────────────────────────────────────────────────
def build_map(df_all, geo, selected_th):
    m = folium.Map(location=[13.0, 101.5], zoom_start=6,
                   tiles="CartoDB positron", prefer_canvas=True)

    # lookup: EN name → row
    en_lookup = {}
    for _, row in df_all.iterrows():
        en = str(row["province_name_en"])
        if en == "Bangkok": en = "Bangkok Metropolis"
        en_lookup[en] = row

    sel_en = None
    if selected_th:
        r = df_all[df_all["province_name_th"] == selected_th]
        if len(r):
            sel_en = str(r.iloc[0]["province_name_en"])
            if sel_en == "Bangkok": sel_en = "Bangkok Metropolis"

    def style_fn(feat):
        name = feat["properties"]["name"]
        row  = en_lookup.get(name)
        if name == sel_en and row is not None:
            return {"fillColor": TIER_FILL.get(row["tier"],"#1A9B6C"),
                    "color":"#0A1628","weight":3.0,"fillOpacity":0.90}
        if row is not None:
            return {"fillColor": TIER_FILL.get(row["tier"],"#BBBBBB"),
                    "color":"#777","weight":0.5,"fillOpacity":0.45}
        return {"fillColor":"#E4ECF5","color":"#BBBBBB","weight":0.4,"fillOpacity":0.3}

    def hl_fn(feat):
        return {"weight":2.5,"color":"#0A1628","fillOpacity":0.7}

    folium.GeoJson(
        geo, style_function=style_fn, highlight_function=hl_fn,
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["จังหวัด:"]),
    ).add_to(m)

    # Marker เฉพาะจังหวัดที่เลือก
    if selected_th:
        r = df_all[df_all["province_name_th"] == selected_th]
        if len(r) and pd.notna(r.iloc[0].get("lat")) and pd.notna(r.iloc[0].get("lng")):
            row  = r.iloc[0]
            lat, lon = float(row["lat"]), float(row["lng"])
            popup_html = f"""
            <div style="font-family:sans-serif;min-width:210px">
              <b style="font-size:1rem;color:#0A1628">{selected_th}</b>&nbsp;
              <span style="color:#888;font-size:.8rem">{row['province_name_en']}</span>
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

    # Legend
    if selected_th:
        r = df_all[df_all["province_name_th"] == selected_th]
        if len(r):
            row = r.iloc[0]
            tc  = TIER_FILL.get(row["tier"],"#888")
            leg = f"""<div style="position:fixed;bottom:24px;left:24px;z-index:1000;background:white;
                        padding:10px 14px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);
                        font-family:sans-serif;font-size:.82rem">
                      <b style="color:#0A1628">จังหวัดที่เลือก</b><br>
                      <span style="color:{tc}">■</span> <b>{selected_th}</b> · {row['tier']}<br>
                      <span style="font-size:.75rem;color:#888">Overall: {row['overall_score']:.2f}</span>
                    </div>"""
    else:
        leg = """<div style="position:fixed;bottom:24px;left:24px;z-index:1000;background:white;
                    padding:10px 14px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);
                    font-family:sans-serif;font-size:.82rem">
                  <b style="color:#0A1628">ระดับศักยภาพ</b><br>
                  <span style="color:#1A9B6C">■</span> Tier 1 – Prime<br>
                  <span style="color:#5BB8A4">■</span> Tier 2 – Suitable<br>
                  <span style="color:#F0C040">■</span> Tier 3 – Conditional<br>
                  <span style="color:#BBBBBB">■</span> Tier 4 – Not Recommended
                </div>"""
    m.get_root().html.add_child(folium.Element(leg))
    return m

# ────────────────────────────────────────────────
# SCORECARD
# ────────────────────────────────────────────────
def render_scorecard(row):
    th    = row["province_name_th"]
    en    = row["province_name_en"]
    score = row["overall_score"]
    grade = str(row["grade"]).strip()
    tier  = row["tier"]
    gate  = row["gate_status"]
    rank  = int(row["rank_overall"])
    tc    = TIER_FILL.get(tier,"#888")
    gc    = GRADE_COLOR.get(grade,"#888")

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
      <div>
        <div style="font-size:.68rem;color:#888;text-transform:uppercase;letter-spacing:.08em">Province Scorecard</div>
        <div style="font-size:1.7rem;font-weight:800;color:#0A1628;line-height:1.1">{th}</div>
        <div style="font-size:.82rem;color:#555">{en} · อันดับ <b>#{rank}</b> จาก 77 จังหวัด</div>
      </div>
      <div style="padding-top:4px">{GATE_HTML.get(gate,'')}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
      <div class="score-label">Overall Score</div>
      <div style="display:flex;align-items:flex-end;gap:14px;flex-wrap:wrap">
        <div class="score-big">{score:.2f}</div>
        <div style="padding-bottom:6px">
          <span style="background:{tc};color:white;padding:4px 13px;border-radius:20px;
                       font-size:.82rem;font-weight:700;display:inline-block">{tier}</span><br>
          <span style="background:{gc};color:white;padding:2px 10px;border-radius:12px;
                       font-size:.78rem;font-weight:700;display:inline-block;margin-top:5px">Grade {grade}</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    badges = []
    if row["EEC"]:       badges.append("✅ EEC Zone")
    if row["Strategic"]: badges.append("🌐 Strategic Digital Province")
    if badges:
        st.markdown(" ".join([f'<span class="chip-green">{b}</span>' for b in badges]),
                    unsafe_allow_html=True)

    st.markdown('<div class="section-header">คะแนนรายมิติ (% จากคะแนนสูงสุด)</div>',
                unsafe_allow_html=True)
    for k in DIM_KEYS:
        pct   = float(row[f"{k}_pct"])
        raw_w = float(row[k])
        mx    = DIM_MAX[k]
        color = DIM_COLORS[k]
        label = DIM_LABELS[k]
        st.markdown(f"""
        <div style="margin-bottom:7px">
          <div style="display:flex;justify-content:space-between;margin-bottom:2px">
            <span style="font-size:.83rem;font-weight:600;color:#222">{label}</span>
            <span style="font-size:.83rem;font-weight:700;color:{color}">{pct:.1f}</span>
          </div>
          <div style="background:#E4ECF5;border-radius:6px;height:10px;overflow:hidden">
            <div style="width:{max(pct,2)}%;background:{color};height:100%;border-radius:6px"></div>
          </div>
          <div style="font-size:.68rem;color:#999;text-align:right">{raw_w:.2f} / {mx}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">จุดแข็ง / จุดอ่อน</div>', unsafe_allow_html=True)
    strengths  = [s.strip() for s in str(row.get("strengths","")).split(",") if s.strip() not in ("","nan","—")]
    weaknesses = [w.strip() for w in str(row.get("weaknesses","")).split(",") if w.strip() not in ("","nan","—")]
    if strengths:
        chips = " ".join([f'<span class="chip-green">💪 {s}</span>' for s in strengths])
        st.markdown(f'<div><b style="font-size:.72rem;color:#1A9B6C">จุดแข็ง</b><br>{chips}</div>',
                    unsafe_allow_html=True)
    if weaknesses:
        chips = " ".join([f'<span class="chip-red">⚠️ {w}</span>' for w in weaknesses])
        st.markdown(f'<div style="margin-top:4px"><b style="font-size:.72rem;color:#E04040">จุดอ่อน</b><br>{chips}</div>',
                    unsafe_allow_html=True)
    note = str(row.get("analyst_note","")).strip()
    if note and note != "nan":
        st.markdown(f'<div style="margin-top:6px"><span class="chip-orange">📝 {note}</span></div>',
                    unsafe_allow_html=True)

    with st.expander("📋 ข้อมูลดิบ"):
        raw_items = {
            "พลังงานติดตั้งรวม (MW)":         f"{float(row.get('installed_mw',0)):,.1f}",
            "ความจุกักเก็บน้ำ (ล้าน ลบ.ม.)":  f"{float(row.get('storage_mcm',0)):,.1f}",
            "มหาวิทยาลัย (วิทยาเขต)":         f"{int(row.get('univ_count',0))} แห่ง",
            "วิทยาลัยอาชีวศึกษา":             f"{int(row.get('voc_count',0))} แห่ง",
            "โครงการ BOI DC":                 f"{int(row.get('boi_projects',0))} โครงการ",
            "นิคมอุตสาหกรรม (IEAT)":          f"{int(row.get('ieat_count',0))} แห่ง",
            "DC IT Load (MW)":                 f"{float(row.get('dc_it_load_mw',0)):.1f}",
            "Risk Score (DB raw)":             f"{float(row.get('risk_raw',0)):.1f} / 100",
            "EEC Zone":                        "✅ ใช่" if row["EEC"] else "❌ ไม่ใช่",
            "Strategic Digital Province":      "✅ ใช่" if row["Strategic"] else "❌ ไม่ใช่",
        }
        st.table(pd.DataFrame(list(raw_items.items()), columns=["ตัวชี้วัด","ค่า"]))


def render_welcome_panel(df_all):
    st.markdown("""
    <div class="welcome-box">
      <div style="font-size:2.5rem;margin-bottom:8px">🗺️</div>
      <div style="font-size:1.1rem;font-weight:700;color:#0A1628;margin-bottom:6px">
        เลือกจังหวัดเพื่อดู Scorecard
      </div>
      <div style="font-size:.85rem;color:#555;line-height:1.6">
        คลิก <b>Marker</b> บนแผนที่ หรือเลือกจาก Dropdown ด้านซ้าย<br>
        ข้อมูลครบ <b>77 จังหวัด</b> · เกณฑ์ v2.0
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:14px">Top 5 จังหวัด</div>',
                unsafe_allow_html=True)
    top5 = df_all.head(5)
    clicked = None
    for _, row in top5.iterrows():
        tc = TIER_FILL.get(row["tier"],"#888")
        gc = GRADE_COLOR.get(str(row["grade"]).strip(),"#888")
        col_info, col_btn = st.columns([3,1])
        with col_info:
            st.markdown(f"""
            <div style="padding:6px 0;border-bottom:1px solid #EEE">
              <span style="font-weight:700;color:#0A1628">{row['province_name_th']}</span>
              <span style="color:#888;font-size:.8rem"> {row['province_name_en']}</span><br>
              <span style="font-size:1.1rem;font-weight:800;color:{tc}">{row['overall_score']:.2f}</span>
              <span style="background:{gc};color:white;padding:1px 7px;border-radius:8px;
                           font-size:.72rem;font-weight:700;margin-left:4px">Grade {row['grade']}</span>
            </div>""", unsafe_allow_html=True)
        with col_btn:
            if st.button("เลือก", key=f"top5_{row['province_name_th']}", use_container_width=True):
                clicked = row["province_name_th"]
    return clicked


# ────────────────────────────────────────────────
# RADAR COMPARE
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
                                   tickfont=dict(size=8), gridcolor="#DDD"),
                   angularaxis=dict(tickfont=dict(size=9))),
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
        height=270, margin=dict(l=24,r=24,t=16,b=60),
        paper_bgcolor="#F5F8FC",
    )
    return fig


# ────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="topnav">
      <div class="topnav-title">🗺️ Data Center Site Selection · Thailand</div>
      <div class="topnav-links">
        <span>📖 คู่มือการใช้งาน</span>
        <span>📤 ส่งออกข้อมูล</span>
        <span>👤 ผู้ใช้งาน</span>
      </div>
    </div>""", unsafe_allow_html=True)

    try:
        df_all = load_data()
        geo    = load_geo()
    except FileNotFoundError as e:
        st.error(f"❌ ไม่พบไฟล์: {e}"); st.stop()

    # ── Session state ──
    if "selected"     not in st.session_state: st.session_state.selected     = None
    if "tier_filter"  not in st.session_state: st.session_state.tier_filter  = "ทั้งหมด"
    if "score_min"    not in st.session_state: st.session_state.score_min    = 0
    if "compare_list" not in st.session_state: st.session_state.compare_list = []

    col_left, col_map, col_right = st.columns([2.0, 4.2, 2.6])

    # ═══════ LEFT PANEL ═══════
    with col_left:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown("#### 🔎 ค้นหาและกรองข้อมูล")
        st.caption("ข้อมูล 77 จังหวัด · เกณฑ์ v2.0")

        all_provinces = ["— กรุณาเลือกจังหวัด —"] + df_all["province_name_th"].tolist()
        cur_idx = 0
        if st.session_state.selected in df_all["province_name_th"].tolist():
            cur_idx = df_all["province_name_th"].tolist().index(st.session_state.selected) + 1

        sel_dd = st.selectbox("เลือกจังหวัด (77 จังหวัด)", options=all_provinces,
                              index=cur_idx, key="prov_dd")
        if sel_dd != "— กรุณาเลือกจังหวัด —":
            st.session_state.selected = sel_dd

        st.markdown("---")
        st.markdown('<div class="section-header">Tier</div>', unsafe_allow_html=True)
        tier_opts = ["ทั้งหมด","Tier 1 – Prime","Tier 2 – Suitable","Tier 3 – Conditional","Tier 4 – Not Recommended"]
        tier_sel  = st.radio("", tier_opts, horizontal=False,
                             label_visibility="collapsed", key="tier_radio")
        st.session_state.tier_filter = tier_sel

        st.markdown('<div class="section-header">คะแนนขั้นต่ำ</div>', unsafe_allow_html=True)
        min_score = st.slider("", 0, 80, st.session_state.score_min,
                              key="score_slider", label_visibility="collapsed")
        st.session_state.score_min = min_score

        st.markdown('<div class="section-header">ตัวกรองเพิ่มเติม</div>', unsafe_allow_html=True)
        eec_only  = st.checkbox("EEC Zone เท่านั้น")
        strat_only= st.checkbox("Strategic Digital Province เท่านั้น")

        if st.button("🔄 รีเซ็ตตัวกรอง", use_container_width=True):
            st.session_state.tier_filter  = "ทั้งหมด"
            st.session_state.score_min    = 0
            st.session_state.selected     = None
            st.session_state.compare_list = []
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Compare panel
        st.markdown("---")
        st.markdown("##### ⚖️ เปรียบเทียบจังหวัด")
        compare_options = df_all["province_name_th"].tolist()
        compare_sel = st.multiselect(
            "เลือกสูงสุด 5 จังหวัด", compare_options,
            default=st.session_state.compare_list[:5],
            max_selections=5, key="compare_ms",
            label_visibility="collapsed",
        )
        st.session_state.compare_list = compare_sel

        if len(compare_sel) >= 2:
            df_cmp = df_all[df_all["province_name_th"].isin(compare_sel)]
            st.plotly_chart(render_radar(df_cmp), use_container_width=True)
        else:
            st.caption("เลือกอย่างน้อย 2 จังหวัดเพื่อดู Radar")

    # ═══════ CENTER — MAP ═══════
    with col_map:
        # Apply filters for display count
        df_filtered = df_all.copy()
        if tier_sel != "ทั้งหมด":
            df_filtered = df_filtered[df_filtered["tier"] == tier_sel]
        df_filtered = df_filtered[df_filtered["overall_score"] >= min_score]
        if eec_only:  df_filtered = df_filtered[df_filtered["EEC"]]
        if strat_only: df_filtered = df_filtered[df_filtered["Strategic"]]

        st.markdown(
            f'<div style="font-size:.75rem;color:#888;margin-bottom:4px">'
            f'🗺️ แสดง <b>{len(df_filtered)}</b> จาก 77 จังหวัด · '
            f'คลิก <b>Marker ★</b> หรือเลือกจาก Dropdown เพื่อดู Scorecard</div>',
            unsafe_allow_html=True)

        m        = build_map(df_all, geo, st.session_state.selected)
        map_data = st_folium(m, width="100%", height=510,
                             returned_objects=["last_object_clicked_popup"])

        # Detect map click
        if map_data and map_data.get("last_object_clicked_popup"):
            popup_text = map_data["last_object_clicked_popup"] or ""
            for th in df_all["province_name_th"].tolist():
                if th in popup_text:
                    if st.session_state.selected != th:
                        st.session_state.selected = th
                        st.rerun()

        # Summary card ของจังหวัดที่เลือก
        sel = st.session_state.selected
        if sel and sel in df_all["province_name_th"].values:
            row_s = df_all[df_all["province_name_th"] == sel].iloc[0]
            tc = TIER_FILL.get(row_s["tier"],"#888")
            gc = GRADE_COLOR.get(str(row_s["grade"]).strip(),"#888")
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:12px 16px;
                        border:2px solid {tc};margin-top:6px">
              <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
                <div>
                  <span style="font-size:1.05rem;font-weight:800;color:#0A1628">{sel}</span>
                  <span style="font-size:.8rem;font-weight:400;color:#888"> {row_s['province_name_en']}</span><br>
                  <span style="font-size:.78rem;color:#555">อันดับ <b>#{int(row_s['rank_overall'])}</b> · {row_s['region']}</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px">
                  <div style="text-align:center">
                    <div style="font-size:1.6rem;font-weight:800;color:{tc};line-height:1">{row_s['overall_score']:.2f}</div>
                    <div style="font-size:.68rem;color:#888">Overall</div>
                  </div>
                  <div style="display:flex;flex-direction:column;gap:4px">
                    <span style="background:{gc};color:white;padding:2px 10px;border-radius:10px;
                                 font-size:.78rem;font-weight:700;text-align:center">Grade {row_s['grade']}</span>
                    <span style="background:{tc};color:white;padding:2px 10px;border-radius:10px;
                                 font-size:.72rem;font-weight:600;text-align:center">{row_s['tier']}</span>
                  </div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#F5F8FC;border-radius:10px;padding:10px 16px;
                        border:1px dashed #9DC3E6;margin-top:6px;font-size:.85rem;
                        color:#888;text-align:center">
              เลือกจังหวัดเพื่อดูข้อมูลสรุป
            </div>""", unsafe_allow_html=True)

    # ═══════ RIGHT — SCORECARD ═══════
    with col_right:
        sel = st.session_state.selected
        if sel and sel in df_all["province_name_th"].values:
            render_scorecard(df_all[df_all["province_name_th"] == sel].iloc[0])
        else:
            clicked = render_welcome_panel(df_all)
            if clicked:
                st.session_state.selected = clicked
                st.rerun()

    # ── BOTTOM FEATURE CARDS ──
    st.divider()
    feat_cols = st.columns(4)
    feats = [
        ("🔍","ค้นหาและเลือกพื้นที่",
         "ค้นหา กรองตาม Tier, คะแนน, EEC Zone ครบ 77 จังหวัด"),
        ("📊","เปรียบเทียบรายมิติ",
         "Radar Chart 6 มิติ เปรียบเทียบได้สูงสุด 5 จังหวัดพร้อมกัน"),
        ("🗺️","แผนที่เชิงโต้ตอบ",
         "Choropleth แสดงระดับ Tier ทุกจังหวัด คลิกเพื่อดูรายละเอียด"),
        ("📋","สนับสนุนการตัดสินใจ",
         "Gate Pass / Under Review พร้อมจุดแข็ง-จุดอ่อน และข้อมูลดิบ"),
    ]
    for col, (icon, title, desc) in zip(feat_cols, feats):
        col.markdown(f"""
        <div class="feat-card">
          <div class="feat-icon">{icon}</div>
          <div class="feat-title">{title}</div>
          <div class="feat-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F0F7FF;border-radius:8px;padding:10px 18px;margin-top:10px;
                border-left:4px solid #2E75B6;font-size:.85rem;color:#333">
      💡 <b>แนวทางการใช้งาน:</b>
      คลิก Marker บนแผนที่ หรือเลือกจาก Dropdown เพื่อดู Scorecard รายมิติ
      ใช้ Multiselect ด้านซ้ายล่างเพื่อเปรียบเทียบหลายจังหวัดพร้อมกัน
      &nbsp;|&nbsp; <b>ข้อมูล 77 จังหวัด</b> · เกณฑ์ v2.0 · พลังงาน 35% + น้ำ 20% + บุคลากร 20% + BOI 7.5% + นิคม 7.5% + ความเสี่ยง 10%
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
