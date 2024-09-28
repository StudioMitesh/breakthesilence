import mediapipe as mp
import cv2
import time
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions, GestureRecognizerResult
import json

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("hackgt-11-firebase-adminsdk-o5ziq-f4f2cd7c75.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


model_path = './model/gesture_recognizer.task'
base_options = BaseOptions(model_asset_path=model_path)

signal_count = 0
past_gesture = ["None"]

with open("./log.txt", "w") as f:
    def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        global signal_count 
        if signal_count >= 2:
            return  # Ignore further processing
        
        if result.gestures and result.gestures[0]:
            gesture_category = result.gestures[0][0]
            gesture_name = gesture_category.category_name
            # Check if the current gesture is different from the last one
            if past_gesture[0] != gesture_name:
                if gesture_name != "None":
                    f.write(f'Gesture: {gesture_name}\n')
                    f.write(f'Score: {gesture_category.score}\n\n')
                    signal_count += 1  # Update signal count when a new gesture is recognized
                past_gesture[0] = gesture_name
            print(gesture_name)

        user_id = "test1"
        db.collection('gestures').add({
            'user_id': user_id,
            'gesture_name': gesture_name,
            'score': gesture_category.score,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print(f"Written to Firestore: Gesture: {gesture_name}, Score: {gesture_category.score}")



    options = GestureRecognizerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,  # Live stream mode
        result_callback=print_result
    )

    with GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            exit()
        
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
            cv2.imshow("Gesture Recognition", frame)
            
            if signal_count >= 2:
                print("Detected two gestures.")
                break
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the capture and close the window
        cap.release()
        cv2.destroyAllWindows()
