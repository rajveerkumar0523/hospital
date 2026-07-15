from django.urls import path

from . import views


app_name = "doctors"


urlpatterns = [
    path(
        "",
        views.doctor_list,
        name="list",
    ),

    path(
        "schedule/",
        views.doctor_schedule,
        name="schedule",
    ),

    path(
        "schedule/<int:schedule_id>/toggle/",
        views.toggle_schedule,
        name="toggle_schedule",
    ),

    path(
        "schedule/<int:schedule_id>/delete/",
        views.delete_schedule,
        name="delete_schedule",
    ),
    path(
        "doctor/<int:id>/",
        views.doctor_profile,
        name="doctor_profile",
    )
]