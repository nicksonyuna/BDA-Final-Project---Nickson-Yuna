# -*- coding: utf-8 -*-
"""
Render figur dashboard menjadi PNG resolusi tinggi untuk disisipkan ke laporan
(Bab 7). Figur direproduksi identik dengan komponen pada app.py Streamlit.
"""
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
FIG_DIR = os.path.join(BASE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

df_pred = pd.read_csv(os.path.join(DATA_DIR, "data_prediksi_dashboard_final.csv"))
df_pred["tanggal"] = pd.to_datetime(df_pred["tanggal"])
df_graph = pd.read_csv(os.path.join(DATA_DIR, "data_graph_dashboard.csv"))
df_fi = pd.read_csv(os.path.join(DATA_DIR, "data_feature_importance.csv"))
m = pd.read_csv(os.path.join(DATA_DIR, "data_metrics.csv")).iloc[0]

C_ACCENT, C_DANGER, C_SAFE, C_PRIMARY, C_WARN = "#1E88E5", "#D32F2F", "#2E7D32", "#0A4D8C", "#F9A825"
PAPER = "#0E1117"
SCALE = 2  # retina


def finalize(fig, name, w=1100, h=620):
    fig.update_layout(template="plotly_dark", paper_bgcolor=PAPER, plot_bgcolor=PAPER)
    fig.write_image(os.path.join(FIG_DIR, name), width=w, height=h, scale=SCALE)
    print("  saved:", name)


# ---- 0. KPI STRIP (gambar ringkasan metrik eksekutif) --------------------
total_hari = len(df_pred)
aktual = int(df_pred["label"].sum())
prediksi = int(df_pred["prediction"].sum())
kpis = [
    ("TOTAL OBSERVASI", f"{total_hari:,}", "hari teruji", C_ACCENT),
    ("BANJIR AKTUAL", f"{aktual}", "insiden", C_DANGER),
    ("ALARM PREDIKSI", f"{prediksi}", "peringatan dini", C_WARN),
    ("AKURASI", f"{m['accuracy']*100:.2f}%", "terkalibrasi", C_PRIMARY),
    ("SENSITIVITAS", f"{m['sensitivity_recall_banjir']*100:.1f}%", "recall banjir", C_SAFE),
]
fig = go.Figure()
n = len(kpis)
for i, (lab, val, sub, col) in enumerate(kpis):
    x0 = i / n + 0.01
    x1 = (i + 1) / n - 0.01
    fig.add_shape(type="rect", x0=x0, x1=x1, y0=0.05, y1=0.95,
                  fillcolor="#13293D", line=dict(color=col, width=2), layer="below")
    cx = (x0 + x1) / 2
    fig.add_annotation(x=cx, y=0.78, text=lab, showarrow=False,
                       font=dict(size=13, color="#90CAF9"))
    fig.add_annotation(x=cx, y=0.50, text=f"<b>{val}</b>", showarrow=False,
                       font=dict(size=34, color="#FFFFFF"))
    fig.add_annotation(x=cx, y=0.24, text=sub, showarrow=False,
                       font=dict(size=12, color=col))
fig.update_xaxes(visible=False, range=[0, 1])
fig.update_yaxes(visible=False, range=[0, 1])
fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
finalize(fig, "fig_kpi.png", w=1300, h=230)

# ---- 1. CONFUSION MATRIX --------------------------------------------------
cm = np.array([[int(m["tn"]), int(m["fp"])], [int(m["fn"]), int(m["tp"])]])
fig = go.Figure(data=go.Heatmap(
    z=cm, x=["Prediksi Aman", "Prediksi Banjir"], y=["Aktual Aman", "Aktual Banjir"],
    text=cm, texttemplate="%{text}", textfont={"size": 40, "color": "white"},
    colorscale="Blues", showscale=False))
fig.update_layout(title="Confusion Matrix - Deteksi Banjir (Spark MLlib)",
                  margin=dict(l=20, r=20, t=60, b=20))
finalize(fig, "fig_confusion_matrix.png", w=760, h=620)

# ---- 2. FEATURE IMPORTANCE ------------------------------------------------
fi = df_fi.sort_values("Bobot")
fig = px.bar(fi, x="Bobot", y="Fitur", orientation="h", color="Bobot",
             color_continuous_scale="Teal",
             text=(fi["Bobot"] * 100).round(2).astype(str) + "%")
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(title="Tingkat Kepentingan Fitur Pemicu Banjir",
                  coloraxis_showscale=False, xaxis_title="Bobot Pengaruh",
                  yaxis_title="", margin=dict(l=20, r=90, t=60, b=20),
                  xaxis=dict(range=[0, 0.19]))
finalize(fig, "fig_feature_importance.png", w=900, h=560)

# ---- 3. METRIK EVALUASI ---------------------------------------------------
met = pd.DataFrame({
    "Metrik": ["Accuracy", "F1-Score", "Weighted Precision", "Weighted Recall"],
    "Nilai": [m["accuracy"], m["f1"], m["weighted_precision"], m["weighted_recall"]]})
fig = px.bar(met, x="Metrik", y="Nilai", color="Metrik",
             text=(met["Nilai"] * 100).round(2).astype(str) + "%",
             color_discrete_sequence=[C_ACCENT, C_SAFE, C_PRIMARY, C_WARN])
fig.update_traces(textposition="outside")
fig.update_layout(title="Ringkasan Metrik Evaluasi Model",
                  showlegend=False, yaxis=dict(range=[0, 1], title="Skor"),
                  xaxis_title="", margin=dict(l=20, r=20, t=60, b=20))
finalize(fig, "fig_metrics.png", w=900, h=480)

# ---- 4. TIME SERIES SRO ---------------------------------------------------
ts = df_pred.sort_values("tanggal")
fig = px.line(ts, x="tanggal", y="sro",
              labels={"sro": "Volume Limpasan (sro)", "tanggal": "Tanggal"})
fig.update_traces(line_color=C_ACCENT, line_width=1.1)
alarm = ts[ts["prediction"] == 1.0]
fig.add_scatter(x=alarm["tanggal"], y=alarm["sro"], mode="markers",
                marker=dict(color=C_DANGER, size=6), name="Alarm Banjir")
fig.update_layout(title=dict(text="Tren Limpasan Permukaan vs Alarm Banjir", y=0.97),
                  legend=dict(orientation="h", y=1.14, x=0.5, xanchor="center"),
                  margin=dict(l=20, r=20, t=95, b=20))
finalize(fig, "fig_timeseries.png", w=1200, h=520)

# ---- 5. NETWORK GRAPH -----------------------------------------------------
edges = [("Katulampa (Bogor)", "Depok"), ("Depok", "Pejaten Timur"),
         ("Pejaten Timur", "Cawang"), ("Cawang", "Bidara Cina"),
         ("Cililitan", "Bidara Cina"), ("Bidara Cina", "Kampung Melayu"),
         ("Kampung Melayu", "Manggarai"), ("Bukit Duri", "Manggarai")]
pos = {"Katulampa (Bogor)": (0.1, 1.00), "Depok": (0.1, 0.80),
       "Pejaten Timur": (0.1, 0.60), "Cawang": (0.25, 0.42),
       "Cililitan": (0.55, 0.42), "Bidara Cina": (0.40, 0.26),
       "Bukit Duri": (0.75, 0.14), "Kampung Melayu": (0.40, 0.10),
       "Manggarai": (0.57, -0.05)}
pr = dict(zip(df_graph["Kelurahan"], df_graph["PageRank_Score"]))
edge_x, edge_y = [], []
for a, b in edges:
    edge_x += [pos[a][0], pos[b][0], None]
    edge_y += [pos[a][1], pos[b][1], None]
fig = go.Figure()
fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines",
              line=dict(color="rgba(211,47,47,0.55)", width=2.5), hoverinfo="none"))
