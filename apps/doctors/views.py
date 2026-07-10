from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.appointments.models import Appointment
from .decorators import doctor_required

from .models import (
    Department,
    DoctorAvailability,
    DoctorProfile,
)


def doctor_list(request):
    departments = Department.objects.filter(
        is_active=True
    )

    doctors = (
        DoctorProfile.objects
        .filter(
            status=DoctorProfile.Status.AVAILABLE
        )
        .select_related(
            "user",
            "department",
        )
    )

    department_id = request.GET.get("department")

    if department_id:
        doctors = doctors.filter(
            department_id=department_id
        )

    return render(
        request,
        "doctors/doctor_list.html",
        {
            "doctors": doctors,
            "departments": departments,
            "selected_department": department_id,
        },
    )


@doctor_required
def doctor_schedule(request):

    doctor = get_object_or_404(
        DoctorProfile,
        user=request.user,
    )

    availabilities = (
        DoctorAvailability.objects
        .filter(doctor=doctor)
        .order_by(
            "day_of_week",
            "start_time",
        )
    )

    # TODAY'S DATE
    today = timezone.localdate()

    # TODAY'S PATIENT APPOINTMENTS
    todays_appointments = (
        Appointment.objects
        .filter(
            doctor=doctor,
            appointment_date=today,
        )
        .exclude(
            status=Appointment.Status.CANCELLED,
        )
        .select_related("patient")
        .order_by("appointment_time")
    )

    if request.method == "POST":

        day_of_week = request.POST.get(
            "day_of_week"
        )

        start_time = request.POST.get(
            "start_time"
        )

        end_time = request.POST.get(
            "end_time"
        )

        slot_duration = request.POST.get(
            "slot_duration"
        )

        # REQUIRED FIELDS
        if not all([
            day_of_week,
            start_time,
            end_time,
            slot_duration,
        ]):
            messages.error(
                request,
                "Please fill all schedule fields.",
            )

            return redirect(
                "doctors:schedule"
            )

        # TIME VALIDATION
        if start_time >= end_time:
            messages.error(
                request,
                "End time must be after start time.",
            )

            return redirect(
                "doctors:schedule"
            )

        # DUPLICATE CHECK
        schedule_exists = (
            DoctorAvailability.objects
            .filter(
                doctor=doctor,
                day_of_week=day_of_week,
                start_time=start_time,
            )
            .exists()
        )

        if schedule_exists:
            messages.error(
                request,
                "This schedule already exists.",
            )

            return redirect(
                "doctors:schedule"
            )

        # CREATE SCHEDULE
        DoctorAvailability.objects.create(
            doctor=doctor,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            slot_duration=slot_duration,
        )

        messages.success(
            request,
            "Schedule added successfully.",
        )

        return redirect(
            "doctors:schedule"
        )

    # IMPORTANT: TODAY'S DATA YAHAN PASS HOGA
    return render(
        request,
        "doctors/doctor_schedule.html",
        {
            "doctor": doctor,
            "availabilities": availabilities,
            "day_choices": DoctorAvailability.Day.choices,
            "today": today,
            "todays_appointments": todays_appointments,
        },
    )


@doctor_required
def toggle_schedule(request, schedule_id):

    if request.method != "POST":
        return redirect("doctors:schedule")

    doctor = get_object_or_404(
        DoctorProfile,
        user=request.user,
    )

    availability = get_object_or_404(
        DoctorAvailability,
        id=schedule_id,
        doctor=doctor,
    )

    availability.is_active = not availability.is_active

    availability.save(
        update_fields=["is_active"]
    )

    if availability.is_active:
        messages.success(
            request,
            "Schedule activated successfully.",
        )
    else:
        messages.success(
            request,
            "Schedule deactivated successfully.",
        )

    return redirect("doctors:schedule")


@doctor_required
def delete_schedule(request, schedule_id):

    if request.method != "POST":
        return redirect("doctors:schedule")

    doctor = get_object_or_404(
        DoctorProfile,
        user=request.user,
    )

    availability = get_object_or_404(
        DoctorAvailability,
        id=schedule_id,
        doctor=doctor,
    )

    availability.delete()

    messages.success(
        request,
        "Schedule deleted successfully.",
    )

    return redirect("doctors:schedule")