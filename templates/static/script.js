// static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById('video');
    const startButton = document.getElementById('start');
    const conversation = True
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

    async function startAudio(){
        fetch('/start_audio_recognition', {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                return response.mp3();
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

    // Start the video on page load
    startVideo();
    startRecognition();
    startAudio();
    setInterval(fetchLog, 5000);
    fetchLog();

});
