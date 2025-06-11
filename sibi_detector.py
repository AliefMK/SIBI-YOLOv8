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
import yaml

# --- Konfigurasi ---
MODEL_PATH = "/home/ubuntu/best.pt"  # Path ke model kustom SIBI
WEBCAM_INDEX = 0  # Indeks webcam (biasanya 0 untuk webcam internal)
CONFIDENCE_THRESHOLD = 0.5  # Ambang batas kepercayaan minimum untuk deteksi

# --- Daftar label SIBI ---
# Label diambil dari data.yaml
SIBI_LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

# --- Fungsi Utama ---
def main():
    """Fungsi utama untuk menjalankan deteksi."""
    print(f"Memuat model YOLOv8 kustom SIBI dari: {MODEL_PATH}")
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

    print("Memulai deteksi bahasa isyarat SIBI real-time... Tekan 'q' untuk keluar.")
    print(f"Label SIBI yang dideteksi: {', '.join(SIBI_LABELS)}")

    while True:
        # Baca frame dari webcam
        success, frame = cap.read()

        if not success:
            print("Error: Gagal membaca frame dari webcam.", file=sys.stderr)
            break

        # Lakukan deteksi dengan YOLOv8
        # Setting stream=True direkomendasikan untuk video/streaming agar lebih efisien
        results = model(frame, stream=True, conf=CONFIDENCE_THRESHOLD, verbose=False)  # verbose=False agar tidak print log per frame

        # Proses hasil deteksi
        for r in results:
            boxes = r.boxes  # Objek Boxes untuk bounding box
            
            for box in boxes:
                # Dapatkan koordinat bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Koordinat (top-left, bottom-right)
                conf = float(box.conf[0])  # Kepercayaan deteksi
                cls_idx = int(box.cls[0])  # ID kelas
                
                # Pastikan indeks kelas valid untuk array SIBI_LABELS
                if 0 <= cls_idx < len(SIBI_LABELS):
                    label = f"{SIBI_LABELS[cls_idx]} {conf:.2f}"  # Buat label (nama kelas + kepercayaan)
                else:
                    label = f"Unknown {conf:.2f}"  # Jika indeks di luar jangkauan
                
                # Gambar bounding box pada frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Warna hijau, ketebalan 2
                
                # Tambahkan label teks
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Tampilkan frame yang sudah diproses
        cv2.imshow("Deteksi Bahasa Isyarat SIBI (YOLOv8) - Tekan 'q' untuk keluar", frame)

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
