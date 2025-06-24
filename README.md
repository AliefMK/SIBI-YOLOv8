# SIBI Detector dengan Mode Debug

Aplikasi web untuk deteksi bahasa isyarat SIBI menggunakan YOLOv8 dengan fitur perekaman stabil, Google Text-to-Speech, dan mode debug untuk analisis performa.

## Fitur Utama

- Deteksi bahasa isyarat SIBI secara real-time menggunakan model YOLOv8 kustom
- Filter stabilitas deteksi - Hanya merekam huruf yang terdeteksi secara konsisten dalam beberapa frame berturut-turut
- Threshold kepercayaan tinggi - Menggunakan ambang batas kepercayaan untuk memastikan deteksi akurat
- Jeda deteksi optimal - Jeda antar deteksi untuk memberikan waktu stabilisasi pose tangan
- Konversi hasil deteksi menjadi audio menggunakan Google Text-to-Speech
- Riwayat deteksi dengan kemampuan memutar ulang audio
- **Mode Debug** - Menampilkan statistik performa deteksi secara real-time:
  - FPS (Frame Per Second)
  - Latensi pemrosesan per frame
  - Waktu inferensi model YOLOv8
  - Penggunaan CPU
  - Penggunaan memori
  - Confidence score rata-rata
  - Jumlah objek terdeteksi per frame

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
   cd sibi_debug
   python -m venv venv
   
   # Di Windows
   venv\Scripts\activate
   
   # Di Linux/Mac
   source venv/bin/activate
   ```

3. Instal dependensi:
   ```bash
   pip install flask opencv-python ultralytics google-cloud-texttospeech psutil
   ```

4. Pastikan file model `best.pt` berada di direktori utama aplikasi (`sibi_debug/`)

5. **Penting:** Untuk fitur Text-to-Speech, letakkan file kredensial Google Cloud Anda dengan nama `google_credentials.json` di direktori utama aplikasi (`sibi_debug/`)

## Menjalankan Aplikasi

1. Pastikan virtual environment aktif

2. Jalankan aplikasi:
   ```bash
   cd sibi_debug
   python src/main.py
   ```

3. Buka browser dan akses `http://localhost:5000`

## Cara Penggunaan

### Fitur Deteksi dan Rekaman

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

### Mode Debug

Mode debug memungkinkan Anda untuk memantau statistik performa deteksi YOLO secara real-time, yang berguna untuk analisis dan optimasi.

1. **Mengaktifkan Mode Debug:**
   - Klik tombol "Mode Debug" di bagian atas panel video
   - Tombol akan berubah warna menjadi hijau dan bertuliskan "Mode Debug: ON"
   - Panel statistik debug akan muncul di bagian bawah panel kiri
   - Overlay statistik akan muncul di video feed

2. **Memahami Statistik Debug:**
   - **FPS:** Frame Per Second - jumlah frame yang diproses per detik. Nilai lebih tinggi berarti performa lebih baik.
   - **Latensi:** Waktu total yang dibutuhkan untuk memproses satu frame (dalam milidetik). Nilai lebih rendah berarti performa lebih baik.
   - **Inferensi:** Waktu yang dibutuhkan model YOLOv8 untuk mendeteksi objek dalam satu frame (dalam milidetik). Nilai lebih rendah berarti performa lebih baik.
   - **CPU:** Persentase penggunaan CPU oleh aplikasi.
   - **Memori:** Persentase penggunaan memori oleh aplikasi.
   - **Confidence:** Nilai kepercayaan rata-rata dari deteksi. Nilai lebih tinggi berarti deteksi lebih akurat.
   - **Objek:** Jumlah objek yang terdeteksi dalam frame saat ini.

3. **Menonaktifkan Mode Debug:**
   - Klik tombol "Mode Debug: ON" untuk menonaktifkan mode debug
   - Panel statistik debug akan disembunyikan
   - Overlay statistik akan dihapus dari video feed

4. **Tips Penggunaan Mode Debug:**
   - Gunakan mode debug untuk mengidentifikasi bottleneck performa
   - Jika FPS rendah (<15), coba kurangi resolusi kamera atau gunakan komputer dengan spesifikasi lebih tinggi
   - Jika waktu inferensi tinggi (>50ms), pertimbangkan untuk menggunakan model YOLOv8 yang lebih kecil (YOLOv8n atau YOLOv8s)
   - Perhatikan penggunaan CPU dan memori untuk memastikan aplikasi tidak menggunakan terlalu banyak sumber daya

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

### Masalah Umum

- **Webcam tidak terdeteksi:** Pastikan webcam terhubung dan tidak digunakan oleh aplikasi lain
- **Model tidak dimuat:** Verifikasi path ke file model `best.pt` sudah benar
- **Error TTS:** Pastikan file kredensial Google Cloud sudah benar dan API sudah diaktifkan
- **Deteksi tidak stabil:** Coba perbaiki pencahayaan, posisi tangan, dan tahan pose lebih lama
- **Huruf tidak terekam:** Pastikan Anda menahan pose tangan cukup lama untuk memenuhi kriteria stabilitas

### Masalah Mode Debug

- **Statistik tidak muncul:** Pastikan mode debug sudah diaktifkan dengan benar
- **FPS sangat rendah:** Periksa apakah ada aplikasi lain yang menggunakan banyak sumber daya CPU/GPU
- **Statistik tidak update:** Refresh halaman browser dan aktifkan kembali mode debug
- **Nilai statistik tidak akurat:** Pastikan tidak ada proses berat lain yang berjalan di latar belakang

## Struktur Direktori

```
sibi_debug/
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

## Pengembangan Lebih Lanjut

Beberapa ide untuk pengembangan lebih lanjut:

1. Tambahkan grafik performa real-time untuk visualisasi statistik debug
2. Implementasikan fitur rekam video dengan overlay deteksi
3. Tambahkan opsi untuk menyimpan log statistik performa ke file CSV
4. Implementasikan deteksi multi-tangan untuk isyarat yang lebih kompleks
5. Tambahkan fitur kalibrasi kamera untuk meningkatkan akurasi deteksi
