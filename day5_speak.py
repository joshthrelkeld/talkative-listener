import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import pyaudio
from pydub import AudioSegment
import io

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

response = client.text_to_speech.convert(
    text="Hello, thank you for calling Santa Monica Hospital. How can I help you today?",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_turbo_v2",
    output_format="mp3_44100_128"
)

audio_bytes = b"".join(response)
audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
raw_audio = audio_segment.raw_data

p = pyaudio.PyAudio()
stream = p.open(
    format=p.get_format_from_width(audio_segment.sample_width),
    channels=audio_segment.channels,
    rate=audio_segment.frame_rate,
    output=True,
)

stream.write(raw_audio)
stream.stop_stream()
stream.close()
p.terminate()

print("Done.")