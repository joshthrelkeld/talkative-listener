import os
import threading
import pyaudio
from dotenv import load_dotenv
from deepgram import DeepgramClient
from deepgram.core.events import EventType

load_dotenv()

client = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

with client.listen.v1.connect(
    model="nova-3",
    language="en-US",
    smart_format=True,
    encoding="linear16",
    sample_rate=16000,
) as connection:

    def on_open(event):
        print("Connection opened")

    def on_message(message):
        if message.type == "Results":
            transcript = message.channel.alternatives[0].transcript
            print(f"Transcript: '{transcript}'")

    def on_error(error):
        print(f"Error: {error}")

    def on_close(event):
        print("Connection closed")

    connection.on(EventType.OPEN, on_open)
    connection.on(EventType.MESSAGE, on_message)
    connection.on(EventType.ERROR, on_error)
    connection.on(EventType.CLOSE, on_close)

    listener_thread = threading.Thread(target=connection.start_listening)
    listener_thread.daemon = True
    listener_thread.start()

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024,
    )

    print("listening... speak into your microphone. Press Ctrl+C to stop.")

    try:
        while True:
            data = stream.read(1024)
            connection.send_media(data)
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()