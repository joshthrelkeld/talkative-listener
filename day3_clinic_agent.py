import os
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

CLINIC_DATA = {
"name": "Santa Monica Hospital",
"hours": {
    "monday": "9am to 5pm",
    "tuesday": "9am to 5pm",
    "wednesday": "9am to 5pm",
    "thursday": "9am to 5pm",
    "friday": "9am to 4pm"
},
"next_three_days": "There are appointments each day at 11am, 12pm , and 3:15 pm",
"services": ["blood testing", "oncology", "surgery"],
"insurance_providers": "The Hospital accepts most major insurance providers. If it is in the top 25 within the US, it is accepted"
}

def build_system_prompt(clinic_data):
    return f"""
You are a receptionist who works at {clinic_data['name']}
The office hours are {clinic_data['hours']}
In the next three days, the available appointments are at {clinic_data['next_three_days']}
The services are {clinic_data['services']}
The four guardrails are: be friendly and courteous, do not ask for unnecessary personal information, 
never share other patients' information, and never answer medical questions, redirect to the doctor.
Keep all responses to one or two sentences maximum."""

client = Anthropic()
conversation_history = []
system_prompt = build_system_prompt(CLINIC_DATA)

while True:
    user_input = input("Patient: ")

    if user_input.lower() == "quit":
        break

    conversation_history.append({"role": "user", "content": user_input})

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=conversation_history
    )

    response_text = message.content[0].text

    print(f"Receptionist: {response_text}")

    conversation_history.append({"role": "assistant", "content": response_text})