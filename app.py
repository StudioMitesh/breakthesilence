from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import threading
import cv2
import time
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions, GestureRecognizerResult
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyaudio
import webrtcvad
import wave
from pydub import AudioSegment
import os

app = Flask(__name__)

# Firebase setup
# cred = credentials.Certificate("/path/to/your/credentials.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# Global variables for gesture recognition
is_recognizing = False
is_recording = False
signal_count = 0
past_gesture = ["None"]
log_output = []
gesture_names = []

def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global signal_count
    global gesture_names
    if signal_count >= 2:
        return  # Ignore further processing
    if result.gestures and result.gestures[0]:
        gesture_category = result.gestures[0][0]
        gesture_name = gesture_category.category_name
        if past_gesture[0] != gesture_name:
            if gesture_name != "None":
                log_output.append(f'Gesture: {gesture_name}, Score: {gesture_category.score}')
                with open("./log.txt", "a") as f:
                    f.write(f'Gesture: {gesture_name}\n')
                    f.write(f'Score: {gesture_category.score}\n\n')
                gesture_names.append(gesture_name)
                signal_count += 1  # Update signal count when a new gesture is recognized
            past_gesture[0] = gesture_name

def gesture_recognition_function():
    global is_recognizing
    global signal_count
    global log_output

    model_path = './cv/model/gesture_recognizer.task'
    base_options = BaseOptions(model_asset_path=model_path)

    options = GestureRecognizerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        result_callback=print_result
    )

    with GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not capture frame in video.")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int(time.time() * 1000)
            recognizer.recognize_async(mp_image, timestamp_ms)

            if signal_count >= 2 or not is_recognizing:
                print("Detected two gestures.")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

@app.route('/')
def landing_preauth():
    return render_template('landing_preauth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            flash('Login successful!')
            return redirect(url_for('landing_postauth'))
        except Exception as e:
            flash(str(e))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user(email=email, password=password)
            flash('User created successfully!')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e))
    return render_template('register.html')

@app.route('/landing_postauth')
def landing_postauth():
    return render_template('landing_postauth.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/llm')
def llm():
    return render_template('llm.html')

@app.route('/start_audio_recording', methods=['POST'])
def start_recording():
    global is_recording
    is_recording = True
    print("Starting audio recording...")

    # Audio configuration
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    frame_duration_ms = 30
    frame_duration_seconds = frame_duration_ms / 1000
    CHUNK = int(RATE * frame_duration_seconds)

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open stream
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    # Initialize VAD
    vad = webrtcvad.Vad()
    vad.set_mode(3)  # 0: Very aggressive, 3: Less aggressive

    # Start recording in a separate thread
    threading.Thread(target=record_audio, args=(vad, stream, audio, CHUNK, RATE, frame_duration_seconds)).start()
    return jsonify({'status': 'Audio recording started'}), 200

def is_speech(frame, sample_rate, vad):
    return vad.is_speech(frame, sample_rate)

def record_audio(vad, stream, audio, CHUNK, RATE, frame_duration_seconds):
    global is_recording
    print("Listening for speech...")
    audio_segments = []
    current_segment = []
    silence_frame_count = 0
    silence_duration = 2.5

    try:
        while is_recording:
            frame = stream.read(CHUNK, exception_on_overflow=False)
            if is_speech(frame, RATE, vad):
                print("Speech detected...")
                current_segment.append(frame)
                silence_frame_count = 0
            else:
                silence_frame_count += 1
                if current_segment and silence_frame_count > (silence_duration / frame_duration_seconds):
                    print("Silence detected, saving current segment...")
                    save_audio_wav(audio, current_segment, f"output.wav")
                    convert_wav_to_mp3(f"output.wav", f"output.mp3")
                    os.remove(f"output.wav")
                    current_segment = []
                    silence_frame_count = 0
                    # Use application context for the following call
                    with app.app_context():
                        stop_audio_recognition()
                    break

    except Exception as e:
        print(f"Error while processing frame: {e}")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
def save_audio_wav(audio, frames, filename="output.wav"):
    """Save the recorded audio as a WAV file."""
    if frames:  # Ensure there are frames to save
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Audio saved as {filename}")
    else:
        print("No frames to save.")


def convert_wav_to_mp3(wav_filename, mp3_filename):
    sound = AudioSegment.from_wav(wav_filename)
    sound.export(mp3_filename, format="mp3")
    print(f"Converted {wav_filename} to {mp3_filename}")


@app.route('/stop_audio_recording', methods=['POST'])
def stop_audio_recognition():
    global is_recording
    is_recording = False
    return jsonify({'status': 'Audio recording stopped'}), 200

@app.route('/start_gesture_recognition', methods=['POST'])
def start_gesture_recognition():
    global gesture_names
    print("Start button clicked")
    open('./log.txt', 'w').close()
    gesture_names = []
    global is_recognizing
    is_recognizing = True
    if is_recognizing:
        threading.Thread(target=run_gesture_recognition).start()
        return jsonify({'status': 'Gesture recognition started'}), 200
    else:
        return jsonify({'status': 'Gesture recognition is already running'}), 400

@app.route('/stop_gesture_recognition', methods=['POST'])
def stop_gesture_recognition():
    global is_recognizing
    print("Stop button clicked")
    if not is_recognizing:
        return jsonify({'status': 'Gesture recognition stopped'}), 200
    else:
        return jsonify({'status': 'Gesture recognition is not running'}), 400

def run_gesture_recognition():
    print("Gesture recognition running")
    global is_recognizing
    gesture_recognition_function()
    if not is_recognizing:
        get_gestures()
        stop_gesture_recognition()

@app.route('/get_gestures', methods=['GET'])
def get_gestures():
    print("Logging gestures")
    gestures_list = []
    with open("./log.txt", "r") as f:
        gestures_list = f.readlines()
    return jsonify(gestures_list)

if __name__ == '__main__':
    app.run(debug=True)
