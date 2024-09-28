import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions, GestureRecognizerResult
import time

# MediaPipe Model Path and Gesture Options
model_path = './model/gesture_recognizer.task'
canned_gestures = ["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"]

base_options = BaseOptions(model_asset_path=model_path)
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Store the recognizer globally so it can be used in transform method
recognizer = GestureRecognizer.create_from_options(
    GestureRecognizerOptions(
        base_options=base_options,
        running_mode=VisionRunningMode.LIVE_STREAM
    )
)

# Custom VideoTransformer to process each frame
class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        # Access frame image as a numpy array (BGR format)
        img = frame.to_ndarray(format="bgr24")

        # Convert frame to RGB for MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Create a MediaPipe Image object
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Get the current timestamp
        timestamp_ms = int(time.time() * 1000)
        
        # Perform gesture recognition on the current frame
        result = recognizer.recognize(mp_image)
        
        # Check for gesture results
        if result.gestures and result.gestures[0]:
            gesture_category = result.gestures[0][0]
            # Display gesture name and score on the frame
            cv2.putText(img, f'Gesture: {gesture_category.category_name} ({gesture_category.score:.2f})', 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            
        # Return the processed frame
        return img

# Title of the Streamlit app
st.title("Gesture Recognition in Streamlit App")

# Start the camera feed within Streamlit with improved settings
webrtc_streamer(
    key="camera",
    video_transformer_factory=VideoTransformer,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 1280},   # Set desired width
            "height": {"ideal": 720},   # Set desired height
            "frameRate": {"ideal": 30}, # Set frame rate
        }
    },
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    mode=WebRtcMode.SENDRECV,
)
