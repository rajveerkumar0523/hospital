from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path(
        "book/<int:doctor_id>/",
        views.book_appointment,
        name="book",
    ),

    path(
    "cancel/<int:appointment_id>/",
    views.cancel_appointment,
    name="cancel",
    ),
    path(
        "<int:appointment_id>/",
        views.appointment_detail,
        name="detail",
    ),
    path(
        "<int:appointment_id>/prescription/",
        views.save_prescription,
        name="save_prescription",
    ),
    path(
        "<int:appointment_id>/prescription/view/",
        views.prescription_detail,
        name="prescription_detail",
    ),
    path(
        "<int:appointment_id>/tests/order/",
        views.order_tests,
        name="order_tests",
    ),
    path(
        "my-lab-tests/",
        views.patient_lab_tests,
        name="patient_lab_tests",
    ),

    path(
        "my-prescriptions/",
        views.patient_prescriptions,
        name="patient_prescriptions",
    ),
    path(
        "my-lab-tests/<int:test_id>/report/",
        views.patient_lab_report_detail,
        name="patient_lab_report_detail",
    ),
    path(
    "<int:appointment_id>/<str:action>/",
    views.update_appointment_status,
    name="update_status",
),
    
]