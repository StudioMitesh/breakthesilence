import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

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
const analytics = getAnalytics(app);

function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    firebase.auth().signInWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // Signed in 
            window.location.href = "/landing_postauth"; // Redirect on success
        })
        .catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            alert("Error: " + errorMessage);
        });
}