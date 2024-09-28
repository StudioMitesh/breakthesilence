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
        } catch (err) {
            console.error("Error accessing camera: ", err);
        }
    }

    // Start gesture recognition on button click
    startButton.addEventListener('click', function () {
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
    });

    function fetchGestures() {
        $.get('/get_gestures', function(data) {
            $('#gesture-results').empty();
            data.forEach(function(gesture) {
                $('#gesture-results').append('<p>' + gesture + '</p>');
            });
        });
    }

    // Start the video on page load
    startVideo();
    setInterval(fetchGestures, 5000);
    fetchGestures();
});
