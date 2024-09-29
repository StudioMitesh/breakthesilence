from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import threading
import cv2
import time
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions, GestureRecognizerResult
import firebase_admin
from firebase_admin import credentials, firestore, auth
from geminilangchain import user_call, send_message, text_to_speech, flow
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate(
    {"type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_DOMAIN")})
firebase_admin.initialize_app(cred)
db = firestore.client()

# Global variables for gesture recognition
is_recognizing = False
signal_count = 0
past_gesture = ["None"]
log_output = []
gesture_names = []
running = True
curr_sequence = []
dct = {"None": 0, "Open_Palm": 1, "Closed_Fist": 2, "Thumb_Up": 3, "Thumb_Down": 4, "Pointing_Up": 5}


def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global signal_count
    global gesture_names
    global is_recognizing
    if signal_count >= 2:
        is_recognizing = False
        return
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
        
        '''# Write to Firestore
        user_id = "test1"
        db.collection('gestures').add({
            'user_id': user_id,
            'gesture_name': gesture_name,
            'score': gesture_category.score,
            'timestamp': firestore.SERVER_TIMESTAMP
        })'''

def gesture_recognition_function():
    global is_recognizing
    global signal_count
    global log_output

    model_path = './cv/model/gesture_recognizer.task'
    base_options = BaseOptions(model_asset_path=model_path)
    
    options = GestureRecognizerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,  # Live stream mode
        result_callback=print_result
    )

    with GestureRecognizer.create_from_options(options) as recognizer:
        global is_recognizing
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not capture frame in video.")
                break
            
            # Convert the frame to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create a MediaPipe Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            
            # Get the current timestamp
            timestamp_ms = int(time.time() * 1000)
            
            # Perform gesture recognition on the current frame
            recognizer.recognize_async(mp_image, timestamp_ms)
            
            # Show the frame with OpenCV
            # cv2.imshow("Gesture Recognition", frame)
            if signal_count>=2 or not is_recognizing:
                print("Detected two gestures.")
                break
            
            # Break the loop if 'q' is pressed
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
    global signal_count
    global running
    global curr_sequence
    print("start button clicked")
    open('./log.txt', 'w').close()
    gesture_names = []
    signal_count = 0
    global is_recognizing
    is_recognizing = True
    while running:
        threading.Thread(target=run_gesture_recognition).start()
        if curr_sequence == [5,5]:
            running = False
            return jsonify({'status': 'Gesture recognition just ended'}), 200
        return jsonify({'status': 'Gesture recognition started'}), 200

@app.route('/stop_gesture_recognition', methods=['POST'])
def stop_gesture_recognition():
    print("stop button clicked")
    global is_recognizing
    is_recognizing = False
    #open("./log.txt", "w").close()
    return jsonify({'status': 'Gesture recognition stopped'}), 200

def run_gesture_recognition():
    print("gesture recognition running")
    global is_recognizing
    gesture_recognition_function()
    if not is_recognizing:
        print("processing gestures")
        with app.app_context():
            process_gestures()
        stop_gesture_recognition()

@app.route('/get_gestures', methods=['GET'])
def get_gestures():
    print("logged")
    gestures_list = []
    with open("./log.txt", "r") as f:
        gestures_list = f.readlines()
    print(gestures_list)
    print(gesture_names)
    '''
    gestures = db.collection('gestures').stream()
    for gesture in gestures:
        gestures_list.append(f"Gesture: {gesture.get('gesture_name')}, Score: {gesture.get('score')}")
        '''

    return jsonify(gestures_list)

@app.route('/process_gestures', methods=['POST'])
def process_gestures():
    global gesture_names
    global curr_sequence
    if len(gesture_names) < 2:
        print("not enough gestures")
        return jsonify({'error': 'Not enough gestures recognized'}), 400
    
    sequence = [dct[name] for name in gesture_names if name in dct]
    print(sequence)

    if len(sequence) != 2:
        print("more than two gestures")
        return jsonify({'error': 'Expected exactly two gestures'}), 400
    print("gemini response")
    response = geminilangchain_llm_call(sequence)
    text_to_speech(response)
    curr_sequence = sequence
    return jsonify({'response': response}), 200

def geminilangchain_llm_call(designation):
    prompt = user_call(designation)
    response = send_message(flow, prompt)
    return response



if __name__ == '__main__':
    app.run(debug=True)
