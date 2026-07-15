
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import TemplateView
from django.shortcuts import render
from apps.doctors.models import DoctorProfile, Department


def home_view(request):

    if request.user.is_authenticated:

        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard:admin")

        if request.user.role == "DOCTOR":
            return redirect("dashboard:doctor")

        if request.user.role == "RECEPTIONIST":
            return redirect("reception:collect_test_payment")

        # if request.user.role == "PATIENT":
        #     return redirect("dashboard:patient")

        if request.user.role == "LAB_TECHNICIAN":
            return redirect("dashboard:lab_technician")

    featured_doctors = (
        DoctorProfile.objects
        .select_related("user", "department")
        .filter(status=DoctorProfile.Status.AVAILABLE)
        .order_by("user__first_name")[:6]
    )

    departments = Department.objects.order_by("name")

    return render(
        request,
        "hospital/home.html",
        {
            "featured_doctors": featured_doctors,
            "departments": departments,
        },
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view,name="home",),
    path("accounts/",include("apps.accounts.urls"),),
    path("patients/",include("apps.patients.urls"),),
    path("dashboard/",include("apps.dashboard.urls"),),
    path("doctors/",include("apps.doctors.urls"),),
    path("appointments/",include("apps.appointments.urls"),),
    path("beds/",include("apps.beds.urls"),),
    path("emergency/",include("apps.emergency.urls"),),
    path("laboratory/",include("apps.laboratory.urls"),),
    path("reception/",include("apps.reception.urls"),),
    path("ai/", include("apps.ai.urls")),
]