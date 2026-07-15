# Talkative Listener

## What This Is

In simplest terms, I created a **working voice agent you can have a real spoken conversation with.**
On top of that, I built a **patient simulator**: two LLMs talking to one another. One LLM plays the role of a *"patient"*, presenting questions regarding hospital information and appointment scheduling designed to represent ordinary challenges that hospital administrative assistants face. On the opposing end is another LLM playing the role of an *"agent"*, prompted with strict instructions on hospital administration, including scheduling, doctor availability, and maintaining HIPAA-compliance and confidentiality.

---

## Why I Built It

This project began as a requirement for a job application, but I quickly realized that I was unprepared to complete it to the level I wanted in a short timeframe. So, what started as a job requirement became a personal, in-depth project to improve my understanding of **text to speech, speech to text, and prompt engineering**. Using my own knowledge of hospital administration (particularly in Keck Hospital's ICU), I designed the patients so that they are polite and respectful, yet not necessarily agreeable — representative of real, complicated scenarios even a human administrator might struggle to solve.

---

## What I Learned

The specific technical gaps this filled: **async Python, websockets, streaming audio** (using PyAudio), and **real-time pipeline architecture** (using Deepgram, ElevenLabs, and Anthropic). Additionally, this required writing adversarial patient personas with specific goals, pushback rules, and termination signals, then iterating on observed failures. For both *"patients"* and *"agents"*, revision was contingent on bug-specific model failures.

---

## Architecture

Simply put, the pipeline is composed of: **microphone → VAD** (voice activity detection) **→ STT** (speech to text) **→ LLM** (Claude Haiku) **→ TTS** (text to speech). In order to simulate organic, human-esque speech, this pipeline is *concurrent* — pieces of the process constantly overlap rather than waiting for the previous step to finish.

---

## How to Run

**Prerequisites**
- Python 3.12
- Homebrew (macOS)
- portaudio: `brew install portaudio`
- ffmpeg: `brew install ffmpeg`

**Installation**
```bash
git clone https://github.com/joshthrelkeld/talkative-listener
cd talkative-listener
python -m venv venv
source venv/bin/activate
pip install anthropic deepgram-sdk elevenlabs pyaudio pydub torch torchaudio numpy python-dotenv websockets packaging
```

**Setup**

Copy `.env.example` to `.env` and add your API keys:
ANTHROPIC_API_KEY=your_key
DEEPGRAM_API_KEY=your_key
ELEVENLABS_API_KEY=your_key

**Run the voice agent**
```bash
python day7_pipeline.py
```

**Run the patient simulator**
```bash
python day10_scenarios.py
```

---

## What I'd Do Differently

If I did this again, I think it would be interesting to pair **two separate LLM providers** against each other — for example, a GPT-4o *"patient"* trying to navigate a complex scheduling conflict with a Claude *"agent"*. This experiment would be particularly interesting in that it tests whether **different model architectures produce different failure modes**, which has real implications for healthcare AI evaluation.