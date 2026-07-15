from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

import json

from apps.ai.forms import AppointmentRecommendationForm
from apps.ai.services.appointment_ai import AppointmentAI
from apps.ai.services.symptom_ai import SymptomAI
from apps.ai.services.gemini import ask_ai

from apps.doctors.models import DoctorProfile

from apps.appointments.models import (
    Appointment,
    Prescription,
    TestOrder,
    TestBill,
    TestBillItem,
    LabResult,
)



@login_required
def home(request):

    answer = ""

    try:

        answer = ask_ai(
            "Say Hello from MediCore AI in one short sentence."
        )

    except Exception:

        answer = (
            "Welcome to MediCore AI."
        )

    return render(

        request,

        "ai/home.html",

        {
            "answer": answer
        }

    )


@login_required
def symptom_checker(request):

    return render(

        request,

        "ai/symptom_checker.html"

    )


@login_required
def appointment_recommendation(request):

    result = None

    form = AppointmentRecommendationForm()

    if request.method == "POST":

        form = AppointmentRecommendationForm(
            request.POST
        )

        if form.is_valid():

            result = AppointmentAI.recommend(

                age=form.cleaned_data["age"],

                gender=form.cleaned_data["gender"],

                symptoms=form.cleaned_data["symptoms"],

                duration=form.cleaned_data["duration"],

                severity=form.cleaned_data["severity"],

            )

    return render(

        request,

        "ai/appointment_recommendation.html",

        {

            "form": form,

            "result": result,

        }

    )



@require_POST
@login_required
def appointment_recommendation_api(request):

    form = AppointmentRecommendationForm(

        request.POST

    )

    if not form.is_valid():

        return JsonResponse(

            {

                "success": False,

                "errors": form.errors,

            },

            status=400,

        )

    result = AppointmentAI.recommend(

        age=form.cleaned_data["age"],

        gender=form.cleaned_data["gender"],

        symptoms=form.cleaned_data["symptoms"],

        duration=form.cleaned_data["duration"],

        severity=form.cleaned_data["severity"],

    )

    department = result.get(

        "department",

        ""

    )

    doctor = (

        DoctorProfile.objects.filter(

            department__name__iexact=department,

            status=DoctorProfile.Status.AVAILABLE,

        )

        .first()

    )

    if doctor:

        result["doctor"] = (

            doctor.user.get_full_name()

        )

        result["specialization"] = (

            doctor.specialization

        )
        result["doctor_id"] = doctor.id

    else:

        result["doctor"] = (

            "No doctor available"

        )

        result["specialization"] = "-"
        result["doctor_id"] = None

    return JsonResponse(

        {

            "success": True,

            "result": result,

        }

    )



@require_POST
@login_required
def symptom_checker_api(request):

    symptoms = request.POST.get(

        "symptoms"

    )

    duration = request.POST.get(

        "duration"

    )

    severity = request.POST.get(

        "severity"

    )

    result = SymptomAI.analyze(

        symptoms,

        duration,

        severity,

    )

    return JsonResponse(

        {

            "success": True,

            "result": result,

        }

    )


@login_required
def prescription_summary(request):

    return render(

        request,

        "ai/prescription_summary.html"

    )


@login_required
def report_analysis(request):

    return render(

        request,

        "ai/report_analysis.html"

    )



@login_required
def chatbot(request):

    return render(

        request,

        "ai/chatbot.html"

    )



# ============================================
# AI Chatbot API
# ============================================

@login_required
@require_POST
def chat_api(request):

    try:

        data = json.loads(request.body)

        message = (
            data.get("message", "")
            .strip()
            .lower()
        )

        patient = request.user

        # ------------------------
        # Greeting
        # ------------------------

        greetings = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good evening",
        ]

        intent = detect_intent(message)
        print("MESSAGE =", message)
        print("INTENT =", intent)
        if intent == "appointment":

            return JsonResponse({

                "reply":

                    get_appointment_reply(patient)

            })


        elif intent == "prescription":

            return JsonResponse({

                "reply":

                    get_prescription_reply(patient)

            })


        elif intent == "lab":

            return JsonResponse({

                "reply":

                    get_lab_reply(patient)

            })


        elif intent == "bill":

            return JsonResponse({

                "reply":

                    get_bill_reply(patient)

            })


        elif intent == "doctor":

            return JsonResponse({

                "reply":

                    get_doctor_reply(patient)

            })

            return JsonResponse({

                "reply":
                f"Hello {patient.get_full_name()} 👋\n\n"
                "How can I help you today?"

            })


        # ------------------------
        # Appointment
        # ------------------------

        if any(

            word in message

            for word in [

                "appointment",

                "booking",

                "doctor visit",

                "next appointment",

            ]

        ):

            return JsonResponse({

                "reply":
                get_appointment_reply(
                    patient
                )

            })


        # ------------------------
        # Prescription
        # ------------------------

        if any(

            word in message

            for word in [

                "prescription",

                "medicine",

                "medicines",

                "tablet",

            ]

        ):

            return JsonResponse({

                "reply":
                get_prescription_reply(
                    patient
                )

            })


        # ------------------------
        # Lab Report
        # ------------------------

        if any(

            word in message

            for word in [

                "lab",

                "report",

                "blood",

                "test",

                "result",

            ]

        ):

            return JsonResponse({

                "reply":
                get_lab_reply(
                    patient
                )

            })


        # ------------------------
        # Test Bill
        # ------------------------

        if any(

            word in message

            for word in [

                "bill",

                "payment",

                "invoice",

            ]

        ):

            return JsonResponse({

                "reply":
                get_bill_reply(
                    patient
                )

            })


        # ------------------------
        # AI Fallback
        # ------------------------

        ai_answer = ask_ai(

            f"""
You are MediCore AI.

Answer briefly.

Question:

{message}
"""

        )

        return JsonResponse({

            "reply": ai_answer

        })

    except Exception as e:

        return JsonResponse({

            "reply":
            f"Error: {str(e)}"

        })


