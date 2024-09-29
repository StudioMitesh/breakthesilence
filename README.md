# Break the Silence

A transformative platform designed to empower non-verbal children, students, and elderly individuals to communicate effectively with minimal movement. Using cutting-edge gesture recognition and contextual understanding, **Break the Silence** enables meaningful and rich interactions for users of all ages.

## 🚀 Project Demo
**Break the Silence** allows users to communicate seamlessly using gestures and context-aware responses.

1. **User Profile Setup**: The platform starts with a user bio page for setting up profiles and preferences, ensuring a personalized experience.
2. **Real-Time Gesture Recognition**: The system recognizes gestures like waving or pointing in real-time, allowing for an immediate understanding of the user’s intent.
3. **Contextual Conversations**: With the help of a memory language chain, the platform builds context around gestures to provide relevant and meaningful dialogue.
4. **Audio Response Generation**: The platform not only recognizes gestures but also provides an audio response to enhance the communication experience.
   
## 🌟 Key Features
- **Gesture Recognition**: Uses [MediaPipe](https://google.github.io/mediapipe/) for detecting and interpreting a wide range of gestures accurately.
- **Context-Aware Interactions**: Powered by OpenAI's API and [LangChain](https://langchain.com/) to build context and generate meaningful conversations based on gestures.
- **Audio Feedback**: Provides real-time audio responses to gestures, enhancing communication effectiveness.

## ⚙️ Tech Stack
- **Frontend**: HTML and JavaScript for an intuitive and user-friendly interface.
- **Backend**: Python for efficient data processing and running machine learning algorithms.
- **Database & Hosting**: [Firebase](https://firebase.google.com/) for real-time data management, hosting, and secure user authentication.
- **Gesture Recognition**: [MediaPipe](https://google.github.io/mediapipe/) for advanced computer vision capabilities.
- **Language Models**: OpenAI API and [LangChain](https://langchain.com/) for contextually rich and accurate dialogue generation.
- **Deployment**: Hosted on [Heroku](https://www.heroku.com/) integrated with Firebase databases for seamless real-time performance.

## 💡 How It Works
1. **Gesture Recognition**: The platform uses the user's webcam to capture gestures, which are processed and recognized by the MediaPipe computer vision library.
2. **Context Building**: Leveraging LangChain and OpenAI's API, the system builds context based on the gesture, user profile, and ongoing interactions.
3. **Audio Generation**: Once the gesture is understood, a relevant and context-aware audio response is generated and played back to the user.

## 📁 Repository Structure
Here's a breakdown of the main folders and files in the repository:

- `.firebase`: Configurations and settings for Firebase hosting and database.
- `.github/workflows`: CI/CD workflows for deployment using Heroku and Firebase.
- `cv/`: Frontend work, including landing and login pages.
- `dataconnect/`: Code and scripts related to Firebase data connections.
- `static/` & `templates/`: Web assets like CSS, JavaScript, HTML templates.
- `geminilangchain.py`: Core file for integrating LangChain with gesture and audio recognition.
- `constant-recording.py`: Script for continuously recording audio in response to gestures.
- `sound-recording.py`: Handles capturing sound input for audio responses.

## 🛠️ Installation & Setup
1. **Clone the repository**:
    ```bash
    git clone https://github.com/YourUsername/break-the-silence.git
    ```
2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Set up Firebase and API keys**: Configure `.env` file with your Firebase credentials and OpenAI API key.
4. **Run the app**:
    ```bash
    python app.py
    ```

## 🤝 Contribution
We welcome contributions to enhance **Break the Silence**. If you're interested in collaborating, please fork the repository and submit a pull request with a detailed description of your changes.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments
- [Firebase](https://firebase.google.com/) for providing real-time database and hosting solutions.
- [MediaPipe](https://google.github.io/mediapipe/) for robust gesture recognition capabilities.
- [OpenAI](https://openai.com/) and [LangChain](https://langchain.com/) for context-aware dialogue generation.
