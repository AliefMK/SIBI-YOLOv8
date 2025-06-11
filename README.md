# SIBI Detector Web Application

Aplikasi web untuk deteksi bahasa isyarat SIBI menggunakan YOLOv8 dengan fitur perekaman stabil dan Google Text-to-Speech.

## Fitur Utama

- Deteksi bahasa isyarat SIBI secara real-time menggunakan model YOLOv8 kustom
- **Filter stabilitas deteksi** - Hanya merekam huruf yang terdeteksi secara konsisten dalam beberapa frame berturut-turut
- **Threshold kepercayaan tinggi** - Menggunakan ambang batas kepercayaan 0.7 untuk memastikan deteksi akurat
- **Jeda deteksi optimal** - Jeda 0.8 detik antar deteksi untuk memberikan waktu stabilisasi pose tangan
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

1. Ekstrak file ke direktori pilihan Anda

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

### Fitur Deteksi Stabil

Aplikasi ini menggunakan tiga mekanisme untuk memastikan deteksi yang stabil dan akurat:

1. **Filter Stabilitas (3 Frame)** - Huruf hanya akan direkam jika terdeteksi secara konsisten dalam 3 frame berturut-turut. Ini mengurangi deteksi yang salah saat mengubah pose tangan.

2. **Threshold Kepercayaan Tinggi (0.7)** - Hanya deteksi dengan tingkat kepercayaan minimal 70% yang akan dipertimbangkan, mengurangi deteksi yang tidak akurat.

3. **Jeda Deteksi Optimal (0.8 detik)** - Sistem menunggu 0.8 detik antara deteksi huruf, memberikan waktu yang cukup untuk stabilisasi pose tangan.

### Langkah Penggunaan

1. **Melihat Deteksi Live:**
   - Saat aplikasi berjalan, Anda akan melihat tampilan live dari webcam
   - Tunjukkan isyarat tangan SIBI di depan kamera
   - Aplikasi akan mendeteksi dan menampilkan bounding box dengan label huruf
   - **Penting:** Tahan pose tangan selama beberapa detik untuk memastikan deteksi stabil

2. **Merekam Deteksi:**
   - Klik tombol "Mulai Rekam" untuk mulai merekam huruf yang terdeteksi
   - Indikator rekaman merah akan muncul di pojok kanan atas video
   - Tunjukkan isyarat tangan SIBI satu per satu
   - **Tahan setiap pose** selama minimal 2-3 detik untuk memastikan deteksi stabil
   - Tunggu hingga huruf muncul di deteksi saat ini sebelum mengubah pose
   - Klik tombol "Berhenti" untuk mengakhiri rekaman

3. **Mendengarkan Hasil:**
   - Setelah rekaman berhenti, audio akan otomatis diputar (jika fitur TTS berfungsi)
   - Kata yang terbentuk akan ditampilkan di bawah video
   - Riwayat deteksi akan ditambahkan ke panel kiri

4. **Melihat Riwayat:**
   - Panel kiri menampilkan riwayat deteksi terbaru
   - Klik pada item riwayat untuk memutar ulang audio

## Tips untuk Deteksi Optimal

- **Pencahayaan yang baik** - Pastikan area tangan Anda memiliki pencahayaan yang cukup dan merata
- **Latar belakang kontras** - Gunakan latar belakang yang kontras dengan warna kulit Anda
- **Posisi tangan yang jelas** - Pastikan tangan Anda berada di tengah frame kamera
- **Gerakan perlahan** - Ubah pose tangan dengan perlahan dan tahan setiap pose selama beberapa detik
- **Jarak optimal** - Jaga jarak sekitar 50-70 cm dari kamera

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
- **Deteksi tidak stabil:** Coba perbaiki pencahayaan, posisi tangan, dan tahan pose lebih lama
- **Huruf tidak terekam:** Pastikan Anda menahan pose tangan cukup lama (minimal 2-3 detik) untuk memenuhi kriteria stabilitas

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
