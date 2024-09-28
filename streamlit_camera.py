import streamlit as st
import mediapipe as mp
import cv2
import time
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions, GestureRecognizerResult

# Streamlit title
st.title("Gesture Recognition App")

# Paths and model settings
model_path = './model/gesture_recognizer.task'
canned_gestures = ["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"]

# Initialize global variables and placeholders
frame_placeholder = st.empty()
gesture_placeholder = st.empty()

# Function to process the gesture recognition results
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    if result.gestures and result.gestures[0]:
        gesture_category = result.gestures[0][0]
        gesture_name = gesture_category.category_name
        gesture_score = gesture_category.score
        gesture_index = canned_gestures.index(gesture_name)

        # Print gesture details in Streamlit
        gesture_placeholder.write(f"Gesture: {gesture_name}, Index: {gesture_index}, Score: {gesture_score:.2f}")

# Initialize MediaPipe options
base_options = BaseOptions(model_asset_path=model_path)
options = GestureRecognizerOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,  # Live stream mode
    result_callback=print_result
)

# Button to start camera and process frames
if st.button("Open Camera"):
    # Create the Gesture Recognizer
    with GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)  # Open the default camera

        if not cap.isOpened():
            st.error("Error: Could not open camera")
            st.stop()

        # Stream video frames and run gesture recognition
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("Error: Could not read frame from camera")
                break

            # Convert frame to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create a MediaPipe Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            # Get the current timestamp
            timestamp_ms = int(time.time() * 1000)

            # Perform gesture recognition on the current frame
            recognizer.recognize_async(mp_image, timestamp_ms)

            # Display the frame in Streamlit
            frame_placeholder.image(frame_rgb, channels="RGB")

        # Release the camera after the loop ends
        cap.release()