nx_, ny_, nsize, ntext = [], [], [], []
for nname, (x, y) in pos.items():
    nx_.append(x); ny_.append(y)
    nsize.append(30 + pr.get(nname, 0) * 200)
    ntext.append(nname.replace(" (Bogor)", ""))
fig.add_trace(go.Scatter(
    x=nx_, y=ny_, mode="markers+text",
    marker=dict(size=nsize, color=[pr.get(nn, 0) for nn in pos],
                colorscale="YlOrRd", line=dict(color="white", width=1.5),
                showscale=True, colorbar=dict(title="PageRank")),
    text=ntext, textposition="top center", textfont=dict(color="#E3F2FD", size=13)))
fig.update_layout(title="Topologi Rambatan Air DAS Ciliwung (ukuran node = PageRank)",
                  showlegend=False, xaxis=dict(visible=False),
                  yaxis=dict(visible=False), margin=dict(l=20, r=20, t=60, b=20))
finalize(fig, "fig_network.png", w=1000, h=720)

# ---- 6. PAGERANK & IN-DEGREE BARS ----------------------------------------
g_pr = df_graph.sort_values("PageRank_Score")
fig = px.bar(g_pr, x="PageRank_Score", y="Kelurahan", orientation="h",
             color="PageRank_Score", color_continuous_scale="Reds",
             text=g_pr["PageRank_Score"].round(4).astype(str))
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(title="Episentrum Banjir Berdasarkan PageRank",
                  coloraxis_showscale=False, xaxis_title="Skor PageRank",
                  yaxis_title="", margin=dict(l=20, r=70, t=60, b=20),
                  xaxis=dict(range=[0, 0.27]))
finalize(fig, "fig_pagerank.png", w=900, h=520)

g_in = df_graph[df_graph["In_Degree_Score"] > 0].sort_values("In_Degree_Score")
fig = px.bar(g_in, x="In_Degree_Score", y="Kelurahan", orientation="h",
             color="In_Degree_Score", color_continuous_scale="Blues",
             text=g_in["In_Degree_Score"].round(4).astype(str))
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(title="Titik Leher Botol (In-Degree Centrality)",
                  coloraxis_showscale=False, xaxis_title="Skor In-Degree",
                  yaxis_title="", margin=dict(l=20, r=70, t=60, b=20),
                  xaxis=dict(range=[0, 0.30]))
finalize(fig, "fig_indegree.png", w=900, h=460)

print("\nSemua figur tersimpan di:", FIG_DIR)
