import json

from .gemini import ask_ai
from .prompts import APPOINTMENT_PROMPT


class AppointmentAI:

    @staticmethod
    def recommend(age, gender, symptoms, duration, severity):

        prompt = f"""
{APPOINTMENT_PROMPT}

Age: {age}

Gender: {gender}

Symptoms:
{symptoms}

Duration:
{duration}

Severity:
{severity}
"""

        response = ask_ai(prompt)

        # -----------------------------
        # Clean Gemini Response
        # -----------------------------

        response = response.strip()

        if response.startswith("```json"):
            response = response.replace("```json", "", 1)

        if response.startswith("```"):
            response = response.replace("```", "", 1)

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        print("\n========== GEMINI RESPONSE ==========")
        print(response)
        print("=====================================\n")

        try:

            return json.loads(response)

        except json.JSONDecodeError as e:

            print("JSON ERROR:", e)

            return {
                "department": "General Medicine",
                "priority": "Medium",
                "reason": "AI returned an invalid response."
            }