# ============================================
# Appointment Helper
# ============================================

def get_appointment_reply(patient):

    appointment = (
        Appointment.objects.filter(
            patient=patient
        )
        .order_by(
            "appointment_date",
            "appointment_time",
        )
        .first()
    )

    if not appointment:

        return (
            "📅 You don't have any upcoming appointments."
        )

    return (
        f"📅 Appointment Details\n\n"
        f"👨‍⚕️ Doctor: {appointment.doctor.user.get_full_name()}\n"
        f"📆 Date: {appointment.appointment_date}\n"
        f"🕒 Time: {appointment.appointment_time}\n"
        f"📌 Status: {appointment.status}"
    )


# ============================================
# Prescription Helper
# ============================================

def get_prescription_reply(patient):

    prescription = (
        Prescription.objects.filter(
            appointment__patient=patient
        )
        .order_by("-created_at")
        .first()
    )

    if not prescription:

        return (
            "💊 No prescription available."
        )

    return (
        f"💊 Latest Prescription\n\n"
        f"Diagnosis:\n"
        f"{prescription.diagnosis}\n\n"
        f"Medicines:\n"
        f"{prescription.medicines}\n\n"
        f"Instructions:\n"
        f"{prescription.instructions}"
    )



# ============================================
# Lab Result Helper
# ============================================

def get_lab_reply(patient):

    report = (
        LabResult.objects.filter(
            test_order__appointment__patient=patient
        )
        .order_by("-completed_at")
        .first()
    )

    if not report:

        return (
            "🧪 No laboratory reports found."
        )

    return (
        f"🧪 Latest Lab Result\n\n"
        f"Test: {report.test_order.test_name}\n"
        f"Status: {report.result_status}\n"
        f"Value: {report.result_value}\n"
        f"Unit: {report.unit}\n\n"
        f"Findings:\n"
        f"{report.findings}"
    )



# ============================================
# Bill Helper
# ============================================

def get_bill_reply(patient):

    bill = (
        TestBill.objects.filter(
            appointment__patient=patient
        )
        .order_by("-created_at")
        .first()
    )

    if not bill:

        return (
            "💳 No bills found."
        )

    text = (
        f"💳 Latest Test Bill\n\n"
        f"Amount: ₹{bill.total_amount}\n"
        f"Status: {bill.payment_status}\n\n"
    )

    items = bill.items.all()

    if items.exists():

        text += "Tests:\n"

        for item in items:

            text += (
                f"• {item.test_name}"
                f" - ₹{item.amount}\n"
            )

    return text



# ============================================
# Intent Detection
# ============================================

def detect_intent(message):

    message = message.lower().strip()

    intents = {

        "appointment": [

            "appointment",

            "book",

            "booking",

            "doctor visit",

            "visit",

            "next appointment",

            "upcoming appointment",

            "meeting doctor",

        ],

        "prescription": [

            "prescription",

            "medicine",

            "tablet",

            "drug",

            "medicines",

            "dose",

        ],

        "lab": [

            "lab",

            "report",

            "blood",

            "test",

            "result",

            "cbc",

            "xray",

            "mri",

            "ct-scan",

            "ct scan",

            "ecg",

            "ultrasound",

        ],

        "bill": [

            "bill",

            "payment",

            "invoice",

            "fee",

            "charges",

        ],

        "doctor": [

            "doctor",

            "physician",

            "consultant",

        ],

    }

    words = message.split()

    for intent, keywords in intents.items():
        for keyword in keywords:
            if " " in keyword:
                if keyword in message:
                    return intent
            else:
                if keyword in words:
                    return intent

    return "ai"





# ============================================
# Doctor Helper
# ============================================

def get_doctor_reply(patient):

    appointment = (

        Appointment.objects.filter(

            patient=patient

        )

        .select_related("doctor")

        .order_by("-appointment_date")

        .first()

    )

    if not appointment:

        return (

            "No doctor found."

        )

    doctor = appointment.doctor

    return (

        f"👨‍⚕️ Doctor Information\n\n"

        f"Name: "

        f"{doctor.user.get_full_name()}\n"

        f"Department: "

        f"{doctor.department.name}\n"

        f"Specialization: "

        f"{doctor.specialization}"

    )