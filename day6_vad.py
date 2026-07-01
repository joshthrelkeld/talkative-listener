import torch
import numpy as np
import pyaudio
from dotenv import load_dotenv

load_dotenv()

print("Loading Silero VAD model...")
model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    force_reload=False,
)
(get_speech_timestamps, _, read_audio, *_) = utils
print("Model loaded.")

THRESHOLD = 0.5
SAMPLE_RATE = 16000
CHUNK = 512

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=CHUNK,
)

print("Listening for speech... Press Ctrl+C to stop.")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_chunk = torch.from_numpy(
            np.frombuffer(data, dtype=np.int16).copy()
        ).float()

        confidence = model(audio_chunk, SAMPLE_RATE).item()

        if confidence >= THRESHOLD:
            print(f"SPEECH detected (confidence: {confidence:.2f})")
        else:
            print(f"silence (confidence: {confidence: .2f}")

except KeyboardInterrupt:
    print("\nStopping.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()