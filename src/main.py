import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import psutil
import threading
import json
import uuid
import numpy as np
from collections import deque
from ultralytics import YOLO
from google.cloud import texttospeech

app = Flask(__name__)

# Konfigurasi
MODEL_PATH = "G:/Github/SIBI/SIBI-YOLOv8/best.pt"  # Path disesuaikan dengan lokasi di server
CONFIDENCE_THRESHOLD = 0.55
DETECTION_DELAY = 0.8
STABILITY_FRAMES = 5

# Daftar label SIBI
SIBI_LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

# Variabel global
camera = None
output_frame = None
lock = threading.Lock()
is_recording = False
recorded_letters = []
model = None
last_detection_time = 0
detection_history = {}
debug_mode = False

# Variabel untuk statistik debug
debug_stats = {
    'fps': 0,
    'latency': 0,
    'inference_time': 0,
    'cpu_percent': 0,
    'memory_percent': 0,
    'avg_confidence': 0,
    'objects_detected': 0,
    'frame_count': 0,
    'processing_times': deque(maxlen=30),  # Menyimpan 30 waktu pemrosesan terakhir untuk perhitungan FPS
    'confidence_scores': deque(maxlen=30),  # Menyimpan 30 confidence score terakhir
}

def initialize():
    global model
    try:
        model = YOLO(MODEL_PATH)
        print(f"Model berhasil dimuat dari: {MODEL_PATH}")
    except Exception as e:
        print(f"Error memuat model: {e}")
        model = None

def text_to_speech(text, output_filename):
    try:
        # Cek apakah file kredensial ada
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "google_credentials.json")
        if not os.path.exists(credentials_path):
            print(f"File kredensial Google Cloud tidak ditemukan di: {credentials_path}")
            return False
            
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        client = texttospeech.TextToSpeechClient()
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="id-ID",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        with open(output_filename, "wb") as out:
            out.write(response.audio_content)
            print(f"Audio content written to file: {output_filename}")
        
        return True
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return False

def update_debug_stats():
    """Update statistik CPU dan memori untuk mode debug"""
    global debug_stats
    
    # Update statistik CPU dan memori
    debug_stats['cpu_percent'] = psutil.cpu_percent()
    debug_stats['memory_percent'] = psutil.virtual_memory().percent
    
    # Hitung FPS dari waktu pemrosesan
    if len(debug_stats['processing_times']) > 1:
        # FPS = 1 / waktu_pemrosesan_rata_rata
        avg_processing_time = sum(debug_stats['processing_times']) / len(debug_stats['processing_times'])
        debug_stats['fps'] = 1.0 / avg_processing_time if avg_processing_time > 0 else 0
    
    # Hitung confidence score rata-rata
    if len(debug_stats['confidence_scores']) > 0:
        debug_stats['avg_confidence'] = sum(debug_stats['confidence_scores']) / len(debug_stats['confidence_scores'])

