from django.shortcuts import render
from apps.doctors.models import DoctorProfile, Department

def home(request):

    doctors = (
        DoctorProfile.objects
        .select_related(
            "user",
            "department",
        )
        .filter(
            status=DoctorProfile.Status.AVAILABLE,
        )
        .order_by(
            "user__first_name",
        )
    )
    print(doctors.count())

    departments = Department.objects.order_by("name")

    context = {

        "doctors": doctors,

        "departments": departments,

    }

    return render(
        request,
        "hospital/home.html",
        context,
    )