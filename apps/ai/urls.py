from django.urls import path
from . import views

app_name = "ai"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "symptom-checker/",
        views.symptom_checker,
        name="symptom_checker",
    ),
    path(
        "appointment-recommendation/",
        views.appointment_recommendation,
        name="appointment_recommendation",
    ),
    path(
        "prescription-summary/",
        views.prescription_summary,
        name="prescription_summary",
    ),
    path(
        "report-analysis/",
        views.report_analysis,
        name="report_analysis",
    ),
    path(
    "api/appointment-recommendation/",
    views.appointment_recommendation_api,
    name="appointment_recommendation_api",
),
path(
    "symptom-checker/",
    views.symptom_checker,
    name="symptom_checker",
),

path(
    "api/symptom-checker/",
    views.symptom_checker_api,
    name="symptom_checker_api",
),
path(
    "assistant/",
    views.chatbot,
    name="assistant",
),

path(
    "api/chat/",
    views.chat_api,
    name="chat_api",
),


path(

    "chatbot/",

    views.chatbot,

    name="chatbot",

),

path(

    "api/chat/",

    views.chat_api,

    name="chat_api",

),
]