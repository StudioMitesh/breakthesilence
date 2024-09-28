import pyaudio
import webrtcvad
import wave
from pydub import AudioSegment
import time

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
frame_duration_ms = 30  
frame_duration_seconds = frame_duration_ms / 1000
CHUNK = int(RATE * frame_duration_seconds)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

# Initialize VAD
vad = webrtcvad.Vad()
vad.set_mode(1)  # 0: Very aggressive, 3: Less aggressive

def is_speech(frame, sample_rate):
    return vad.is_speech(frame, sample_rate)

def record_audio(silence_duration):
    frames = []
    recording = False
    silence_frame_count = 0  # Counter for silence frames
    print("Listening for speech...")
    try:
        while True:
            frame = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(frame)

            # Check if the frame contains speech
            if is_speech(frame, RATE):
                if not recording:
                    print("Speech detected, starting recording...")
                    recording = True
                silence_frame_count = 0  
            else:
                if recording:
                    silence_frame_count += 1

            if recording and silence_frame_count > (silence_duration / frame_duration_seconds):
                print("Silence detected, stopping recording...")
                break

    except Exception as e:
        print(f"Error while processing frame: {e}")

    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

    return frames

def save_audio_wav(frames, filename="output.wav"):
    """Save the recorded audio as a WAV file."""
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def convert_wav_to_mp3(wav_filename, mp3_filename):
    sound = AudioSegment.from_wav(wav_filename)
    sound.export(mp3_filename, format="mp3")

# Example usage
silence_duration = 0.5  # Number of seconds of silence before stopping
frames = record_audio(silence_duration=silence_duration)

# Save the audio as WAV
wav_filename = "output.wav"
save_audio_wav(frames, wav_filename)
print(f"Audio saved as {wav_filename}")

# Convert WAV to MP3
mp3_filename = "output.mp3"
convert_wav_to_mp3(wav_filename, mp3_filename)
print(f"Audio converted and saved as {mp3_filename}")