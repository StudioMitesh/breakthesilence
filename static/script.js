document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById('video');
    const recordButton = document.getElementById('record');

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

     // Start audio recognition
     function startAudio(){
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

    // Add event listener to stop button
    recordButton.addEventListener('click', startAudio);

    // Start the video on page load
    startVideo();
    startRecognition();
    setInterval(fetchLog, 5000);
    fetchLog();
});