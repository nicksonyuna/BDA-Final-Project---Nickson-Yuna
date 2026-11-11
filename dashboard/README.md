# Executive Dashboard — Sistem Peringatan Dini Banjir DKI Jakarta

Dashboard interaktif untuk merepresentasikan temuan **Bab 5 (Machine Learning)** dan
**Bab 6 (Graph Analytics)** dari laporan *Rancangan Arsitektur Big Data untuk Prediksi
Risiko Banjir di DKI Jakarta*.

## Isi Folder

| Berkas | Keterangan |
|---|---|
| `app.py` | Aplikasi dashboard Streamlit (KPI, Confusion Matrix, Feature Importance, Time-Series, Graph Analytics, Audit) |
| `generate_data.py` | Membuat dataset dashboard yang mereplikasi metrik pada laporan |
| `render_figures.py` | Merender tiap panel dashboard menjadi PNG resolusi tinggi |
| `compose_overview.py` | Menyusun komposit tampilan dashboard (Gambar 7.1) |
| `compose_graph.py` | Menyusun komposit panel Graph Analytics (Gambar 7.2) |
| `data/` | Dataset CSV antara (hasil ekspor analitik) |
| `figures/` | Gambar hasil render yang disisipkan ke dokumen |

## Cara Menjalankan

```powershell
# 1. Pasang dependensi (sekali saja)
pip install streamlit plotly pandas numpy kaleido

# 2. Siapkan dataset (sekali saja, atau saat ingin memperbarui data)
python generate_data.py

# 3. Jalankan dashboard
python -m streamlit run app.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`.

## Memperbarui Gambar untuk Laporan

```powershell
python render_figures.py      # render ulang semua panel
python compose_overview.py    # komposit Gambar 7.1
python compose_graph.py       # komposit Gambar 7.2
```

## Catatan Data

Dataset pada folder `data/` dikalibrasi agar konsisten dengan metrik laporan:

- **Confusion Matrix (Spark MLlib):** TN=359, FP=233, FN=20, TP=65
- **Akurasi:** 62,63% · **F1-Score:** 68,92% · **Sensitivitas banjir:** 76,5%
- **Feature Importance:** sro (16,35%), u10 (14,11%), tp (13,59%), dst.
- **PageRank:** Manggarai (0,2302), Kampung Melayu (0,1872), Bidara Cina (0,1751)
- **In-Degree Centrality:** Manggarai & Bidara Cina (0,2500)

Untuk menghubungkan dengan data riil Spark, ganti isi folder `data/` dengan
`data_prediksi_dashboard_final.csv` dan `data_graph_dashboard.csv` hasil ekspor dari
Google Colab (`assignment_bda_data.py`).
