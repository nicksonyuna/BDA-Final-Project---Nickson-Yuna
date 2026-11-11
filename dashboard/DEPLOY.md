# Cara Men-deploy Dashboard ke Link Publik (Streamlit Community Cloud)

Hasil akhir: link permanen gratis seperti `https://namaapp.streamlit.app`
yang bisa diakses siapa saja tanpa komputer Anda harus menyala.

Semua berkas pendukung (requirements.txt, config, .gitignore) sudah disiapkan.

---

## Langkah 1 — Buat akun (sekali saja)
1. Daftar GitHub gratis: https://github.com/signup
2. Daftar Streamlit (login pakai GitHub): https://share.streamlit.io

## Langkah 2 — Upload folder `dashboard` ke GitHub

### Cara A: Lewat Website GitHub (paling mudah, tanpa perintah)
1. Buka https://github.com/new
2. Isi **Repository name**, contoh: `dashboard-banjir-jakarta`
3. Pilih **Public**, lalu klik **Create repository**
4. Di halaman repo baru, klik **"uploading an existing file"**
5. Seret (drag) SELURUH ISI folder `dashboard` ke jendela browser
   (app.py, generate_data.py, requirements.txt, folder data/, dll.)
6. Klik **Commit changes**

### Cara B: Lewat Git (jika Anda terbiasa terminal)
Jalankan di dalam folder `dashboard`:
```powershell
git init
git add app.py generate_data.py render_figures.py compose_overview.py compose_graph.py requirements.txt README.md .gitignore .streamlit data
git commit -m "Dashboard mitigasi banjir DKI Jakarta"
git branch -M main
git remote add origin https://github.com/USERNAME/dashboard-banjir-jakarta.git
git push -u origin main
```
(Ganti `USERNAME` dengan nama pengguna GitHub Anda.)

## Langkah 3 — Deploy di Streamlit Cloud
1. Buka https://share.streamlit.io
2. Klik **Create app** → **Deploy a public app from GitHub**
3. Isi:
   - **Repository:** `USERNAME/dashboard-banjir-jakarta`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. (Opsional) klik **Advanced settings** → pilih **Python 3.12**
5. Klik **Deploy**

Tunggu 2-4 menit saat Streamlit memasang dependensi. Setelah selesai, Anda
mendapat link publik permanen yang bisa langsung dibagikan ke dosen.

---

## Catatan
- Setiap kali Anda memperbarui kode di GitHub, dashboard online ikut ter-update
  otomatis.
- Folder `data/` WAJIB ikut di-upload. Jika lupa, aplikasi akan membuat ulang
  data secara otomatis saat pertama dijalankan (sudah ada mekanisme cadangan di
  `app.py`), tetapi lebih aman jika CSV ikut terunggah.
- Folder `figures/` TIDAK perlu di-upload (hanya untuk laporan Word).
