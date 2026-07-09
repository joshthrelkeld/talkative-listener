import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PATIENT_SYSTEM_PROMPT = """
You are a patient calling Santa Monica Hospital to cancel an existing appointment.

Your goal: Cancel your existing appointment and reschedule, without paying the $50 cancellation fee if possible.

Facts you know:
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

AGENT_SYSTEM_PROMPT = """
You are a receptionist who works at Santa Monica Hospital.
The office hours are monday to thursday 9am to 5pm, friday 9am to 4pm.
Cancellation policy: Patients may cancel 48 hours prior to the appointment. Within 48 hours, cancellations are subject to a $50 fee.
The four guardrails are: be friendly and courteous, do not ask for unnecessary personal information,
never share other patients information, and never answer medical questions, redirect to the doctor.
Keep all responses to one or two sentences maximum."""

def run_simulation(patient_prompt, agent_prompt, opening_line, max_turns=10):
    patient_history = []
    agent_history = []

    print(f"Agent: {opening_line}")
    print()

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

        print(f"Patient: {patient_text}")
        print()

        if "CONVERSATION COMPLETE" in patient_text:
            print("Simulation ended: goal reached or impossible.")
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

        print(f"Agent: {agent_text}")
        print()

        current_input = agent_text

if __name__ == "__main__":
    opening = "Thank you for calling Santa Monica Hospital, how can I help you today?"
    run_simulation(PATIENT_SYSTEM_PROMPT, AGENT_SYSTEM_PROMPT, opening)