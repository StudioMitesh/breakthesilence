import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import cv2

# Custom VideoTransformer to process each frame
class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        # Access frame image as a numpy array (BGR format)
        img = frame.to_ndarray(format="bgr24")
        # Return the processed frame
        return img

# Title of the Streamlit app
st.title("Enhanced Camera Stream in Streamlit App")

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
        # You can specify STUN/TURN servers here if needed
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    # Set broadcast mode to improve synchronization
    mode=WebRtcMode.SENDRECV,
)
