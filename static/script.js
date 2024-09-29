// static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById('video');
    const startButton = document.getElementById('start'); // Assuming there is a start button
    const stopButton = document.getElementById('stop-button');

    let stream; // Store the video stream so we can stop it later

    // Start the video stream
    async function startVideo() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: true
            });
            video.srcObject = stream;
            video.play();
        } catch (err) {
            console.error("Error accessing camera: ", err);
        }
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

    // Stop the video stream
    function stopVideoStream() {
        if (stream) {
            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
    }

    // Add event listener to stop button
    stopButton.addEventListener('click', stopVideoStream);

    // Start the video on page load
    startVideo();
    startRecognition();
    setInterval(fetchLog, 5000);
    fetchLog();
});
