from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import threading
import cv2
import time
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions, GestureRecognizerResult
import firebase_admin
from firebase_admin import credentials, firestore, auth
from geminilangchain import user_call, send_message
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
dct = {"None": 0, "Open_Palm": 1, "Closed_Fist": 2, "Thumbs_Up": 3, "Thumbs_Down": 4, "Pointing_Up": 5}


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

@app.route('/start_gesture_recognition', methods=['POST'])
def start_gesture_recognition():
    global gesture_names
    print("start button clicked")
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
    print("stop button clicked")
    global is_recognizing
    #open("./log.txt", "w").close()
    if not is_recognizing:
        return jsonify({'status': 'Gesture recognition stopped'}), 200
    else:
        return jsonify({'status': 'Gesture recognition is not running'}), 400

def run_gesture_recognition():
    print("gesture recognition running")
    global is_recognizing
    gesture_recognition_function()
    if not is_recognizing:
        get_gestures()
        with app.test_request_context():
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
    if len(gesture_names) < 2:
        return jsonify({'error': 'Not enough gestures recognized'}), 400
    
    sequence = [dct[name] for name in gesture_names if name in dct]

    if len(sequence) != 2:
        return jsonify({'error': 'Expected exactly two gestures'}), 400

    designation = f"{sequence[0]} {sequence[1]}"
    response = geminilangchain_llm_call(designation)

    return jsonify({'response': response}), 200

def geminilangchain_llm_call(designation):
    prompt = user_call(designation)
    
    response = send_message(app, prompt)
    return response



if __name__ == '__main__':
    app.run(debug=True)
