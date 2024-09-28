import {
  GestureRecognizer,
  FilesetResolver,
  DrawingUtils
} from "@mediapipe/tasks-vision";

let gestureRecognizer: GestureRecognizer | null = null;
let gestures = ['None'];
let signalCount = 0;

// Get references to DOM elements
const videoElement = document.getElementById("video") as HTMLVideoElement;
const canvasElement = document.getElementById("output_canvas") as HTMLCanvasElement;
const canvasCtx = canvasElement.getContext("2d") as CanvasRenderingContext2D;
const gestureOutput = document.getElementById("gesture_output") as HTMLDivElement;

const videoWidth = 1280;
const videoHeight = 720;

let gestureRecognizer: GestureRecognizer | null = null; // Initialize as null

// Setup the gesture recognizer
async function createGestureRecognizer() {
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
  );

  gestureRecognizer = await GestureRecognizer.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: "https://storage.googleapis.com/mediapipe-tasks/gesture_recognizer/gesture_recognizer.task",
      delegate: "GPU"
    },
    runningMode: "VIDEO" // Set the running mode to video
  }) as GestureRecognizer;
}
createGestureRecognizer();

async function recognizeGesture() {
  if (!gestureRecognizer) {
    console.log("GestureRecognizer not initialized");
    return;
  }

  const videoStream = await navigator.mediaDevices.getUserMedia({
    video: { width: videoWidth, height: videoHeight }
  });

  videoElement.srcObject = videoStream;
  videoElement.play();

  videoElement.addEventListener("loadeddata", async () => {
    const drawingUtils = new DrawingUtils(canvasCtx);

    while (signalCount < 2) {
      // Perform gesture recognition at each frame
      let time = Date.now();
      let results = await gestureRecognizer.recognizeForVideo(videoElement, time);
      

      canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

      if (results.landmarks) {
        for (const landmarks of results.landmarks) {
          drawingUtils.drawConnectors(
            landmarks,
            GestureRecognizer.HAND_CONNECTIONS,
            { color: "#00FF00", lineWidth: 5 }
          );
          drawingUtils.drawLandmarks(landmarks, {
            color: "#FF0000", lineWidth: 2
          });
        }
      }

      // Check and log gestures
      if (results.gestures && results.gestures[0]) {
        const gestureCategory = results.gestures[0][0].categoryName;

        // Log only new gestures
        if (gestureCategory !== 'None' && gestures[gestures.length - 1] !== gestureCategory) {
          console.log(`Gesture: ${gestureCategory}`);
          console.log(`Score: ${results.gestures[0][0].score}`);
          gestures.push(gestureCategory);
          signalCount++;
        }

        // Display gesture information
        gestureOutput.innerText = `Gesture: ${gestureCategory}\n Confidence: ${(results.gestures[0][0].score * 100).toFixed(2)} %`;
        gestureOutput.style.display = 'block';
      } else {
        gestureOutput.style.display = 'none';
      }

      // Break loop after detecting two gestures
      if (signalCount >= 2) {
        console.log("Detected two gestures.");
        break;
      }

      // Request the next frame
      await new Promise(requestAnimationFrame);
    }
  });
}

// Initialize and start gesture recognition when the webcam is activated
const start = document.getElementById("startButton") as HTMLButtonElement;
start.addEventListener("click", () => { recognizeGesture(); });
