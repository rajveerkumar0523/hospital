from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import TemplateView


def home_view(request):

    if request.user.is_authenticated:

        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard:admin")

        if request.user.role == "DOCTOR":
            return redirect("dashboard:doctor")
        
        if request.user.role == "RECEPTIONIST":
             return redirect("reception:collect_test_payment")

        if request.user.role == "PATIENT":
            return redirect("dashboard:patient")
        if request.user.role == "LAB_TECHNICIAN":
            return redirect("dashboard:lab_technician")

    return TemplateView.as_view(
        template_name="hospital/home.html"
    )(request)


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "",
        home_view,
        name="home",
    ),

    path(
        "accounts/",
        include("apps.accounts.urls"),
    ),

    path(
        "patients/",
        include("apps.patients.urls"),
    ),

    path(
        "dashboard/",
        include("apps.dashboard.urls"),
    ),

    path(
        "doctors/",
        include("apps.doctors.urls"),
    ),

    path(
        "appointments/",
        include("apps.appointments.urls"),
    ),
    path(
    "beds/",
    include("apps.beds.urls"),
),
  path(
    "emergency/",
    include("apps.emergency.urls"),
),
path(
    "laboratory/",
    include("apps.laboratory.urls"),
),
path(
    "reception/",
    include("apps.reception.urls"),
),
]