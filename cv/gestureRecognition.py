import streamlit as st
import mediapipe as mp
import cv2
import time
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions, GestureRecognizerResult
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def gesture_recognition(navigate_to):
    model_path = './cv/model/gesture_recognizer.task'
    canned_gestures = ["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"]
    base_options = BaseOptions(model_asset_path=model_path)
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Create a gesture recognizer instance with the live stream mode:
    def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        if(result.gestures and result.gestures[0]):
            gesture_category = result.gestures[0][0]
            print('Gesture:', gesture_category.category_name)
            print('Index:', canned_gestures.index(gesture_category.category_name))
            print('Score:', gesture_category.score)


    options = GestureRecognizerOptions(
        base_options=base_options,
        running_mode=VisionRunningMode.LIVE_STREAM,  # Live stream mode
        result_callback=print_result
        )

    with GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            exit()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not capture frame in video")
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
            cv2.imshow("Gesture Recognition", frame)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the capture and close the window
        cap.release()
        cv2.destroyAllWindows()
