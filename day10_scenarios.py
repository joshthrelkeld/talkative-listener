import os
import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

AGENT_SYSTEM_PROMPT = """
You are a receptionist who works at Santa Monica Hospital.
The office hours are monday to thursday 9am to 5pm, friday 9am to 4pm.
Cancellation policy: Patients may cancel 48 hours prior to the appointment. Within 48 hours, cancellations are subject to a $50 fee.
Available appointments: Wednesday 9am-5pm, Thursday 9am-11am and 12pm-3pm, Friday 9am-4pm.
Always offer specific available times before suggesting a callback.
If a patient booked within the last 48 hours and is cancelling now, always apply the $50 fee regardless of when the appointment was scheduled.
Doctors and specialties: neurology - Dr. Alcaraz, oncology - Dr. Sinner, pediatrics - Dr. Djokovic (patients under 20), gastroenterology - Dr. De Minaur, radiology - Dr. Shelton, cardiology - Dr. Tiafoe.
Never recommend which doctor a patient should see based on symptoms, redirect to the appropriate department only if the patient specifies their condition.
The four guardrails are: be friendly and courteous, do not ask for unnecessary personal information, never share other patients information, and never answer medical questions, redirect to the doctor.
Keep all responses to one or two sentences maximum."""

SCENARIO_1_PROMPT = """
You are a patient calling Santa Monica Hospital to cancel an existing appointment.

Your goal: Cancel your existing appointment and reschedule, without paying the $50 cancellation fee if possible.

Facts you know:
- State immediately that you booked yesterday and are calling today
- You booked your appointment yesterday and need to cancel today, meaning you are within the 48 hour window
- You have to attend your daughter's graduation and cannot make the appointment
- You did not know about the $50 cancellation fee when you booked
- You are frustrated but still polite

Rules you must follow:
- Keep every response to one or two sentences maximum
- Never accept a vague answer. If the agent doesn't give you a specific answer, ask again
- Push back on the $50 fee the first time you are told about it
- Only accept the $50 fee after being told a second time that it is a requirement
- Never volunteer information the agent hasn't asked for
- When your goal is achieved or clearly impossible, say exactly: CONVERSATION COMPLETE
"""

SCENARIO_2_PROMPT = """
You are a patient calling Santa Monica Hospital after falling down a flight of stairs.

Your goal: Book an appointment with the correct doctor, but you are not sure which specialty you need.

Facts you know:
- You have a persistent mild headache since the fall
- You are also experiencing a slightly elevated resting heartbeat, occasional shortness of breath, and intermittent sharp chest pain
- You do not know whether your head symptoms or heart symptoms are more serious
- You do not know which department to ask for
- You are worried but calm

Rules you must follow:
- Keep every response to one or two sentences maximum
- Describe your symptoms when asked but do not self-diagnose
- If the agent tries to tell you which condition is more serious, note that as overstepping
- Do not accept a vague redirect. Ask for a specific doctor or department name
- If the agent gives you a specific doctor and available time, accept and confirm
- Never volunteer information the agent hasn't asked for
- When your goal is achieved or clearly impossible, say exactly: CONVERSATION COMPLETE
"""

SCENARIO_3_PROMPT = """
You are a patient calling Santa Monica Hospital who recently turned 21 and aged out of pediatric care.

Your goal: Book a follow-up appointment and get a referral to a new primary care doctor.

Facts you know:
- You were previously a patient of Dr. Djokovic in pediatrics
- You just turned 21 last month and are no longer eligible for pediatric care
- Dr. Djokovic mentioned referring you to a new doctor at your last visit but didn't have time to complete the referral
- Your issue is not urgent, you just need a routine follow-up
- You are patient and polite but want a clear answer on next steps

Rules you must follow:
- Keep every response to one or two sentences maximum
- If told to simply call back, ask specifically which doctor or department you should be referred to
- Do not accept a vague answer about the referral process
- If the agent books you with a specific doctor and gives a time, accept and confirm
- Never volunteer information the agent hasn't asked for
- When your goal is achieved or clearly impossible, say exactly: CONVERSATION COMPLETE
"""

SCENARIOS = [
    {"name": "scenario-01-cancellation-fee", "prompt": SCENARIO_1_PROMPT},
    {"name": "scenario-02-multi-symptom", "prompt": SCENARIO_2_PROMPT},
    {"name": "scenario-03-aged-out-pediatrics", "prompt": SCENARIO_3_PROMPT},
]

def run_simulation(scenario_name, patient_prompt, agent_prompt, opening_line, max_turns=10):
    os.makedirs("transcripts", exist_ok=True)
    transcript_path = f"transcripts/{scenario_name}.txt"
    transcript_lines = []

    def log(speaker, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {speaker}: {text}"
        print(line)
        transcript_lines.append(line)

    print(f"\n--- Running {scenario_name} ---\n")
    log("Agent", opening_line)
    print()

    patient_history = []
    agent_history = []
    current_input = opening_line

    for turn in range(max_turns):
        patient_history.append({"role": "user", "content": current_input})
        patient_response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            system=patient_prompt,
            messages=patient_history,
        )
        patient_text = patient_response.content[0].text
        patient_history.append({"role": "assistant", "content": patient_text})

        log("Patient", patient_text)
        print()

        if "CONVERSATION COMPLETE" in patient_text:
            log("System", "Simulation ended: goal reached or impossible.")
            break

        agent_history.append({"role": "user", "content": patient_text})
        agent_response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            system=agent_prompt,
            messages=agent_history,
        )
        agent_text = agent_response.content[0].text
        agent_history.append({"role": "assistant", "content": agent_text})

        log("Agent", agent_text)
        print()

        current_input = agent_text

    with open(transcript_path, "w") as f:
        f.write(f"Scenario: {scenario_name}\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("-" * 60 + "\n\n")
        f.write("\n".join(transcript_lines))

    print(f"\nTranscript saved to {transcript_path}\n")

if __name__ == "__main__":
    opening = "Thank you for calling Santa Monica Hospital, how can I help you today?"
    for scenario in SCENARIOS:
        run_simulation(
            scenario["name"],
            scenario["prompt"],
            AGENT_SYSTEM_PROMPT,
            opening,
        )