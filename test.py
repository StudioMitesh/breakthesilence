import streamlit as st

# Define your HTML/JS for the gesture recognition
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gesture Recognition</title>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3"></script>
  <style>
    video {
      width: 1280px;
      height: 720px;
      border: 2px solid black;
    }
    canvas {
      position: absolute;
      left: 0;
      top: 0;
    }
  </style>
</head>
<body>
  <video id="video" autoplay></video>
  <canvas id="output_canvas"></canvas>
  <div id="gesture_output" style="display:none;"></div>

  <script src="script.js"></script>
</body>
</html>
"""
def test(navigate_to):
    # Use the Streamlit components to render the HTML
    st.components.v1.html(html_code, height=400)

    # Optional: Provide a way to display logs or results from the JavaScript
    log_file_path = './log.txt'  # Path to your log file
    if st.button("Show Log"):
        with open(log_file_path, "r") as f:
            log_content = f.read()
            st.text_area("Gesture Log", log_content, height=300)
