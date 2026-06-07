# Thailand DC Site Suitability Dashboard — Phase 1

## วิธีรัน (Step-by-step)

### 1. ตรวจสอบโครงสร้างไฟล์
```
บทที่ 4-5/
├── 00_All Database 20260516.xlsx   ← ไฟล์ข้อมูลหลัก (ต้องอยู่ที่นี่!)
└── dc_dashboard/
    ├── app.py
    ├── requirements.txt
    └── README.md
```

> **สำคัญ:** ไฟล์ Excel ต้องอยู่ใน folder `บทที่ 4-5/` ไม่ใช่ใน `dc_dashboard/`

---

### 2. ติดตั้ง Python (ถ้ายังไม่มี)
- ดาวน์โหลดจาก https://www.python.org/downloads/
- ติ๊ก "Add to PATH" ตอนติดตั้ง

---

### 3. เปิด Terminal แล้วไปที่ folder dc_dashboard
```bash
cd "/path/to/บทที่ 4-5/dc_dashboard"
```

---

### 4. ติดตั้ง Library (ครั้งแรกครั้งเดียว)
```bash
pip install -r requirements.txt
```

---

### 5. รันแอป
```bash
streamlit run app.py
```

เบราว์เซอร์จะเปิดอัตโนมัติที่ http://localhost:8501

---

## ฟังก์ชันที่มี

| หน้า | ฟังก์ชัน |
|------|---------|
| 🏠 Dashboard | KPI สรุป, Top 20 Bar Chart, กระจาย Grade/Tier |
| 🔍 ค้นหาจังหวัด | ตาราง filter, Scorecard รายมิติ, Radar Chart, Bar Chart |
| ⚖️ เปรียบเทียบ | Radar overlay สูงสุด 5 จังหวัด + ตารางเปรียบเทียบ |

### Sidebar Filters
- ค้นหาชื่อจังหวัด (ไทย / อังกฤษ)
- Filter ตาม Tier / Grade / Region
- Slider Overall Score
- Checkbox EEC Zone

---

## สูตรคะแนน

```
Overall Score (0–100) =
  Energy        35%   (installed MW 70% + renewable % 30%)
  Water         20%   (storage 70% + annual volume 30%)
  Talent        20%   (universities 40% + vocational 30% + working-age pop 30%)
  Business       7.5% (BOI projects + IT load + investment + EEC/Strategic bonus)
  Infrastructure 7.5% (DC count proxy — จะอัปเดตด้วย IEAT data ใน Phase 2)
  Risk          10%   (placeholder 7.0/10 — จะอัปเดตด้วย GIS flood/seismic ใน Phase 2)
```

---

## Phase 2 (ต่อไป)
- [ ] เพิ่ม Choropleth Map (ต้องการไฟล์ GeoJSON จังหวัดไทย)
- [ ] เพิ่มข้อมูล IEAT (นิคมอุตสาหกรรม)
- [ ] เพิ่มข้อมูล Flood/Seismic Risk จาก GIS
- [ ] Export PDF Scorecard รายจังหวัด

### แหล่ง GeoJSON จังหวัดไทย
ใช้ไฟล์นี้ได้เลย (เปิดให้ใช้ฟรี):
- https://github.com/apisit/thailand.json  
  → ไฟล์ `thailand.json` มีชื่อจังหวัดเป็นภาษาไทยตรงกับ `province_name_th` ในฐานข้อมูล
# dc-site-suitability-pilot
