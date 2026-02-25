# 🏛️ Dashboard Transparansi APBA Aceh 2025

**Anggaran Pendapatan dan Belanja Aceh — Tahun Anggaran 2025**

Dashboard interaktif untuk eksplorasi dan transparansi data APBA Aceh 2025.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 📊 Halaman Dashboard

| Halaman | Visualisasi | Deskripsi |
|---------|-------------|-----------|
| **Ringkasan Eksekutif** | KPI, Pie, Bar, Treemap | Overview anggaran + top 15 SKPD |
| **Eksplorasi Belanja** | Sunburst, Bar, Tabel | Drill-down per SKPD + search |
| **Dana Otsus** | Sankey, Bar | Aliran & distribusi dana otsus |
| **Hibah & Bantuan** | Donut, Bar, Tabel | Penerima hibah & bantuan kab/kota |
| **Analisis Komparatif** | Heatmap, Scatter, Radar | Perbandingan antar SKPD |
| **Pencarian Global** | Tabel | Full-text search seluruh data |

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run dashboard_apba_2025.py
```

## 📈 Data Highlights

- **Total Pendapatan**: Rp 15,58 Triliun
- **Total Belanja**: Rp 19,32 Triliun
- **36 SKPD** ter-mapping otomatis
- **10.255** item belanja detail
- **617** penerima hibah
- **191** penerima bantuan keuangan

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Visualisasi**: Plotly
- **Data Processing**: Pandas, NumPy
- **Deployment**: Streamlit Community Cloud

## 📂 Files

| File | Deskripsi |
|------|-----------|
| `dashboard_apba_2025.py` | Aplikasi utama |
| `requirements.txt` | Dependencies |
| `.streamlit/config.toml` | Konfigurasi tema |
| `02_lampiran2_*.csv` | Rincian APBD (Lamp II) |
| `03_lampiran3_*.csv` | Penerima Hibah (Lamp III) |
| `04_lampiran5_*.csv` | Bantuan Keuangan (Lamp V) |
| `05_lampiran7_*.csv` | Dana Otsus (Lamp VII) |

## 📝 Lisensi

Data publik — Qanun APBA Aceh 2025. Dashboard untuk transparansi & edukasi.
