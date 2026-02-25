#!/usr/bin/env python3
"""
Dashboard Transparansi APBA Aceh 2025
Streamlit + Plotly | Cloud-Ready
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io, warnings
warnings.filterwarnings("ignore")

# ════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════

st.set_page_config(
    page_title="Transparansi APBA Aceh 2025",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CP = {
    "primary":"#1B4965","secondary":"#5FA8D3","accent":"#62B6CB",
    "success":"#2EC4B6","warning":"#FF9F1C","danger":"#E71D36",
    "light":"#CAE9FF","dark":"#0B132B",
}

BC = {
    "Belanja Pegawai":"#1B4965","Belanja Barang dan Jasa":"#5FA8D3",
    "Belanja Modal":"#2EC4B6","Belanja Hibah":"#FF9F1C",
    "Belanja Bantuan Sosial":"#E71D36","Belanja Tidak Terduga":"#9B5DE5",
    "Belanja Transfer":"#00BBF9","Belanja Subsidi":"#F15BB5",
    "Belanja Lainnya":"#AAAAAA",
}

def rp(v, short=False):
    if pd.isna(v) or v == 0: return "Rp 0"
    if short:
        if abs(v)>=1e12: return f"Rp {v/1e12:,.2f} T"
        if abs(v)>=1e9:  return f"Rp {v/1e9:,.2f} M"
        if abs(v)>=1e6:  return f"Rp {v/1e6:,.1f} Jt"
    return f"Rp {v:,.0f}"

# ════════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════════

@st.cache_data
def load_data():
    lamp2 = pd.read_csv("02_lampiran2_rincian_apbd_2025.csv", dtype=str)
    lamp3 = pd.read_csv("03_lampiran3_hibah_2025.csv", dtype=str)
    lamp5 = pd.read_csv("04_lampiran5_bantuan_keuangan_2025.csv", dtype=str)
    lamp7 = pd.read_csv("05_lampiran7_dana_otsus_2025.csv", dtype=str)

    for df in [lamp2, lamp3, lamp5, lamp7]:
        if "HALAMAN" in df.columns:
            df["HAL_NUM"] = pd.to_numeric(df["HALAMAN"], errors="coerce")
        if "JUMLAH_RP" in df.columns:
            df["JUMLAH_NUM"] = pd.to_numeric(df["JUMLAH_RP"], errors="coerce")
        if "LEVEL" in df.columns:
            df["LEVEL_NUM"] = pd.to_numeric(df["LEVEL"], errors="coerce")
        if "BESARAN_RP" in df.columns:
            df["BESARAN_NUM"] = pd.to_numeric(df["BESARAN_RP"], errors="coerce")

    # ── SKPD Mapping ──
    S = [
        ("Dinas Pendidikan","DINAS","1.01",55,82),
        ("Bappeda","BADAN","4.01",83,99),
        ("Dinas Pendidikan Dayah","DINAS","1.01",100,204),
        ("Dinas Kesehatan","DINAS","1.02",205,215),
        ("Satpol PP & WH","SATPOL","1.05",216,250),
        ("Dinas Sosial","DINAS","1.06",251,280),
        ("Dinas Pemberdayaan Perempuan & PA","DINAS","2.08",281,370),
        ("Dinas Pangan","DINAS","2.09",371,400),
        ("Dinas Kominfo & Persandian","DINAS","2.16",401,462),
        ("Dinas PUPR","DINAS","1.03",463,473),
        ("DPMPTSP","DINAS","2.18",474,520),
        ("Dinas Kebudayaan & Pariwisata","DINAS","2.22",521,555),
        ("Dinas Perpustakaan & Kearsipan","DINAS","2.23",556,600),
        ("Dinas Tenaga Kerja","DINAS","2.07",601,630),
        ("Dinas LHK","DINAS","2.11",631,656),
        ("RSUD dr. Zainoel Abidin","RSUD","1.02",657,669),
        ("Dinas Pemberdayaan Masyarakat & Gampong","DINAS","2.13",670,700),
        ("Dinas Syariat Islam","DINAS","9.01",701,730),
        ("Dinas Pertanian & Perkebunan","DINAS","3.27",731,760),
        ("Dinas Peternakan","DINAS","3.27",761,780),
        ("Dinas Koperasi & UKM","DINAS","2.17",781,800),
        ("BPKA","BADAN","4.02",801,812),
        ("Dinas Perumahan & Permukiman","DINAS","1.04",813,823),
        ("BKD","BADAN","5.01",824,860),
        ("BPSDM","BADAN","5.02",861,900),
        ("Inspektorat Aceh","INSPEKTORAT","6.01",901,920),
        ("Sekretariat MPU","SEKRETARIAT","9.01",921,950),
        ("Sekretariat MAA","SEKRETARIAT","9.01",951,970),
        ("Sekretariat MPA","SEKRETARIAT","9.01",971,980),
        ("Sekretariat BRA","SEKRETARIAT","9.01",981,987),
        ("Sekretariat Daerah Aceh","SETDA","7.01",26,54),
        ("Dinas Kelautan & Perikanan","DINAS","3.25",988,1000),
        ("Dinas Perindustrian & Perdagangan","DINAS","3.30",1001,1020),
        ("Dinas Pemuda & Olahraga","DINAS","2.19",1021,1040),
        ("Dinas Perhubungan","DINAS","2.15",1041,1055),
        ("Badan Kesbangpol","BADAN","9.01",1056,1062),
    ]
    skpd_df = pd.DataFrame(S, columns=["nama_skpd","tipe","kode_urusan","h_awal","h_akhir"])

    # Map halaman → SKPD
    ranges = list(zip(skpd_df["h_awal"], skpd_df["h_akhir"], skpd_df["nama_skpd"]))
    def m(h):
        if pd.isna(h): return "N/A"
        for a, b, n in ranges:
            if a <= h <= b: return n
        return "N/A"
    lamp2["SKPD"] = lamp2["HAL_NUM"].apply(m)

    # Kategori belanja
    def kb(k):
        if not isinstance(k, str): return "Lainnya"
        if k.startswith("5.1.01"): return "Belanja Pegawai"
        if k.startswith("5.1.02"): return "Belanja Barang dan Jasa"
        if k.startswith("5.1.03"): return "Belanja Subsidi"
        if k.startswith("5.1.05"): return "Belanja Hibah"
        if k.startswith("5.1.06"): return "Belanja Bantuan Sosial"
        if k.startswith("5.2"):    return "Belanja Modal"
        if k.startswith("5.3"):    return "Belanja Tidak Terduga"
        if k.startswith("5.4"):    return "Belanja Transfer"
        if k.startswith("5."):     return "Belanja Lainnya"
        if k.startswith("4."):     return "Pendapatan"
        if k.startswith("6."):     return "Pembiayaan"
        return "Lainnya"
    lamp2["KAT"] = lamp2["KODE_REKENING"].apply(kb)

    # Urusan map
    UM = {
        "1.01":"Pendidikan","1.02":"Kesehatan","1.03":"Pekerjaan Umum",
        "1.04":"Perumahan","1.05":"Trantibum","1.06":"Sosial",
        "2.07":"Tenaga Kerja","2.08":"Pemberdayaan Perempuan","2.09":"Pangan",
        "2.11":"Lingkungan Hidup","2.13":"Pemberdayaan Masyarakat",
        "2.15":"Perhubungan","2.16":"Komunikasi & Informatika",
        "2.17":"Koperasi & UKM","2.18":"Penanaman Modal",
        "2.19":"Pemuda & Olahraga","2.22":"Kebudayaan","2.23":"Perpustakaan",
        "3.25":"Kelautan & Perikanan","3.27":"Pertanian",
        "3.30":"Perdagangan","4.01":"Perencanaan","4.02":"Keuangan",
        "5.01":"Kepegawaian","5.02":"Pengembangan SDM",
        "6.01":"Pengawasan","7.01":"Pemerintahan Umum",
        "9.01":"Keistimewaan Aceh",
    }
    skpd_df["urusan"] = skpd_df["kode_urusan"].map(UM).fillna("Lainnya")
    urusan_inv = dict(zip(skpd_df["nama_skpd"], skpd_df["urusan"]))

    return lamp2, lamp3, lamp5, lamp7, skpd_df, urusan_inv


# ════════════════════════════════════════════
# PAGE 1: RINGKASAN EKSEKUTIF
# ════════════════════════════════════════════

def pg_ringkasan(lamp2, lamp3, lamp5, lamp7, urusan_inv):
    st.markdown("## 📊 Ringkasan Eksekutif APBA 2025")
    d = lamp2[lamp2["LEVEL_NUM"]==6].copy()
    pend = d[d["KODE_REKENING"].str.startswith("4.",na=False)]["JUMLAH_NUM"].sum()
    bel  = d[d["KODE_REKENING"].str.startswith("5.",na=False)]["JUMLAH_NUM"].sum()
    sur  = pend - bel
    otsus = lamp7["JUMLAH_NUM"].sum() if "JUMLAH_NUM" in lamp7 else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("💰 Pendapatan", rp(pend,True))
    c2.metric("💸 Belanja", rp(bel,True))
    c3.metric("📈 Surplus/Defisit", rp(sur,True), delta=f"{sur/bel*100:.1f}%" if bel else "0%")
    c4.metric("🏛️ Dana Otsus", rp(otsus,True))
    st.divider()

    L,R = st.columns(2)
    with L:
        st.markdown("### Komposisi Belanja")
        bd = d[d["KODE_REKENING"].str.startswith("5.",na=False)]
        km = bd.groupby("KAT")["JUMLAH_NUM"].sum().reset_index()
        km = km[km["JUMLAH_NUM"]>0].sort_values("JUMLAH_NUM",ascending=False)
        km.columns = ["Kategori","Jumlah"]
        fig = px.pie(km, values="Jumlah", names="Kategori", color="Kategori",
                     color_discrete_map=BC, hole=0.4)
        fig.update_traces(textposition="inside", textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>")
        fig.update_layout(showlegend=False, height=420, margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig, use_container_width=True)

    with R:
        st.markdown("### Top 15 SKPD")
        st15 = bd.groupby("SKPD")["JUMLAH_NUM"].sum().reset_index()
        st15.columns = ["SKPD","Total"]
        st15 = st15.sort_values("Total",ascending=True).tail(15)
        fig = px.bar(st15, x="Total", y="SKPD", orientation="h",
                     color_discrete_sequence=[CP["primary"]])
        fig.update_traces(hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>")
        fig.update_layout(height=420, xaxis_title="", yaxis_title="",
                          margin=dict(t=20,b=20,l=10,r=10), xaxis=dict(tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Alokasi per Urusan Pemerintahan")
    bd2 = bd.copy()
    bd2["Urusan"] = bd2["SKPD"].map(urusan_inv).fillna("Lainnya")
    tm = bd2.groupby(["Urusan","SKPD"])["JUMLAH_NUM"].sum().reset_index()
    tm.columns = ["Urusan","SKPD","Anggaran"]
    tm = tm[tm["Anggaran"]>0]
    fig = px.treemap(tm, path=["Urusan","SKPD"], values="Anggaran",
                     color="Anggaran", color_continuous_scale="Blues")
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percentRoot:.1%}<extra></extra>")
    fig.update_layout(height=500, margin=dict(t=30,b=10,l=10,r=10), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE 2: EKSPLORASI BELANJA
# ════════════════════════════════════════════

def pg_eksplorasi(lamp2):
    st.markdown("## 🔍 Eksplorasi Belanja per SKPD")
    d = lamp2[(lamp2["LEVEL_NUM"]==6) & lamp2["KODE_REKENING"].str.startswith("5.",na=False)].copy()
    sl = sorted(d["SKPD"].dropna().unique())
    sel = st.selectbox("🏢 Pilih SKPD:", sl, index=0)
    sd = d[d["SKPD"]==sel]; tot = sd["JUMLAH_NUM"].sum()
    st.info(f"**{sel}** — Total: **{rp(tot,True)}** ({len(sd):,} item)")

    L,R = st.columns(2)
    with L:
        st.markdown("### Proporsi Belanja")
        sb = sd.copy(); sb["U"] = sb["URAIAN"].str[:40]
        sa = sb.groupby(["KAT","U"])["JUMLAH_NUM"].sum().reset_index()
        sa = sa[sa["JUMLAH_NUM"]>0].nlargest(30,"JUMLAH_NUM")
        fig = px.sunburst(sa, path=["KAT","U"], values="JUMLAH_NUM",
                          color="KAT", color_discrete_map=BC)
        fig.update_traces(hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<extra></extra>")
        fig.update_layout(height=450, margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    with R:
        st.markdown("### Breakdown Kategori")
        ks = sd.groupby("KAT")["JUMLAH_NUM"].sum().reset_index().sort_values("JUMLAH_NUM",ascending=False)
        ks.columns = ["Kategori","Jumlah"]; ks["Fmt"] = ks["Jumlah"].apply(lambda x: rp(x,True))
        fig = px.bar(ks, x="Jumlah", y="Kategori", orientation="h",
                     color="Kategori", color_discrete_map=BC, text="Fmt")
        fig.update_traces(textposition="outside",
            hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>")
        fig.update_layout(height=450, showlegend=False,
                          margin=dict(t=10,b=10,l=10,r=80), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Rincian Belanja")
    q = st.text_input("🔎 Cari kode/uraian:", "")
    dd = sd[["KODE_REKENING","URAIAN","JUMLAH_NUM","KAT","INDIKATOR"]].copy()
    dd.columns = ["Kode","Uraian","Jumlah (Rp)","Kategori","Indikator"]
    if q:
        m = dd["Kode"].str.contains(q,case=False,na=False) | dd["Uraian"].str.contains(q,case=False,na=False) | dd["Indikator"].str.contains(q,case=False,na=False)
        dd = dd[m]
    st.dataframe(dd.sort_values("Jumlah (Rp)",ascending=False).style.format({"Jumlah (Rp)":"{:,.0f}"}),
                 use_container_width=True, height=400)
    st.download_button("📥 Download CSV", dd.to_csv(index=False).encode("utf-8"),
                       f"belanja_{sel.replace(' ','_')}.csv","text/csv")


# ════════════════════════════════════════════
# PAGE 3: DANA OTSUS
# ════════════════════════════════════════════

def pg_otsus(lamp7):
    st.markdown("## 🏛️ Dana Otonomi Khusus Aceh (Lampiran VII)")
    l7 = lamp7.copy()
    l7p = l7[l7["KODE_REKENING"].str.match(r"^\d+\.\d+\.\d+$",na=False)].copy()
    l7p["ku"] = l7p["KODE_REKENING"].str.extract(r"^(\d+\.\d+)")
    UN = {"1.01":"Pendidikan","1.02":"Kesehatan","1.03":"Pekerjaan Umum",
          "1.04":"Perumahan","1.06":"Sosial","2.09":"Pangan","2.11":"LH & Kehutanan",
          "2.13":"Pemberdayaan Masyarakat","2.16":"Komunikasi","2.22":"Kebudayaan",
          "3.25":"Kelautan","3.27":"Pertanian","9.01":"Keistimewaan Aceh"}
    l7p["Sektor"] = l7p["ku"].map(UN).fillna("Lainnya")
    st.metric("Total Dana Otsus", rp(l7["JUMLAH_NUM"].sum(),True))

    L,R = st.columns(2)
    with L:
        st.markdown("### Distribusi per Sektor")
        sa = l7p.groupby("Sektor")["JUMLAH_NUM"].sum().reset_index()
        sa = sa[sa["JUMLAH_NUM"]>0].sort_values("JUMLAH_NUM",ascending=True)
        sa.columns = ["Sektor","Alokasi"]
        fig = px.bar(sa, x="Alokasi", y="Sektor", orientation="h",
                     color_discrete_sequence=[CP["accent"]])
        fig.update_traces(hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>")
        fig.update_layout(height=400, xaxis_title="", yaxis_title="", margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    with R:
        st.markdown("### Aliran Dana Otsus")
        sd2 = l7p.groupby("Sektor")["JUMLAH_NUM"].sum().reset_index()
        sd2 = sd2[sd2["JUMLAH_NUM"]>0].sort_values("JUMLAH_NUM",ascending=False)
        labels = ["Dana Otsus Aceh"] + sd2["Sektor"].tolist()
        fig = go.Figure(go.Sankey(
            node=dict(pad=15,thickness=20,line=dict(color="black",width=0.5),
                      label=labels, color=[CP["primary"]]+[CP["accent"]]*len(sd2)),
            link=dict(source=[0]*len(sd2), target=list(range(1,len(sd2)+1)),
                      value=sd2["JUMLAH_NUM"].tolist())))
        fig.update_layout(height=400, margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Detail Otsus")
    do = l7[["KODE_REKENING","URAIAN","JUMLAH_NUM"]].copy()
    do.columns = ["Kode","Uraian","Jumlah (Rp)"]
    do = do[do["Jumlah (Rp)"]>0]
    st.dataframe(do.sort_values("Jumlah (Rp)",ascending=False).style.format({"Jumlah (Rp)":"{:,.0f}"}),
                 use_container_width=True, height=400)


# ════════════════════════════════════════════
# PAGE 4: HIBAH & BANTUAN
# ════════════════════════════════════════════

def pg_hibah(lamp3, lamp5):
    st.markdown("## 🤝 Transparansi Hibah & Bantuan Keuangan")
    t1,t2 = st.tabs(["📄 Penerima Hibah (Lamp III)","🗺️ Bantuan Keuangan (Lamp V)"])

    with t1:
        h = lamp3[lamp3["NO"].notna() & (lamp3["NO"]!="") & (lamp3["NO"]!="nan")].copy()
        c1,c2,c3 = st.columns(3)
        c1.metric("Hibah Uang", rp(h[h["JENIS_HIBAH"]=="UANG"]["BESARAN_NUM"].sum(),True))
        c2.metric("Hibah Barang", rp(h[h["JENIS_HIBAH"]=="BARANG"]["BESARAN_NUM"].sum(),True))
        c3.metric("Jumlah Penerima", f"{len(h):,}")

        L,R = st.columns(2)
        with L:
            st.markdown("### Proporsi Hibah")
            hj = h.groupby("JENIS_HIBAH")["BESARAN_NUM"].sum().reset_index()
            hj.columns = ["Jenis","Total"]
            fig = px.pie(hj, values="Total", names="Jenis", hole=0.5,
                         color_discrete_sequence=[CP["primary"],CP["warning"]])
            fig.update_traces(textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<extra></extra>")
            fig.update_layout(height=350, margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
        with R:
            st.markdown("### Top 15 Penerima")
            th = h.nlargest(15,"BESARAN_NUM")[["NAMA_PENERIMA","BESARAN_NUM","JENIS_HIBAH"]]
            th.columns = ["Penerima","Besaran (Rp)","Jenis"]
            st.dataframe(th.style.format({"Besaran (Rp)":"{:,.0f}"}), use_container_width=True, height=350)

        st.markdown("### 📋 Daftar Lengkap")
        jf = st.multiselect("Filter Jenis:", ["UANG","BARANG"], default=["UANG","BARANG"])
        fh = h[h["JENIS_HIBAH"].isin(jf)]
        dh = fh[["NO","NAMA_PENERIMA","ALAMAT","BESARAN_NUM","JENIS_HIBAH"]].copy()
        dh.columns = ["No","Penerima","Alamat","Besaran (Rp)","Jenis"]
        sq = st.text_input("🔎 Cari penerima:", "", key="sh")
        if sq:
            dh = dh[dh["Penerima"].str.contains(sq,case=False,na=False)|dh["Alamat"].str.contains(sq,case=False,na=False)]
        st.dataframe(dh.sort_values("Besaran (Rp)",ascending=False).style.format({"Besaran (Rp)":"{:,.0f}"}),
                     use_container_width=True, height=400)
        st.download_button("📥 Download CSV", dh.to_csv(index=False).encode("utf-8"), "hibah_apba_2025.csv")

    with t2:
        b = lamp5[lamp5["NO"].notna() & (lamp5["NO"]!="") & (lamp5["NO"]!="nan")].copy()
        c1,c2 = st.columns(2)
        c1.metric("Bantuan Umum", rp(b[b["JENIS"]=="UMUM"]["BESARAN_NUM"].sum(),True))
        c2.metric("Bantuan Khusus", rp(b[b["JENIS"]=="KHUSUS"]["BESARAN_NUM"].sum(),True))
        st.markdown("### Distribusi per Kabupaten/Kota")
        bk = b.groupby(["NAMA_PENERIMA","JENIS"])["BESARAN_NUM"].sum().reset_index()
        bk.columns = ["Kab/Kota","Jenis","Besaran"]
        bk = bk[bk["Besaran"]>0].sort_values("Besaran",ascending=True)
        fig = px.bar(bk, x="Besaran", y="Kab/Kota", orientation="h", color="Jenis",
                     color_discrete_map={"UMUM":CP["secondary"],"KHUSUS":CP["warning"]}, barmode="stack")
        fig.update_traces(hovertemplate="<b>%{y}</b><br>%{data.name}: Rp %{x:,.0f}<extra></extra>")
        fig.update_layout(height=max(400,len(bk)*22), xaxis_title="", yaxis_title="",
                          margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE 5: ANALISIS KOMPARATIF
# ════════════════════════════════════════════

def pg_analisis(lamp2):
    st.markdown("## 📈 Analisis Komparatif")
    d = lamp2[(lamp2["LEVEL_NUM"]==6) & lamp2["KODE_REKENING"].str.startswith("5.",na=False)].copy()

    st.markdown("### Heatmap: Intensitas Belanja per SKPD & Jenis")
    pv = d.groupby(["SKPD","KAT"])["JUMLAH_NUM"].sum().reset_index()
    pt = pv.pivot_table(index="SKPD", columns="KAT", values="JUMLAH_NUM", fill_value=0)
    pl = np.log10(pt.replace(0,np.nan))
    fig = px.imshow(pl, labels=dict(x="Jenis Belanja",y="SKPD",color="Log₁₀(Rp)"),
                    color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(height=700, margin=dict(t=10,b=10,l=10,r=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Korelasi: Sub-Kegiatan vs Anggaran")
    pc = d.groupby("SKPD").agg(total=("JUMLAH_NUM","sum"),items=("JUMLAH_NUM","count"),
                                indikator=("INDIKATOR","nunique")).reset_index()
    fig = px.scatter(pc, x="indikator", y="total", size="items", color="total",
                     hover_name="SKPD", color_continuous_scale="Viridis",
                     labels={"indikator":"Sub-Kegiatan","total":"Total Anggaran (Rp)","items":"Item"})
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Sub-Keg: %{x}<br>Rp %{y:,.0f}<extra></extra>")
    fig.update_layout(height=500, margin=dict(t=10,b=10,l=10,r=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Radar: Profil Belanja Top 10 SKPD")
    t10 = d.groupby("SKPD")["JUMLAH_NUM"].sum().nlargest(10).index.tolist()
    rd = d[d["SKPD"].isin(t10)]
    rp2 = rd.groupby(["SKPD","KAT"])["JUMLAH_NUM"].sum().reset_index()
    rp2["Pct"] = rp2.groupby("SKPD")["JUMLAH_NUM"].transform(lambda x: x/x.sum()*100).round(1)
    sel = st.multiselect("Pilih SKPD:", t10, default=t10[:3])
    if sel:
        fig = go.Figure()
        for s in sel:
            sr = rp2[rp2["SKPD"]==s]
            if len(sr) > 0:
                fig.add_trace(go.Scatterpolar(
                    r=sr["Pct"].tolist()+[sr["Pct"].iloc[0]],
                    theta=sr["KAT"].tolist()+[sr["KAT"].iloc[0]],
                    fill="toself", name=s[:25],
                    hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>"))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),
                          height=500, margin=dict(t=30,b=30,l=80,r=80),
                          showlegend=True, legend=dict(font=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE 6: PENCARIAN GLOBAL
# ════════════════════════════════════════════

def pg_search(lamp2):
    st.markdown("## 🔎 Pencarian Global")
    q = st.text_input("Masukkan kata kunci:", "")
    if q and len(q)>=2:
        m = lamp2["KODE_REKENING"].str.contains(q,case=False,na=False) | \
            lamp2["URAIAN"].str.contains(q,case=False,na=False) | \
            lamp2["INDIKATOR"].str.contains(q,case=False,na=False)
        r = lamp2[m].copy()
        st.success(f"Ditemukan **{len(r):,}** baris untuk \"{q}\"")
        dd = r[["KODE_REKENING","URAIAN","JUMLAH_NUM","KAT","SKPD","HALAMAN"]].copy()
        dd.columns = ["Kode","Uraian","Jumlah (Rp)","Kategori","SKPD","Halaman"]
        st.dataframe(dd.sort_values("Jumlah (Rp)",ascending=False).style.format({"Jumlah (Rp)":"{:,.0f}"}),
                     use_container_width=True, height=500)
        st.download_button("📥 Download", dd.to_csv(index=False).encode("utf-8"), "pencarian_apba.csv")
    elif q: st.warning("Minimal 2 karakter.")


# ════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════

def main():
    with st.sidebar:
        st.markdown("# 🏛️ APBA Aceh 2025")
        st.caption("Dashboard Transparansi Anggaran")
        st.divider()
        page = st.radio("📑 Navigasi:", [
            "📊 Ringkasan Eksekutif",
            "🔍 Eksplorasi Belanja",
            "🏛️ Dana Otsus",
            "🤝 Hibah & Bantuan",
            "📈 Analisis Komparatif",
            "🔎 Pencarian Global",
        ])
        st.divider()
        st.markdown("**Sumber:** Qanun APBA 2025\n\n**Cakupan:** Lampiran I-VII\n\n**Update:** Februari 2026")
        st.caption("© 2026 Transparansi APBA Aceh")

    lamp2, lamp3, lamp5, lamp7, skpd_df, urusan_inv = load_data()

    if "Ringkasan" in page:     pg_ringkasan(lamp2,lamp3,lamp5,lamp7,urusan_inv)
    elif "Eksplorasi" in page:  pg_eksplorasi(lamp2)
    elif "Otsus" in page:       pg_otsus(lamp7)
    elif "Hibah" in page:       pg_hibah(lamp3,lamp5)
    elif "Komparatif" in page:  pg_analisis(lamp2)
    elif "Pencarian" in page:   pg_search(lamp2)

if __name__ == "__main__":
    main()
