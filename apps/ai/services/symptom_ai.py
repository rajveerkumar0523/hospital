import json

from .gemini import ask_ai
from .prompts import SYMPTOM_PROMPT


class SymptomAI:

    @staticmethod
    def analyze(

        symptoms,

        duration,

        severity

    ):

        prompt=f"""
{SYMPTOM_PROMPT}

Symptoms:
{symptoms}

Duration:
{duration}

Severity:
{severity}
"""

        response=ask_ai(prompt)

        start=response.find("{")

        end=response.rfind("}")

        if start!=-1 and end!=-1:

            response=response[start:end+1]

        return json.loads(response)