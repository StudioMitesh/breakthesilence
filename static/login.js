import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyBfrbcvOqpQwt3e-ptBOjbUXsX77-N_Asc",
    authDomain: "hackgt-11.firebaseapp.com",
    projectId: "hackgt-11",
    storageBucket: "hackgt-11.appspot.com",
    messagingSenderId: "847885215810",
    appId: "1:847885215810:web:7ec0687b07fe2995d725db",
    measurementId: "G-PGZQ5XLE8M"
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    firebase.auth().signInWithEmailAndPassword(email, password)
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `email=${email}&password=${password}`
        })
        .then(response => response.json())
        .then(data => {
        // Redirect to authenticated page
        window.location.href = '/landing_postauth';
        })
    .catch((error) => {
        const errorMessage = error.message;
        alert("Error: " + errorMessage);
    });
}

console.log("JavaScript Loaded"); // Log to check if script is loaded

function register() {
    console.log("Register function called"); // Log when the function is called

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Create a new user with email and password
    auth.createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // Successfully registered
            const user = userCredential.user;
            console.log("User registered:", user);

            // Optionally, store the user's name in the database
            db.collection("users").doc(user.uid).set({
                name: name,
                email: email
            }).then(() => {
                console.log("User information saved to Firestore");
                alert("Registration successful!");
                window.location.href = "/login"; // Redirect to login page after registration
            }).catch((error) => {
                console.error("Error saving user information:", error);
            });
        })
        .catch((error) => {
            console.error("Error during registration:", error.message);
            alert("Error during registration: " + error.message);
        });
}

// Attach event listener to the register form
document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('register-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting
        register(); // Call the register function
    });
});

document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting
        login(); // Call the login function
    });
});

/* auth().currentUser.getIdToken()
  .then((idToken) => {
    // Send the ID token to your Flask server
    fetch('/your-secure-endpoint', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify({  }),
    });
}); */