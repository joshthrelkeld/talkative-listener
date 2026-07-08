import os
import threading
import numpy as np
import torch
import pyaudio
from dotenv import load_dotenv
from anthropic import Anthropic
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import io

load_dotenv()

# Clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
deepgram_client = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

CLINIC_DATA = {
"name": "Santa Monica Hospital",
"hours": {
    "monday": "9am to 5pm",
    "tuesday": "9am to 5pm",
    "wednesday": "9am to 5pm",
    "thursday": "9am to 5pm",
    "friday": "9am to 4pm"
},
"next_three_days": {
    "Wednesday": "9am to 5pm",
    "Thursday": "9am to 11am, 12pm to 3pm, and 4:30pm",
    "Friday": "9am to 5pm"
},
"services": ["blood testing", "oncology", "neurology", "pediatrics", "gastroenterology", "radiology", "cardiology"],
"insurance_providers": "The Hospital accepts most major insurance providers. If it is in the top 25 within the US, it is accepted",
"doctors": {
    "neurology": "Dr. Alcaraz",
    "oncology": "Dr. Sinner",
    "pediatrics": "Dr. Djokovic",
    "gastroenterology": "Dr. De Minaur",
    "radiology": "Dr. Shelton",
    "cardiology": "Dr. Tiafoe",
},
"appointment_lengths": {
    "neurology": "3 hours",
    "oncology": "3 hours",
    "pediatric": "45 minutes",
    "gastroenterology": "1 hour",
    "radiology": "4 hours",
    "cardiology": "1 hour and a half",
},
"cancellation_policy": "Patients may cancel 48 hours prior to the appointment. However, within the 48 hours before, appointment cancellations are subject to a $50 fee"
}

def build_system_prompt(clinic_data):
    return f"""
You are a receptionist who works at {clinic_data['name']}.
The office hours are {clinic_data['hours']}.
Available appointments for the next three days: {clinic_data['next_three_days']}.
The services offered are: {clinic_data['services']}.
The doctors and their specialties are: {clinic_data['doctors']}.
Appointment lengths by specialty: {clinic_data['appointment_lengths']}.
Cancellation policy: {clinic_data['cancellation_policy']}.
Insurance: {clinic_data['insurance_providers']}.
The four guardrails are: be friendly and courteous, do not ask for unnecessary personal information,
never share other patients' information, and never answer medical questions, redirect to the doctor.
Keep all responses to one or two sentences maximum."""

conversation_history = []
system_prompt = build_system_prompt(CLINIC_DATA)

print("Loading Silero VAD model...")
model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    force_reload=False,
)
print("VAD model loaded.")

THRESHOLD = 0.5
SAMPLE_RATE = 16000
CHUNK = 512

def speak(text):
    print(f"Agent: {text}")
    response = elevenlabs_client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_turbo_v2",
        output_format="mp3_44100_128",
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

def on_message(message):
    if message.type == "Results":
        transcript = message.channel.alternatives[0].transcript
        if not transcript or not message.is_final:
            return

        print(f"Patient: {transcript}")

        conversation_history.append({"role": "user", "content": transcript})

        response = anthropic_client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            system=system_prompt,
            messages=conversation_history,
        )

        response_text = response.content[0].text
        conversation_history.append({"role": "assistant", "content": response_text})

        speak(response_text)

def main():
    with deepgram_client.listen.v1.connect(
        model="nova-3",
        language="en-US",
        smart_format=True,
        encoding="linear16",
        sample_rate=SAMPLE_RATE,
    ) as connection:

        connection.on(EventType.MESSAGE, on_message)

        listener_thread = threading.Thread(target=connection.start_listening)
        listener_thread.daemon = True
        listener_thread.start()

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        speak("Hello, thank you for calling Santa Monica Hospital. How can I help you today?")

        print("Listening... Press Ctrl+C to stop.")

        speech_detected = False

        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                connection.send_media(data)

                audio_chunk = torch.from_numpy(
                    np.frombuffer(data, dtype=np.int16).copy()
                ).float()

                confidence = model(audio_chunk, SAMPLE_RATE).item()

                if confidence >= THRESHOLD:
                    speech_detected = True
                elif speech_detected:
                    speech_detected = False
                    connection.send_finalize()

        except KeyboardInterrupt:
            print("\nEnding call.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    main()