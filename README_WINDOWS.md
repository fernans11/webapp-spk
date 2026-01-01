# Web App SPK - Pemilihan Produk Sepatu Olahraga (AHP + Profile Matching)

Project web app (Windows-friendly) untuk SPK dengan:
- **AHP**: bobot kriteria (dengan cek Consistency Ratio / CR)
- **Profile Matching**: perangkingan alternatif berdasarkan kedekatan ke profil ideal

## Anti-dummy rule (sesuai syarat tugas)
Aplikasi **memaksa**:
- Setiap **Kriteria** harus punya **Judul Sumber** dan **URL Sumber** (URL publik valid).
- Setiap **Alternatif (produk sepatu)** harus punya **Judul Sumber** dan **URL Sumber** (URL publik valid).
- Menu **Hasil** hanya bisa dibuka jika:
  1) Ada kriteria & alternatif,
  2) Semua alternatif punya nilai untuk semua kriteria,
  3) AHP sudah menghasilkan bobot.

## Cara menjalankan (Windows)
1) Install Python 3.11 (64-bit).
2) Buka CMD di folder project ini.
3) Buat venv:
   python -m venv .venv
4) Aktifkan:
   .venv\Scripts\activate
5) Install dependency:
   pip install -r requirements.txt
6) Jalankan:
   python run.py
7) Buka di browser:
   http://127.0.0.1:5000

Database SQLite otomatis dibuat: `spk_sepatu.db`

## Alur input
1) Menu **Kriteria**
2) Menu **AHP**
3) Menu **Alternatif**
4) Menu **Data Alternatif**
5) Menu **Hasil**
