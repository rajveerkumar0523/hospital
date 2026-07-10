from django.shortcuts import render

from .models import Ambulance


def emergency_request(request):

    ambulances = (
        Ambulance.objects
        .filter(is_active=True)
        .order_by("ambulance_number")
    )

    context = {
        "ambulances": ambulances,

        "total_ambulances": ambulances.count(),

        "available_ambulances": ambulances.filter(
            status=Ambulance.Status.AVAILABLE
        ).count(),

        "on_duty_ambulances": ambulances.filter(
            status=Ambulance.Status.ON_DUTY
        ).count(),
    }

    return render(
        request,
        "emergency/emergency_request.html",
        context,
    )