// static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById('video');
    const startButton = document.getElementById('start');

    // Start the video stream
    async function startVideo() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true
            });
            video.srcObject = stream;
            video.play();
        } catch (err) {
            console.error("Error accessing camera: ", err);
        }
    }

    // Start audio recognition
    async function startAudio(){
        fetch('/start_audio_recording', {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                return response.json();  // Handling JSON response
            } else {
                throw new Error('Failed to start audio recognition');
            }
        })
        .then(data => {
            console.log(data.status); // Display success message
        })
        .catch(error => {
            console.error(error);
        });
    }

    async function startRecognition() {
        fetch('/start_gesture_recognition', {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to start gesture recognition');
            }
        })
        .then(data => {
            console.log(data.status); // Display success message
        })
        .catch(error => {
            console.error(error);
        });
    }

    function fetchLog() {
        $.get('/get_gestures', function(data) {
            $('#gesture-log').empty();
            data.forEach(function(gesture) {
                $('#gesture-log').append('<li>' + gesture + '</li>');
            });
        }).fail(function(err) {
            console.error(err);
        });
    }

    // Start all processes concurrently
    function startProcesses() {
        // Start video, audio, and gesture recognition concurrently
        startVideo(); // Video runs separately and doesn't depend on audio or gesture
        Promise.all([startAudio(), startRecognition()])
        .then(() => {
            console.log("Both audio and gesture recognition started successfully.");
        })
        .catch(error => {
            console.error("Error in starting processes: ", error);
        });
    }
    startProcesses();

    // Refresh gesture log every 5 seconds
    setInterval(fetchLog, 5000);
});
