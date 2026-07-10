from django.urls import path

from . import views


app_name = "laboratory"


urlpatterns = [

    path(
        "",
        views.laboratory_dashboard,
        name="dashboard",
    ),
    path(
    "patient/<int:patient_id>/",
    views.patient_tests,
    name="patient_tests",
),
path(
    "test/<int:test_id>/",
    views.test_detail,
    name="test_detail",
),
]