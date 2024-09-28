import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def landing_preauth():
    return render_template('landing_preauth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic
        return render_template('landing_postauth.html')
    return render_template('login.html')

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
    try:
        # Start the gesture recognition script
        subprocess.Popen(['python', 'gestureRecognition.py'])  # Adjust this path if necessary
        return jsonify({'status': 'Gesture recognition started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
