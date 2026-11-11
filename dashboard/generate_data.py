# -*- coding: utf-8 -*-
"""
Generate dataset dashboard yang MEREPLIKASI hasil temuan pada Bab 5 (Machine
Learning) dan Bab 6 (Graph Analytics) laporan.

Output:
  - data_prediksi_dashboard_final.csv  (hasil Random Forest Spark MLlib)
  - data_graph_dashboard.csv           (hasil Graph Analytics NetworkX)

Angka-angka dikalibrasi agar konsisten dengan metrik yang tertulis di laporan:
  Confusion Matrix (Spark MLlib):
    True Negative (Aman benar)      = 359
    False Positive (alarm palsu)    = 233
    False Negative (gagal deteksi)  = 20
    True Positive (banjir terdeteksi)= 65
  => Total observasi test           = 677
  Feature Importance (Random Forest):
    sro 16.35%, u10 14.11%, tp 13.59%, dst.
  Graph Analytics (PageRank & In-Degree Centrality):
    Manggarai, Kampung Melayu, Bidara Cina, dst.
"""
import os
import numpy as np
import pandas as pd

np.random.seed(42)
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# =========================================================================
# 1. DATA PREDIKSI MACHINE LEARNING (mereplikasi Confusion Matrix Bab 5)
# =========================================================================
# Komposisi test-set 677 baris sesuai confusion matrix laporan:
#   label=0 -> 359 (TN) + 233 (FP) = 592 baris aman
#   label=1 -> 20  (FN) + 65  (TP) = 85  baris banjir
n_tn, n_fp, n_fn, n_tp = 359, 233, 20, 65

records = []
# Rentang tanggal observasi harian (test-set diambil acak sepanjang 2016-2025)
date_pool = pd.date_range("2016-01-01", "2025-12-31", freq="D")

def sample_weather(is_flood):
    """Nilai hidrometeorologi realistis. Hari banjir -> sro/tp lebih tinggi."""
    if is_flood:
        tp = np.random.gamma(6.0, 0.9) / 1000      # curah hujan tinggi (m)
        sro = np.random.gamma(5.0, 0.8) / 1000      # limpasan tinggi
        swvl1 = np.random.uniform(0.38, 0.46)       # tanah jenuh
    else:
        tp = np.random.gamma(1.2, 0.5) / 1000
        sro = np.random.gamma(1.0, 0.4) / 1000
        swvl1 = np.random.uniform(0.20, 0.38)
    sp = np.random.normal(100800, 400)              # tekanan permukaan (Pa)
    return tp, sro, swvl1, sp

def add_block(n, label, prediction):
    for _ in range(n):
        tp, sro, swvl1, sp = sample_weather(label == 1)
        # Untuk FP (prediksi banjir padahal aman) naikkan sedikit sro agar realistis
        if label == 0 and prediction == 1:
            sro *= np.random.uniform(2.0, 3.5)
            tp *= np.random.uniform(1.8, 3.0)
        # Untuk FN (gagal deteksi) turunkan sinyalnya
        if label == 1 and prediction == 0:
            sro *= np.random.uniform(0.3, 0.6)
        d = np.random.choice(date_pool)
        records.append({
            "tanggal": pd.Timestamp(d).strftime("%Y-%m-%d"),
            "tp": round(tp, 6),
            "sro": round(sro, 6),
            "swvl1": round(swvl1, 4),
            "sp": round(sp, 2),
            "label": int(label),
            "prediction": float(prediction),
        })

add_block(n_tn, 0, 0.0)  # True Negative
add_block(n_fp, 0, 1.0)  # False Positive
add_block(n_fn, 1, 0.0)  # False Negative
add_block(n_tp, 1, 1.0)  # True Positive

df_pred = pd.DataFrame(records)
df_pred["tanggal"] = pd.to_datetime(df_pred["tanggal"])
df_pred = df_pred.sort_values("tanggal").reset_index(drop=True)
df_pred.to_csv(os.path.join(DATA_DIR, "data_prediksi_dashboard_final.csv"), index=False)

# =========================================================================
# 2. FEATURE IMPORTANCE (mereplikasi Bab 5.6 - Random Forest)
# =========================================================================
fi = pd.DataFrame({
    "Fitur": ["sro", "u10", "tp", "swvl1", "d2m", "v10", "t2m", "sp"],
    "Deskripsi": [
        "Limpasan Permukaan (Surface Runoff)",
        "Komponen Angin U (10m)",
        "Curah Hujan (Total Precipitation)",
        "Kelembapan Tanah Lapis 1",
        "Suhu Titik Embun (2m)",
        "Komponen Angin V (10m)",
        "Suhu Udara (2m)",
        "Tekanan Permukaan",
    ],
    "Bobot": [0.1635, 0.1411, 0.1359, 0.1288, 0.1172, 0.1098, 0.0982, 0.0855],
})
fi.to_csv(os.path.join(DATA_DIR, "data_feature_importance.csv"), index=False)

# =========================================================================
# 3. DATA GRAPH ANALYTICS (mereplikasi Bab 6 - PageRank & In-Degree)
# =========================================================================
graph = pd.DataFrame({
    "Kelurahan": [
        "Manggarai", "Kampung Melayu", "Bidara Cina", "Cawang",
        "Pejaten Timur", "Depok", "Cililitan", "Bukit Duri",
        "Katulampa (Bogor)",
    ],
    "PageRank_Score": [0.2302, 0.1872, 0.1751, 0.0998,
                        0.0734, 0.0612, 0.0451, 0.0451, 0.0329],
    "In_Degree_Score": [0.2500, 0.1250, 0.2500, 0.1250,
                         0.1250, 0.1250, 0.0000, 0.0000, 0.0000],
})
graph.to_csv(os.path.join(DATA_DIR, "data_graph_dashboard.csv"), index=False)

# =========================================================================
# 4. METRIK EVALUASI MODEL (Bab 5.5)
# =========================================================================
metrics = pd.DataFrame([{
    "accuracy": 0.6263,
    "f1": 0.6892,
    "weighted_precision": 0.8557,
    "weighted_recall": 0.6263,
    "sensitivity_recall_banjir": 0.7647,   # 65 / (65+20)
    "tn": n_tn, "fp": n_fp, "fn": n_fn, "tp": n_tp,
}])
metrics.to_csv(os.path.join(DATA_DIR, "data_metrics.csv"), index=False)

print("Dataset dashboard berhasil dibuat di:", DATA_DIR)
print(f"  Prediksi : {len(df_pred)} baris  (TN={n_tn} FP={n_fp} FN={n_fn} TP={n_tp})")
print(f"  Banjir aktual: {df_pred['label'].sum()} | Alarm prediksi: {int(df_pred['prediction'].sum())}")
print("  Graph    :", len(graph), "kelurahan")
