# Instruksi Menjalankan Program Deteksi Bahasa Isyarat SIBI (YOLOv8)

Berikut adalah langkah-langkah untuk menjalankan program Python `sibi_detector_updated.py` yang telah dibuat:

## Prasyarat

1.  **Python 3:** Pastikan Anda telah menginstal Python 3 (versi 3.8 atau lebih baru direkomendasikan) di komputer Anda.
2.  **pip:** Pastikan pip (package installer for Python) sudah terinstal dan terbarui.
3.  **Webcam:** Pastikan komputer Anda memiliki webcam yang terhubung dan berfungsi.
4.  **File Model:** Anda memerlukan file model YOLOv8 kustom (`best.pt`) yang telah dilatih untuk deteksi SIBI.

## Langkah-langkah Instalasi dan Menjalankan

1.  **Unduh File:**
    *   Unduh file skrip Python `sibi_detector_updated.py`.
    *   Unduh file model kustom `best.pt`.
    *   Pastikan kedua file berada di direktori yang sama, atau sesuaikan path di dalam kode.

2.  **Buka Terminal atau Command Prompt:**
    *   Buka terminal (Linux/macOS) atau Command Prompt (Windows).
    *   Navigasikan ke direktori tempat Anda menyimpan file `sibi_detector_updated.py` dan file model `best.pt` menggunakan perintah `cd`.
      ```bash
      cd path/ke/direktori/anda
      ```

3.  **Instal Dependensi:**
    *   Jalankan perintah berikut untuk menginstal pustaka Python yang diperlukan (ultralytics dan OpenCV):
      ```bash
      pip install ultralytics opencv-contrib-python
      ```
    *   Tunggu hingga proses instalasi selesai. Ini mungkin memerlukan waktu beberapa saat tergantung pada koneksi internet Anda.
    *   **Penting:** Gunakan `opencv-contrib-python` bukan `opencv-python` untuk menghindari error GUI pada Windows.

4.  **Sesuaikan Konfigurasi (Jika Perlu):**
    *   Buka file `sibi_detector_updated.py` dengan editor teks.
    *   Jika lokasi file model Anda berbeda, ubah nilai variabel `MODEL_PATH`:
      ```python
      MODEL_PATH = "path/lengkap/ke/best.pt"
      ```
    *   Jika Anda memiliki lebih dari satu webcam dan ingin menggunakan webcam yang berbeda, ubah nilai `WEBCAM_INDEX`. Biasanya 0 adalah webcam internal, 1 adalah webcam eksternal pertama, dan seterusnya.
      ```python
      WEBCAM_INDEX = 1 # Contoh jika ingin menggunakan webcam kedua
      ```
    *   Anda juga bisa menyesuaikan `CONFIDENCE_THRESHOLD` (antara 0 dan 1) untuk mengatur sensitivitas deteksi. Nilai yang lebih rendah akan mendeteksi lebih banyak objek tetapi mungkin juga lebih banyak hasil yang salah.

5.  **Jalankan Skrip:**
    *   Kembali ke terminal atau Command Prompt.
    *   Jalankan skrip Python dengan perintah:
      ```bash
      python sibi_detector_updated.py
      ```

6.  **Lihat Hasil Deteksi:**
    *   Sebuah jendela baru akan muncul menampilkan feed langsung dari webcam Anda.
    *   Jika isyarat tangan SIBI terdeteksi, Anda akan melihat kotak pembatas (bounding box) berwarna hijau di sekitarnya, beserta label huruf SIBI (A-Y, tanpa J dan Z) dan tingkat kepercayaannya.

7.  **Keluar dari Program:**
    *   Untuk menghentikan program, klik pada jendela tampilan video dan tekan tombol `q` pada keyboard Anda.

## Troubleshooting

*   **Error: Tidak dapat membuka webcam:** Pastikan webcam terhubung dengan benar, driver terinstal, dan tidak sedang digunakan oleh aplikasi lain. Coba ubah `WEBCAM_INDEX`.
*   **Error memuat model:** Pastikan path ke file `best.pt` di variabel `MODEL_PATH` sudah benar dan file model tidak rusak.
*   **Error GUI/cv2.imshow:** Jika Anda mendapatkan error terkait GUI atau cv2.imshow, pastikan Anda menginstal `opencv-contrib-python` dan bukan versi headless dari OpenCV.
*   **Deteksi lambat:** Deteksi objek secara real-time membutuhkan sumber daya komputasi. Jika performa lambat, coba tutup aplikasi lain yang tidak perlu atau pertimbangkan menggunakan komputer dengan spesifikasi lebih tinggi (terutama GPU jika model mendukung akselerasi CUDA).
*   **Tidak ada deteksi / deteksi tidak akurat:** Ini mungkin terkait dengan kondisi pencahayaan, atau posisi tangan terhadap webcam. Pastikan tangan Anda terlihat jelas dan coba berbagai posisi dan pencahayaan.

## Informasi Label SIBI

Program ini dilatih untuk mendeteksi 24 huruf bahasa isyarat SIBI:
A, B, C, D, E, F, G, H, I, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y (tanpa J dan Z)

Semoga berhasil menjalankan program deteksi bahasa isyarat SIBI!
