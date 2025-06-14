import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
from ultralytics import YOLO
import threading
import json
from google.cloud import texttospeech
import uuid
from collections import deque

app = Flask(__name__)

# Konfigurasi
MODEL_PATH = "G:/Github/SIBI/SIBI-YOLOv8/best.pt"  # Path ke model kustom SIBI
CONFIDENCE_THRESHOLD = 0.7  # Ambang batas kepercayaan minimum untuk deteksi (ditingkatkan dari 0.5)
DETECTION_DELAY = 0.8  # Jeda antar deteksi dalam detik (ditingkatkan dari 0.5)
STABILITY_FRAMES = 3  # Jumlah frame berturut-turut yang diperlukan untuk konfirmasi deteksi

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
detection_history = {}  # Untuk melacak stabilitas deteksi

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
            
        # Sesuaikan path ke file kredensial Google Cloud
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # Create a Text-to-Speech client
        client = texttospeech.TextToSpeechClient()
        
        # Prepare the text input for synthesis
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Set the voice parameters
        voice = texttospeech.VoiceSelectionParams(
            language_code="id-ID",  # Use "id-ID" for Indonesian
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        # Set the audio configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        # Perform the text-to-speech synthesis
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Write the response to an output file
        with open(output_filename, "wb") as out:
            out.write(response.audio_content)
            print(f"Audio content written to file: {output_filename}")
        
        return True
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return False

def detect_sibi_in_frame(frame):
    global model, detection_history
    
    if model is None:
        return frame, None
    
    # Lakukan deteksi dengan YOLOv8
    results = model(frame, stream=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    detected_letters = []
    current_detections = {}
    
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
                letter = SIBI_LABELS[cls_idx]
                label = f"{letter} {conf:.2f}"  # Buat label (nama kelas + kepercayaan)
                
                # Tambahkan ke deteksi saat ini
                if letter in current_detections:
                    if conf > current_detections[letter]['conf']:
                        current_detections[letter] = {'conf': conf, 'box': (x1, y1, x2, y2)}
                else:
                    current_detections[letter] = {'conf': conf, 'box': (x1, y1, x2, y2)}
            else:
                label = f"Unknown {conf:.2f}"  # Jika indeks di luar jangkauan
    
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
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Warna hijau, ketebalan 2
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Reset history untuk huruf yang tidak terdeteksi di frame saat ini
    for letter in list(detection_history.keys()):
        if letter not in current_detections:
            detection_history[letter] = 0
            # Hapus dari history jika sudah tidak terdeteksi lagi
            if detection_history[letter] <= 0:
                del detection_history[letter]
    
    return frame, detected_letters

def generate_frames():
    global output_frame, lock, is_recording, recorded_letters, camera, last_detection_time
    
    if camera is None:
        camera = cv2.VideoCapture(0)  # 0 untuk webcam default
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

if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
