# -*- coding: utf-8 -*-
"""
Program Python untuk Deteksi Bahasa Isyarat SIBI Real-time menggunakan YOLOv8 dan Webcam.

Program ini akan:
1. Memuat model YOLOv8 kustom yang telah dilatih untuk deteksi SIBI.
2. Mengakses feed video dari webcam.
3. Melakukan inferensi pada setiap frame untuk mendeteksi isyarat tangan.
4. Menampilkan frame video dengan bounding box dan label hasil deteksi.
5. Berhenti ketika tombol 'q' ditekan.
"""

import cv2
from ultralytics import YOLO
import sys

# --- Konfigurasi ---
MODEL_PATH = "G:/SIBI_DATASET/runs/detect/train3/weights/best.pt"  # Ganti dengan path model .pt Anda
WEBCAM_INDEX = 0  # Indeks webcam (biasanya 0 untuk webcam internal)
CONFIDENCE_THRESHOLD = 0.4 # Ambang batas kepercayaan minimum untuk deteksi

# --- Fungsi Utama ---
def main():
    """Fungsi utama untuk menjalankan deteksi."""
    print(f"Memuat model YOLOv8 dari: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
        print("Model berhasil dimuat.")
    except Exception as e:
        print(f"Error memuat model: {e}", file=sys.stderr)
        print("Pastikan path model sudah benar dan file model tidak rusak.", file=sys.stderr)
        return

    print(f"Membuka webcam dengan indeks: {WEBCAM_INDEX}")
    cap = cv2.VideoCapture(WEBCAM_INDEX)

    if not cap.isOpened():
        print(f"Error: Tidak dapat membuka webcam dengan indeks {WEBCAM_INDEX}.", file=sys.stderr)
        print("Pastikan webcam terhubung dan indeksnya benar.", file=sys.stderr)
        return

    print("Memulai deteksi real-time... Tekan 'q' untuk keluar.")

    while True:
        # Baca frame dari webcam
        success, frame = cap.read()

        if not success:
            print("Error: Gagal membaca frame dari webcam.", file=sys.stderr)
            break

        # Lakukan deteksi dengan YOLOv8
        # Setting stream=True direkomendasikan untuk video/streaming agar lebih efisien
        results = model(frame, stream=True, conf=CONFIDENCE_THRESHOLD, verbose=False) # verbose=False agar tidak print log per frame

        # Proses hasil deteksi
        for r in results:
            boxes = r.boxes # Objek Boxes untuk bounding box
            names = r.names # Nama kelas

            for box in boxes:
                # Dapatkan koordinat bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0]) # Koordinat (top-left, bottom-right)
                conf = box.conf[0] # Kepercayaan deteksi
                cls = int(box.cls[0]) # ID kelas
                label = f"{names[cls]} {conf:.2f}" # Buat label (nama kelas + kepercayaan)

                # Gambar bounding box pada frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) # Warna hijau, ketebalan 2

                # Tambahkan label teks
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Tampilkan frame yang sudah diproses
        cv2.imshow("Deteksi Bahasa Isyarat SIBI (YOLOv8) - Tekan 'q' untuk keluar", frame)

        # Cek jika tombol 

        # Cek jika tombol 'q' ditekan untuk keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Menghentikan deteksi...")
            break

    # Bebaskan sumber daya
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam dan jendela tampilan ditutup.")

if __name__ == "__main__":
    main()

