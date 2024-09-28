import pyaudio
import webrtcvad
import wave
from pydub import AudioSegment
import os

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
frame_duration_ms = 30  
frame_duration_seconds = frame_duration_ms / 1000
CHUNK = int(RATE * frame_duration_seconds)
global conversation
conversation = True

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
vad.set_mode(3)  # 0: Very aggressive, 3: Less aggressive

def is_speech(frame, sample_rate):
    return vad.is_speech(frame, sample_rate)

def record_audio(silence_duration):
    print("Listening for speech...")
    audio_segments = []  # To store audio segments where speech is detected
    current_segment = []  # To store the current segment of speech
    silence_frame_count = 0
    try:
        while conversation:
            frame = stream.read(CHUNK, exception_on_overflow=False)
            # Check if the frame contains speech
            if is_speech(frame, RATE):
                print("Speech detected...")
                current_segment.append(frame)  # Append speech frame to current segment
                silence_frame_count = 0  # Reset silence counter
            else:
                silence_frame_count += 1
                if current_segment and silence_frame_count > (silence_duration / frame_duration_seconds):
                    print("Silence detected, saving current segment...")
                    save_audio_wav(current_segment, f"output.wav")
                    convert_wav_to_mp3(f"output.wav", f"output.mp3")
                    os.remove(f"output.wav")  # Optional: Remove WAV after conversion
                    current_segment = []  # Reset for the next segment
                    silence_frame_count = 0
                    break
                else:
                    print("Not detecting speech.")

    except KeyboardInterrupt:
        print("Recording stopped manually.")

    except Exception as e:
        print(f"Error while processing frame: {e}")

    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

def save_audio_wav(frames, filename="output.wav"):
    """Save the recorded audio as a WAV file."""
    if frames:  # Ensure there are frames to save
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Audio saved as {filename}")
    else:
        print("No frames to save.")

def convert_wav_to_mp3(wav_filename, mp3_filename):
    sound = AudioSegment.from_wav(wav_filename)
    sound.export(mp3_filename, format="mp3")
    print(f"Converted {wav_filename} to {mp3_filename}")

# Example usage
silence_duration = 0.5
record_audio(silence_duration)
