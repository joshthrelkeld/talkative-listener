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