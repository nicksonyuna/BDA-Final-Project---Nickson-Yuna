# -*- coding: utf-8 -*-
"""
Executive Dashboard - Sistem Peringatan Dini Banjir DKI Jakarta
================================================================
Memvisualisasikan hasil Machine Learning (Bab 5) dan Graph Analytics (Bab 6)
dari arsitektur Big Data mitigasi banjir DAS Ciliwung.

Jalankan:  streamlit run app.py
"""
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")

# ------------------------------------------------------------------ CONFIG
st.set_page_config(
    page_title="Dashboard Mitigasi Banjir DKI Jakarta",
    layout="wide",
    page_icon="🌊",
    initial_sidebar_state="expanded",
)

# Palet warna korporat
C_PRIMARY = "#0A4D8C"   # biru tua
C_ACCENT = "#1E88E5"    # biru
C_DANGER = "#D32F2F"    # merah
C_WARN = "#F9A825"      # oranye
C_SAFE = "#2E7D32"      # hijau
C_BG = "#0E1117"

# ------------------------------------------------------------------ CSS
st.markdown(
    """
    <style>
    /* Header bawaan Streamlit dibiarkan utuh agar tombol buka/tutup sidebar
       selalu tersedia. Hanya jarak atas konten yang ditambah agar judul lega. */
    .block-container {padding-top: 3.2rem; padding-bottom: 2rem;}
    /* Pastikan tombol pembuka sidebar selalu terlihat & di atas elemen lain */
    [data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important; opacity: 1 !important; z-index: 999999 !important;
    }
    .main-title {font-size: 1.75rem; font-weight: 800; color: #E3F2FD;
        margin-bottom: .15rem; line-height: 1.25;}
    .subtitle {color: #90CAF9; font-size: 0.98rem; margin-bottom: .4rem;}
    .kpi-card {
        background: linear-gradient(160deg, #13293D 0%, #0A1929 100%);
        border: 1px solid #1E3A5F; border-radius: 14px;
        padding: 18px 20px; box-shadow: 0 4px 14px rgba(0,0,0,.35);
    }
    .kpi-label {color:#90CAF9; font-size:.82rem; letter-spacing:.4px; text-transform:uppercase;}
    .kpi-value {color:#FFFFFF; font-size:1.9rem; font-weight:800; line-height:1.1;}
    .kpi-sub {font-size:.8rem; margin-top:2px;}
    .section-head {font-size:1.25rem; font-weight:700; color:#E3F2FD;
        border-left:5px solid #1E88E5; padding-left:12px; margin:8px 0 4px 0;}
    .badge {display:inline-block; padding:3px 10px; border-radius:20px;
        font-size:.75rem; font-weight:700; margin-right:6px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ DATA
def _ensure_data():
    """Jika dataset belum ada (mis. saat baru deploy), buat otomatis."""
    needed = ["data_prediksi_dashboard_final.csv", "data_graph_dashboard.csv",
              "data_feature_importance.csv", "data_metrics.csv"]
    if all(os.path.exists(os.path.join(DATA_DIR, f)) for f in needed):
        return
    import runpy
    runpy.run_path(os.path.join(BASE, "generate_data.py"))


@st.cache_data
def load_data():
    _ensure_data()
    df_pred = pd.read_csv(os.path.join(DATA_DIR, "data_prediksi_dashboard_final.csv"))
    df_pred["tanggal"] = pd.to_datetime(df_pred["tanggal"])
    df_graph = pd.read_csv(os.path.join(DATA_DIR, "data_graph_dashboard.csv"))
    df_fi = pd.read_csv(os.path.join(DATA_DIR, "data_feature_importance.csv"))
    df_metrics = pd.read_csv(os.path.join(DATA_DIR, "data_metrics.csv")).iloc[0]
    return df_pred, df_graph, df_fi, df_metrics


try:
    df_pred, df_graph, df_fi, m = load_data()
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()

# ------------------------------------------------------------------ SIDEBAR
with st.sidebar:
    st.markdown("### 🌊 Panel Kendali")
    st.caption("Sistem Peringatan Dini Banjir DAS Ciliwung")
    st.divider()

    years = sorted(df_pred["tanggal"].dt.year.unique())
    yr_sel = st.multiselect("Filter Tahun Observasi", years, default=years)

    status_opt = st.radio(
        "Tampilkan Status Prediksi",
        ["Semua", "Hanya Alarm Banjir", "Hanya Kondisi Aman"],
        index=0,
    )
    st.divider()
    st.markdown(
        f"<span class='badge' style='background:{C_SAFE};color:#fff'>Model: Random Forest</span>"
        f"<span class='badge' style='background:{C_ACCENT};color:#fff'>Engine: Spark MLlib</span>",
        unsafe_allow_html=True,
    )
    st.caption("Sumber: Copernicus ERA5 (2016–2025) & BPBD DKI Jakarta")

# Terapkan filter
mask = df_pred["tanggal"].dt.year.isin(yr_sel) if yr_sel else np.ones(len(df_pred), bool)
dff = df_pred[mask].copy()
if status_opt == "Hanya Alarm Banjir":
    dff = dff[dff["prediction"] == 1.0]
elif status_opt == "Hanya Kondisi Aman":
    dff = dff[dff["prediction"] == 0.0]

# ------------------------------------------------------------------ HEADER
st.markdown("<div class='main-title'>🌊 Executive Dashboard — Sistem Peringatan Dini Banjir DKI Jakarta</div>",
            unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Integrasi prediksi hidrometeorologi (Machine Learning) dan analisis "
    "rambatan spasial (Graph Analytics) pada Daerah Aliran Sungai Ciliwung.</div>",
    unsafe_allow_html=True,
)
st.divider()


def kpi(col, label, value, sub="", sub_color="#90CAF9"):
    col.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"<div class='kpi-sub' style='color:{sub_color}'>{sub}</div></div>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ KPI ROW
total_hari = len(df_pred)
aktual = int(df_pred["label"].sum())
prediksi = int(df_pred["prediction"].sum())
alarm_palsu = int(m["fp"])

c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Total Observasi", f"{total_hari:,}", "hari teruji")
kpi(c2, "Banjir Aktual", f"{aktual}", "insiden tercatat", C_DANGER)
kpi(c3, "Alarm Prediksi", f"{prediksi}", f"+{alarm_palsu} alarm pencegahan", C_WARN)
kpi(c4, "Akurasi Terkalibrasi", f"{m['accuracy']*100:.2f}%", "pasca-balancing", C_ACCENT)
kpi(c5, "Sensitivitas Banjir", f"{m['sensitivity_recall_banjir']*100:.1f}%", "recall kelas banjir", C_SAFE)

st.divider()

# ------------------------------------------------------------------ TABS
tab1, tab2, tab3 = st.tabs(
    ["📈 Prediksi Machine Learning", "🗺️ Graph Analytics (Rambatan Air)", "📋 Data & Audit"]
)

# ========================== TAB 1 : MACHINE LEARNING =====================
with tab1:
    st.markdown("<div class='section-head'>Performa Model Klasifikasi Banjir</div>",
                unsafe_allow_html=True)

    colA, colB = st.columns([1, 1])

    # --- Confusion Matrix ---
    with colA:
        st.markdown("**Matriks Kebingungan (Confusion Matrix)**")
        cm = np.array([[int(m["tn"]), int(m["fp"])],
                       [int(m["fn"]), int(m["tp"])]])
        fig_cm = go.Figure(data=go.Heatmap(
            z=cm,
            x=["Prediksi Aman", "Prediksi Banjir"],
            y=["Aktual Aman", "Aktual Banjir"],
            text=cm, texttemplate="%{text}", textfont={"size": 22, "color": "white"},
            colorscale="Blues", showscale=False,
        ))
        fig_cm.update_layout(
            template="plotly_dark", height=360,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_cm, width="stretch")
        st.caption(
            f"TP={int(m['tp'])} · TN={int(m['tn'])} · FP={int(m['fp'])} · FN={int(m['fn'])}. "
            "Model mengutamakan deteksi banjir (meminimalkan False Negative)."
        )

    # --- Feature Importance ---
    with colB:
        st.markdown("**Tingkat Kepentingan Fitur Pemicu Banjir**")
        fi_sorted = df_fi.sort_values("Bobot")
        fig_fi = px.bar(
            fi_sorted, x="Bobot", y="Fitur", orientation="h",
            color="Bobot", color_continuous_scale="Teal",
            text=(fi_sorted["Bobot"] * 100).round(2).astype(str) + "%",
            hover_data={"Deskripsi": True, "Bobot": ":.4f"},
        )
        fig_fi.update_traces(textposition="outside")
        fig_fi.update_layout(
            template="plotly_dark", height=360, coloraxis_showscale=False,
            margin=dict(l=10, r=30, t=30, b=10),
            xaxis_title="Bobot Pengaruh", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_fi, width="stretch")
        st.caption("Limpasan permukaan (sro) adalah pemicu utama — ciri khas banjir urban Jakarta.")

    # --- Metrik bar ---
    st.markdown("<div class='section-head'>Ringkasan Metrik Evaluasi</div>", unsafe_allow_html=True)
    met_df = pd.DataFrame({
        "Metrik": ["Accuracy", "F1-Score", "Weighted Precision", "Weighted Recall"],
        "Nilai": [m["accuracy"], m["f1"], m["weighted_precision"], m["weighted_recall"]],
    })
    fig_met = px.bar(
        met_df, x="Metrik", y="Nilai", color="Metrik",
        text=(met_df["Nilai"] * 100).round(2).astype(str) + "%",
        color_discrete_sequence=[C_ACCENT, C_SAFE, C_PRIMARY, C_WARN],
    )
    fig_met.update_traces(textposition="outside")
    fig_met.update_layout(
        template="plotly_dark", height=320, showlegend=False,
        yaxis=dict(range=[0, 1], title="Skor"), xaxis_title="",
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_met, width="stretch")

    # --- Time series Surface Runoff ---
    st.markdown("<div class='section-head'>Tren Limpasan Permukaan vs Alarm Banjir</div>",
                unsafe_allow_html=True)
    ts = dff.sort_values("tanggal")
    fig_ts = px.line(
        ts, x="tanggal", y="sro",
        labels={"sro": "Volume Limpasan (sro)", "tanggal": "Tanggal Observasi"},
    )
    fig_ts.update_traces(line_color=C_ACCENT, line_width=1.2)
    alarm = ts[ts["prediction"] == 1.0]
    fig_ts.add_scatter(
        x=alarm["tanggal"], y=alarm["sro"], mode="markers",
        marker=dict(color=C_DANGER, size=7, line=dict(color="white", width=0.5)),
        name="Alarm Banjir",
    )
    fig_ts.update_layout(
        template="plotly_dark", height=380,
        margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h", y=1.1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_ts, width="stretch")

# ========================== TAB 2 : GRAPH ANALYTICS ======================
with tab2:
    st.markdown("<div class='section-head'>Topologi Rambatan Air DAS Ciliwung</div>",
                unsafe_allow_html=True)

    colG1, colG2 = st.columns([1.15, 1])

    # --- Network graph ---
    with colG1:
        st.markdown("**Jaringan Aliran Hulu → Hilir (ukuran node = skor PageRank)**")
        edges = [
            ("Katulampa (Bogor)", "Depok"), ("Depok", "Pejaten Timur"),
            ("Pejaten Timur", "Cawang"), ("Cawang", "Bidara Cina"),
            ("Cililitan", "Bidara Cina"), ("Bidara Cina", "Kampung Melayu"),
            ("Kampung Melayu", "Manggarai"), ("Bukit Duri", "Manggarai"),
        ]
        # Posisi manual hulu(atas) -> hilir(bawah)
        pos = {
            "Katulampa (Bogor)": (0.1, 1.00), "Depok": (0.1, 0.80),
            "Pejaten Timur": (0.1, 0.60), "Cawang": (0.25, 0.42),
            "Cililitan": (0.55, 0.42), "Bidara Cina": (0.40, 0.26),
            "Bukit Duri": (0.75, 0.14), "Kampung Melayu": (0.40, 0.10),
            "Manggarai": (0.57, -0.05),
        }
        pr = dict(zip(df_graph["Kelurahan"], df_graph["PageRank_Score"]))

        edge_x, edge_y = [], []
        for a, b in edges:
            edge_x += [pos[a][0], pos[b][0], None]
            edge_y += [pos[a][1], pos[b][1], None]
        fig_net = go.Figure()
        fig_net.add_trace(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(color="rgba(211,47,47,0.55)", width=2), hoverinfo="none",
        ))
        nx_, ny_, nsize, ntext, nhover = [], [], [], [], []
        for n, (x, y) in pos.items():
            nx_.append(x); ny_.append(y)
            nsize.append(25 + pr.get(n, 0) * 160)
            ntext.append(n.replace(" (Bogor)", ""))
            nhover.append(f"{n}<br>PageRank: {pr.get(n,0):.4f}")
        fig_net.add_trace(go.Scatter(
            x=nx_, y=ny_, mode="markers+text",
            marker=dict(size=nsize, color=[pr.get(n, 0) for n in pos],
                        colorscale="YlOrRd", line=dict(color="white", width=1.2),
                        showscale=True, colorbar=dict(title="PageRank")),
            text=ntext, textposition="top center",
            textfont=dict(color="#E3F2FD", size=11),
            hovertext=nhover, hoverinfo="text",
        ))
        fig_net.update_layout(
            template="plotly_dark", height=520, showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_net, width="stretch")

    with colG2:
        st.markdown("**Episentrum Banjir (PageRank)**")
        g_pr = df_graph.sort_values("PageRank_Score")
        fig_pr = px.bar(
            g_pr, x="PageRank_Score", y="Kelurahan", orientation="h",
            color="PageRank_Score", color_continuous_scale="Reds",
            text=g_pr["PageRank_Score"].round(4).astype(str),
        )
        fig_pr.update_traces(textposition="outside")
        fig_pr.update_layout(
            template="plotly_dark", height=250, coloraxis_showscale=False,
            margin=dict(l=10, r=20, t=10, b=10), xaxis_title="", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pr, width="stretch")

        st.markdown("**Titik Leher Botol (In-Degree Centrality)**")
        g_in = df_graph[df_graph["In_Degree_Score"] > 0].sort_values("In_Degree_Score")
        fig_in = px.bar(
            g_in, x="In_Degree_Score", y="Kelurahan", orientation="h",
            color="In_Degree_Score", color_continuous_scale="Blues",
            text=g_in["In_Degree_Score"].round(4).astype(str),
        )
        fig_in.update_traces(textposition="outside")
        fig_in.update_layout(
            template="plotly_dark", height=250, coloraxis_showscale=False,
            margin=dict(l=10, r=20, t=10, b=10), xaxis_title="", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_in, width="stretch")

    st.info(
        "🎯 **Prioritas Intervensi:** Manggarai (PageRank 0.2302) adalah episentrum absolut, "
        "disusul Kampung Melayu (0.1872) dan Bidara Cina (0.1751). Bidara Cina & Manggarai "
        "juga merupakan leher botol pertemuan air (In-Degree 0.2500). Normalisasi sungai dan "
        "pembangunan polder sebaiknya dipusatkan di titik-titik ini."
    )

# ========================== TAB 3 : DATA & AUDIT =========================
with tab3:
    st.markdown("<div class='section-head'>Rekapitulasi Log Prediksi (Automated Audit)</div>",
                unsafe_allow_html=True)
    show = dff.copy()
    show["Status"] = np.where(show["prediction"] == 1.0, "🔴 Alarm Banjir", "🟢 Aman")
    show["Aktual"] = np.where(show["label"] == 1, "Banjir", "Aman")
    show = show.rename(columns={
        "tanggal": "Tanggal", "tp": "Curah Hujan", "sro": "Limpasan",
        "swvl1": "Kelembapan Tanah", "sp": "Tekanan",
    })
    st.dataframe(
        show[["Tanggal", "Curah Hujan", "Limpasan", "Kelembapan Tanah",
              "Tekanan", "Aktual", "Status"]].sort_values("Tanggal", ascending=False),
        width="stretch", height=440,
    )
    st.download_button(
        "⬇️ Unduh Data Terfilter (CSV)",
        data=show.to_csv(index=False).encode("utf-8"),
        file_name="log_prediksi_banjir.csv", mime="text/csv",
    )

st.divider()
st.caption(
    "Dashboard dibangun dengan Streamlit + Plotly · Rancangan Arsitektur Big Data untuk "
    "Prediksi Risiko Banjir DKI Jakarta · Nickson Yuna — 2702750104"
)
