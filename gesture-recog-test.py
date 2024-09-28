import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import mediapipe as mp
import cv2
import time
import os

# Check if MediaPipe model exists
model_path = './model/gesture_recognizer.task'
canned_gestures = [
    "None", "Closed_Fist", "Open_Palm", "Pointing_Up", 
    "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"
]

if not os.path.exists(model_path):
    st.error("Model file not found. Please ensure the model is available at './model/gesture_recognizer.task'.")
    st.stop()

# MediaPipe Gesture Recognizer Setup
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Define a callback function for results
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    if result.gestures and result.gestures[0]:
        gesture_category = result.gestures[0][0]
        gesture_name = gesture_category.category_name
        gesture_index = canned_gestures.index(gesture_name)
        gesture_score = gesture_category.score
        st.write(f'Gesture: {gesture_name}, Index: {gesture_index}, Score: {gesture_score}')

# Options for Gesture Recognizer
options = GestureRecognizerOptions(
    base_options=base_options,
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

# Define a VideoTransformer for Streamlit WebRTC
class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        # Initialize the gesture recognizer
        self.recognizer = GestureRecognizer.create_from_options(options)
    
    def transform(self, frame):
        # Access frame image as numpy array (BGR format)
        img = frame.to_ndarray(format="bgr24")
        
        # Convert the frame to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Create a MediaPipe Image object
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Get the current timestamp
        timestamp_ms = int(time.time() * 1000)
        
        # Perform gesture recognition on the current frame
        self.recognizer.recognize_async(mp_image, timestamp_ms)
        
        # Return the original frame (processed if desired)
        return img

# Streamlit App Title
st.title("Enhanced Camera Stream with Gesture Recognition")

# Start camera feed within Streamlit using WebRTC
webrtc_streamer(
    key="gesture-recognition",
    video_transformer_factory=VideoTransformer,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 1280},
            "height": {"ideal": 720},
            "frameRate": {"ideal": 30},
        }
    },
    rtc_configuration={
        # STUN server for connectivity
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    mode=WebRtcMode.SENDRECV,
)
