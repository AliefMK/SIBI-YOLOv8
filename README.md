# SIBI Detector Web Application

Aplikasi web untuk deteksi bahasa isyarat SIBI menggunakan YOLOv8 dengan fitur perekaman dan Google Text-to-Speech.

## Fitur Utama

- Deteksi bahasa isyarat SIBI secara real-time menggunakan model YOLOv8 kustom
- Tampilan live view dari webcam dengan bounding box deteksi
- Fitur rekam untuk mengumpulkan huruf-huruf yang terdeteksi
- Konversi hasil deteksi menjadi audio menggunakan Google Text-to-Speech
- Riwayat deteksi dengan kemampuan memutar ulang audio
- Antarmuka pengguna modern dengan dark theme

## Prasyarat

Sebelum menjalankan aplikasi, pastikan Anda memiliki:

1. Python 3.8 atau lebih baru
2. Webcam yang terhubung dan berfungsi
3. File model YOLOv8 kustom untuk deteksi SIBI (`best.pt`)
4. File kredensial Google Cloud untuk Text-to-Speech API

## Instalasi

1. Clone repositori ini atau ekstrak file ke direktori pilihan Anda

2. Buat dan aktifkan virtual environment:
   ```bash
   cd sibi_flask_app
   python -m venv venv
   
   # Di Windows
   venv\Scripts\activate
   
   # Di Linux/Mac
   source venv/bin/activate
   ```

3. Instal dependensi:
   ```bash
   pip install flask opencv-python ultralytics google-cloud-texttospeech
   ```

4. Pastikan file model `best.pt` berada di direktori utama aplikasi (`sibi_flask_app/`)

5. **Penting:** Untuk fitur Text-to-Speech, letakkan file kredensial Google Cloud Anda dengan nama `google_credentials.json` di direktori utama aplikasi (`sibi_flask_app/`)

## Menjalankan Aplikasi

1. Pastikan virtual environment aktif

2. Jalankan aplikasi:
   ```bash
   cd sibi_flask_app
   python src/main.py
   ```

3. Buka browser dan akses `http://localhost:5000`

## Cara Penggunaan

1. **Melihat Deteksi Live:**
   - Saat aplikasi berjalan, Anda akan melihat tampilan live dari webcam
   - Tunjukkan isyarat tangan SIBI di depan kamera
   - Aplikasi akan mendeteksi dan menampilkan bounding box dengan label huruf

2. **Merekam Deteksi:**
   - Klik tombol "Mulai Rekam" untuk mulai merekam huruf yang terdeteksi
   - Indikator rekaman merah akan muncul di pojok kanan atas video
   - Tunjukkan isyarat tangan SIBI satu per satu
   - Klik tombol "Berhenti" untuk mengakhiri rekaman

3. **Mendengarkan Hasil:**
   - Setelah rekaman berhenti, audio akan otomatis diputar (jika fitur TTS berfungsi)
   - Kata yang terbentuk akan ditampilkan di bawah video
   - Riwayat deteksi akan ditambahkan ke panel kiri

4. **Melihat Riwayat:**
   - Panel kiri menampilkan riwayat deteksi terbaru
   - Klik pada item riwayat untuk memutar ulang audio

## Mendapatkan Kredensial Google Cloud

Untuk menggunakan fitur Text-to-Speech, Anda memerlukan kredensial Google Cloud:

1. Buat akun Google Cloud Platform (GCP) jika belum memilikinya
2. Buat project baru di GCP Console
3. Aktifkan Text-to-Speech API untuk project tersebut
4. Buat service account dan download file kredensial JSON
5. Rename file tersebut menjadi `google_credentials.json` dan letakkan di direktori utama aplikasi

## Troubleshooting

- **Webcam tidak terdeteksi:** Pastikan webcam terhubung dan tidak digunakan oleh aplikasi lain
- **Model tidak dimuat:** Verifikasi path ke file model `best.pt` sudah benar
- **Error TTS:** Pastikan file kredensial Google Cloud sudah benar dan API sudah diaktifkan
- **Deteksi tidak akurat:** Coba perbaiki pencahayaan dan posisi tangan Anda

## Struktur Direktori

```
sibi_flask_app/
├── best.pt                    # File model YOLOv8 kustom
├── google_credentials.json    # File kredensial Google Cloud (harus ditambahkan)
├── venv/                      # Virtual environment
└── src/
    ├── main.py                # File utama aplikasi Flask
    ├── static/
    │   ├── css/
    │   │   └── style.css      # Stylesheet
    │   ├── js/
    │   │   └── script.js      # JavaScript untuk interaktivitas
    │   └── audio/             # Direktori untuk file audio hasil TTS
    └── templates/
        └── index.html         # Template halaman utama
```
