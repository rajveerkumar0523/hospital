import re

from .gemini import ask_ai


class ChatbotAI:

    @staticmethod
    def get_reply(message, user):

        text = message.lower()


        # =============================
        # Appointment
        # =============================

        if any(word in text for word in [

            "appointment",

            "booking",

            "next appointment",

            "schedule"

        ]):

            return ChatbotAI.appointment(user)


        # =============================
        # Lab Report
        # =============================

        if any(word in text for word in [

            "report",

            "lab",

            "blood report",

            "test result"

        ]):

            return ChatbotAI.lab_report(user)


        # =============================
        # Prescription
        # =============================

        if any(word in text for word in [

            "prescription",

            "medicine",

            "tablet"

        ]):

            return ChatbotAI.prescription(user)


        # =============================
        # General AI
        # =============================

        prompt = f"""
You are MediCore AI.

You are NOT a doctor.

Answer briefly.

Question:

{message}
"""

        return ask_ai(prompt)
    


# temp file
    @staticmethod
    def appointment(user):

        return (
            "📅 Appointment feature "
            "will be connected "
            "with database."
        )


    @staticmethod
    def lab_report(user):

        return (
            "🧪 Lab Report feature "
            "will be connected "
            "with database."
        )


    @staticmethod
    def prescription(user):

        return (
            "💊 Prescription feature "
            "will be connected "
            "with database."
        )