import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

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
MODEL_PATH = "G:/Github/SIBI/SIBI-YOLOv8/best.pt"
CONFIDENCE_THRESHOLD = 0.3
DETECTION_DELAY = 0.8
STABILITY_FRAMES = 3

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

def detect_sibi_in_frame(frame):
    global model, detection_history
    
    if model is None:
        return frame, None
    
    results = model(frame, stream=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    detected_letters = []
    current_detections = {}
    
    for r in results:
        boxes = r.boxes
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_idx = int(box.cls[0])
            
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
    
    for letter, data in current_detections.items():
        if letter not in detection_history:
            detection_history[letter] = 1
        else:
            detection_history[letter] += 1
        
        if detection_history[letter] >= STABILITY_FRAMES:
            detected_letters.append(letter)
            
            x1, y1, x2, y2 = data['box']
            conf = data['conf']
            label = f"{letter} {conf:.2f}"
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) 
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    for letter in list(detection_history.keys()):
        if letter not in current_detections:
            detection_history[letter] = 0
            if detection_history[letter] <= 0:
                del detection_history[letter]
    
    return frame, detected_letters

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
        
        processed_frame, detected_letters = detect_sibi_in_frame(frame)
        
        current_time = time.time()
        if is_recording and detected_letters:
            if current_time - last_detection_time >= DETECTION_DELAY:
                for letter in detected_letters:
                    if not recorded_letters or recorded_letters[-1] != letter:
                        recorded_letters.append(letter)
                        last_detection_time = current_time
                        break
        
        if is_recording:
            cv2.circle(processed_frame, (30, 30), 15, (0, 0, 255), -1)  # Lingkaran merah
            cv2.putText(processed_frame, "Recording", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        
        with lock:
            output_frame = processed_frame.copy()
        
        ret, buffer = cv2.imencode('.jpg', output_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
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