def detect_sibi_in_frame(frame):
    global model, detection_history, debug_stats, debug_mode
    
    if model is None:
        return frame, None
    
    # Waktu mulai untuk pengukuran latensi dan waktu inferensi
    start_time = time.time()
    inference_start = time.time()
    
    # Lakukan deteksi dengan YOLOv8
    results = model(frame, stream=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    # Waktu selesai inferensi
    inference_time = time.time() - inference_start
    
    detected_letters = []
    current_detections = {}
    confidence_scores = []
    objects_count = 0
    
    # Proses hasil deteksi
    for r in results:
        boxes = r.boxes
        objects_count = len(boxes)  # Jumlah objek terdeteksi
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_idx = int(box.cls[0])
            
            # Tambahkan confidence score untuk perhitungan rata-rata
            confidence_scores.append(conf)
            
            if 0 <= cls_idx < len(SIBI_LABELS):
                letter = SIBI_LABELS[cls_idx]
                label = f"{letter} {conf:.2f}"
                
                if letter in current_detections:
                    if conf > current_detections[letter]['conf']:
                        current_detections[letter] = {'conf': conf, 'box': (x1, y1, x2, y2)}
                else:
                    current_detections[letter] = {'conf': conf, 'box': (x1, y1, x2, y2)}
            else:
                label = f"Unknown {conf:.2f}"
    
    # Update history deteksi dan gambar bounding box
    for letter, data in current_detections.items():
        # Update history deteksi
        if letter not in detection_history:
            detection_history[letter] = 1
        else:
            detection_history[letter] += 1
        
        # Jika deteksi stabil (terdeteksi dalam beberapa frame berturut-turut)
        if detection_history[letter] >= STABILITY_FRAMES:
            detected_letters.append(letter)
            
            # Gambar bounding box pada frame
            x1, y1, x2, y2 = data['box']
            conf = data['conf']
            label = f"{letter} {conf:.2f}"
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Reset history untuk huruf yang tidak terdeteksi di frame saat ini
    for letter in list(detection_history.keys()):
        if letter not in current_detections:
            detection_history[letter] = 0
            # Hapus dari history jika sudah tidak terdeteksi lagi
            if detection_history[letter] <= 0:
                del detection_history[letter]
    
    # Waktu selesai untuk pengukuran latensi
    end_time = time.time()
    latency = end_time - start_time
    
    # Update statistik debug jika mode debug aktif
    if debug_mode:
        debug_stats['latency'] = latency
        debug_stats['inference_time'] = inference_time
        debug_stats['processing_times'].append(latency)
        debug_stats['objects_detected'] = objects_count
        debug_stats['frame_count'] += 1
        
        if confidence_scores:
            debug_stats['confidence_scores'].extend(confidence_scores)
        
        # Update statistik CPU dan memori setiap 10 frame
        if debug_stats['frame_count'] % 10 == 0:
            update_debug_stats()
        
        # Tambahkan overlay statistik debug ke frame
        if debug_mode:
            add_debug_overlay(frame)
    
    return frame, detected_letters

def add_debug_overlay(frame):
    """Tambahkan overlay statistik debug ke frame"""
    # Buat background semi-transparan untuk teks
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (300, 160), (0, 0, 0), -1)
    alpha = 0.7  # Transparansi
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Tambahkan statistik ke frame
    cv2.putText(frame, f"FPS: {debug_stats['fps']:.2f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.putText(frame, f"Latency: {debug_stats['latency']*1000:.2f} ms", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.putText(frame, f"Inference: {debug_stats['inference_time']*1000:.2f} ms", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.putText(frame, f"CPU: {debug_stats['cpu_percent']:.1f}%", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.putText(frame, f"Memory: {debug_stats['memory_percent']:.1f}%", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.putText(frame, f"Avg Conf: {debug_stats['avg_confidence']:.2f}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.putText(frame, f"Objects: {debug_stats['objects_detected']}", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

def generate_frames():
    global output_frame, lock, is_recording, recorded_letters, camera, last_detection_time
    
    if camera is None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("Error: Tidak dapat membuka webcam.")
            return
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Deteksi SIBI pada frame
        processed_frame, detected_letters = detect_sibi_in_frame(frame)
        
        # Jika sedang merekam, tambahkan huruf yang terdeteksi dengan jeda
        current_time = time.time()
        if is_recording and detected_letters:
            if current_time - last_detection_time >= DETECTION_DELAY:
                for letter in detected_letters:
                    if not recorded_letters or recorded_letters[-1] != letter:
                        recorded_letters.append(letter)
                        last_detection_time = current_time
                        break  # Hanya tambahkan satu huruf per interval waktu
        
        # Tambahkan indikator rekaman jika sedang merekam
        if is_recording:
            cv2.circle(processed_frame, (30, 30), 15, (0, 0, 255), -1)  # Lingkaran merah
            cv2.putText(processed_frame, "Recording", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        
        # Encode frame sebagai JPEG
        with lock:
            output_frame = processed_frame.copy()
        
        # Konversi frame ke format JPEG
        ret, buffer = cv2.imencode('.jpg', output_frame)
        frame_bytes = buffer.tobytes()
        
        # Yield frame untuk streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Beri waktu untuk thread lain
        time.sleep(0.01)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording, recorded_letters, last_detection_time, detection_history
    is_recording = True
    recorded_letters = []
    last_detection_time = time.time()
    detection_history = {}  # Reset history deteksi saat mulai merekam
    return jsonify({"status": "success", "message": "Recording started"})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording, recorded_letters
    is_recording = False
    
    # Gabungkan huruf yang terekam menjadi kata
    word = ''.join(recorded_letters)
    
    # Buat file audio jika ada huruf yang terekam
    audio_file = None
    if word:
        audio_filename = f"src/static/audio/sibi_{uuid.uuid4().hex[:8]}.mp3"
        if text_to_speech(word, audio_filename):
            audio_file = audio_filename.replace('src/', '')
    
    return jsonify({
        "status": "success", 
        "message": "Recording stopped",
        "word": word,
        "audio_file": audio_file
    })

@app.route('/get_recording_status')
def get_recording_status():
    global is_recording, recorded_letters
    return jsonify({
        "is_recording": is_recording,
        "recorded_letters": recorded_letters,
        "word": ''.join(recorded_letters)
    })

@app.route('/toggle_debug', methods=['POST'])
def toggle_debug():
    """Toggle mode debug on/off"""
    global debug_mode, debug_stats
    
    debug_mode = not debug_mode
    
    # Reset statistik debug jika mode debug diaktifkan
    if debug_mode:
        debug_stats = {
            'fps': 0,
            'latency': 0,
            'inference_time': 0,
            'cpu_percent': 0,
            'memory_percent': 0,
            'avg_confidence': 0,
            'objects_detected': 0,
            'frame_count': 0,
            'processing_times': deque(maxlen=30),
            'confidence_scores': deque(maxlen=30),
        }
    
    return jsonify({
        "status": "success",
        "debug_mode": debug_mode
    })

@app.route('/get_debug_stats')
def get_debug_stats():
    """Dapatkan statistik debug terbaru"""
    global debug_stats, debug_mode
    
    if not debug_mode:
        return jsonify({
            "status": "error",
            "message": "Debug mode is not active"
        })
    
    # Update statistik CPU dan memori
    update_debug_stats()
    
    # Konversi deque ke list untuk serialisasi JSON
    stats = {k: v for k, v in debug_stats.items() if not isinstance(v, deque)}
    
    return jsonify({
        "status": "success",
        "stats": stats
    })

if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
