from django.shortcuts import render
from apps.doctors.models import DoctorProfile, Department

def home(request):

    featured_doctors = (
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
        )[:6]
    )

    print(featured_doctors.count())

    departments = Department.objects.order_by("name")

    context = {
        "featured_doctors": featured_doctors,
        "departments": departments,
    }

    return render(
        request,
        "hospital/home.html",
        context,
    )


