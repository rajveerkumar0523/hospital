from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.doctors.models import DoctorAvailability, DoctorProfile

from .models import Appointment


from decimal import Decimal
from .models import (
    Appointment,
    Prescription,
    TestBill,
    TestBillItem,
    TestOrder,
)


@login_required
def book_appointment(request, doctor_id):
    if request.user.role != "PATIENT":
        messages.error(
            request,
            "Only patients can book appointments."
        )

        if request.user.role == "DOCTOR":
            return redirect("dashboard:doctor")

        return redirect("home")

    doctor = get_object_or_404(
        DoctorProfile.objects.select_related(
            "user",
            "department",
        ),
        id=doctor_id,
        status=DoctorProfile.Status.AVAILABLE,
    )

    selected_date = request.GET.get("date")

    available_slots = []

    if selected_date:

        try:
            appointment_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            appointment_date = None

        if appointment_date:

            # Python:
            # Monday = 0
            # Sunday = 6
            day_of_week = appointment_date.weekday()

            availabilities = DoctorAvailability.objects.filter(
                doctor=doctor,
                day_of_week=day_of_week,
                is_active=True,
            )

            booked_times = set(
                Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=appointment_date,
                    status__in=[
                        Appointment.Status.PENDING,
                        Appointment.Status.CONFIRMED,
                    ],
                ).values_list(
                    "appointment_time",
                    flat=True,
                )
            )

            for availability in availabilities:

                current_time = datetime.combine(
                    appointment_date,
                    availability.start_time,
                )

                end_time = datetime.combine(
                    appointment_date,
                    availability.end_time,
                )

                while current_time < end_time:

                    slot_time = current_time.time()

                    if slot_time not in booked_times:
                        available_slots.append(
                            slot_time.strftime("%H:%M")
                        )

                    current_time += timedelta(
                        minutes=availability.slot_duration
                    )

    if request.method == "POST":

        selected_date = request.POST.get("appointment_date")
        selected_time = request.POST.get("appointment_time")
        reason = request.POST.get("reason", "").strip()

        if not selected_date or not selected_time or not reason:
            messages.error(
                request,
                "Please complete all appointment details.",
            )

            return redirect(
                f"/appointments/book/{doctor.id}/" # type: ignore
                f"?date={selected_date}"
            )

        appointment_date = datetime.strptime(
            selected_date,
            "%Y-%m-%d",
        ).date()

        appointment_time = datetime.strptime(
            selected_time,
            "%H:%M",
        ).time()

        # Prevent booking past dates
        if appointment_date < timezone.localdate():
            messages.error(
                request,
                "You cannot book an appointment in the past.",
            )

            return redirect(
                "appointments:book",
                doctor_id=doctor.id, # pyright: ignore[reportAttributeAccessIssue]
            )

        # Final duplicate-slot protection
        slot_taken = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ],
        ).exists()

        if slot_taken:
            messages.error(
                request,
                "This slot has already been booked.",
            )

            return redirect(
                f"/appointments/book/{doctor.id}/" # type: ignore
                f"?date={selected_date}"
            )

        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
        )

        messages.success(
            request,
            "Appointment booked successfully.",
        )

        return redirect("dashboard:patient")

    context = {
        "doctor": doctor,
        "selected_date": selected_date,
        "available_slots": available_slots,
        "today": timezone.localdate().isoformat(),
    }

    return render(
        request,
        "appointments/book_appointment.html",
        context,
    )

@login_required
def cancel_appointment(request, appointment_id):

    if request.user.role != "PATIENT":
        return redirect("home")

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user,
    )

    if request.method == "POST":

        if appointment.status in [
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
        ]:
            appointment.status = Appointment.Status.CANCELLED

            appointment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Appointment cancelled successfully.",
            )

        else:
            messages.error(
                request,
                "This appointment cannot be cancelled.",
            )

    return redirect("dashboard:patient")


@login_required
def update_appointment_status(request, appointment_id, action):

    if request.method != "POST":
        return redirect("dashboard:doctor")

    if request.user.role != "DOCTOR":
        return redirect("home")

    doctor = get_object_or_404(
        DoctorProfile,
        user=request.user,
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor,
    )

    if action == "confirm":
        appointment.status = Appointment.Status.CONFIRMED
        message = "Appointment confirmed successfully."

    elif action == "complete":
        appointment.status = Appointment.Status.COMPLETED
        message = "Appointment marked as completed."

    elif action == "cancel":
        appointment.status = Appointment.Status.CANCELLED
        message = "Appointment cancelled successfully."

    else:
        messages.error(
            request,
            "Invalid appointment action.",
        )
        return redirect("dashboard:doctor")

    appointment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        message,
    )

    return redirect("dashboard:doctor")
@login_required
def appointment_detail(request, appointment_id):

    if request.user.role != "DOCTOR":
        return redirect("home")

    doctor = get_object_or_404(
        DoctorProfile,
        user=request.user,
    )

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "patient",
            "doctor",
            "doctor__department",
        ),
        id=appointment_id,
        doctor=doctor,
    )

    patient_profile = getattr(
        appointment.patient,
        "patient_profile",
        None,
    )

    # ALL TESTS OF THIS APPOINTMENT
    test_orders = (
        TestOrder.objects
        .filter(appointment=appointment)
        .select_related(
            "lab_result",
            "lab_result__tested_by",
        )
        .order_by("ordered_at")
    )

    has_tests = test_orders.exists()

    pending_tests = test_orders.filter(
        status__in=[
            TestOrder.Status.ORDERED,
            TestOrder.Status.SAMPLE_COLLECTED,
        ]
    ).exists()

    report_ready = test_orders.filter(
        status__in=[
            TestOrder.Status.REPORT_READY,
            TestOrder.Status.REVIEWED,
        ],
        lab_result__isnull=False,
    ).exists()

    all_reports_ready = (
        has_tests
        and not pending_tests
        and not test_orders.exclude(
            status__in=[
                TestOrder.Status.REPORT_READY,
                TestOrder.Status.REVIEWED,
            ]
        ).exists()
    )

    # SAVED PRESCRIPTION
    prescription = (
        Prescription.objects
        .filter(appointment=appointment)
        .first()
    )

    # DISPLAY STATUS
    if prescription:
        display_status = "COMPLETED"

    elif all_reports_ready:
        display_status = "REPORT READY"

    elif pending_tests:
        display_status = "AWAITING TESTS"

    else:
        display_status = appointment.get_status_display().upper() # type: ignore

    context = {
        "appointment": appointment,
        "patient": appointment.patient,
        "patient_profile": patient_profile,

        "test_orders": test_orders,
        "has_tests": has_tests,
        "report_ready": report_ready,
        "all_reports_ready": all_reports_ready,

        "prescription": prescription,
        "display_status": display_status,
    }

    return render(
        request,
        "appointments/appointment_detail.html",
        context,
    )

@login_required
def save_prescription(request, appointment_id):

    if request.user.role != "DOCTOR":
        return redirect("home")

    if request.method != "POST":
        return redirect(
            "appointments:detail",
            appointment_id=appointment_id,
        )

    doctor = get_object_or_404(
        DoctorProfile,
        user=request.user,
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor,
    )

    if appointment.status == Appointment.Status.CANCELLED:
        messages.error(
            request,
            "Prescription cannot be added to a cancelled appointment.",
        )

        return redirect(
            "appointments:detail",
            appointment_id=appointment.id, # type: ignore
        )

    diagnosis = request.POST.get(
        "diagnosis",
        "",
    ).strip()

    medicines = request.POST.get(
        "medicines",
        "",
    ).strip()

    instructions = request.POST.get(
        "instructions",
        "",
    ).strip()

    follow_up_date = request.POST.get(
        "follow_up_date",
        "",
    )

    if not diagnosis or not medicines:
        messages.error(
            request,
            "Diagnosis and medicines are required.",
        )

        return redirect(
            "appointments:detail",
            appointment_id=appointment.id,
        )

    Prescription.objects.update_or_create(
        appointment=appointment,
        defaults={
            "diagnosis": diagnosis,
            "medicines": medicines,
            "instructions": instructions,
            "follow_up_date": (
                follow_up_date
                if follow_up_date
                else None
            ),
        },
    )

    appointment.status = Appointment.Status.COMPLETED

    appointment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "Prescription saved and appointment completed.",
    )

    return redirect(
        "appointments:detail",
        appointment_id=appointment.id,
    )

@login_required
def prescription_detail(request, appointment_id):

    if request.user.role != "PATIENT":
        return redirect("home")

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "doctor",
            "doctor__user",
            "doctor__department",
        ),
        id=appointment_id,
        patient=request.user,
        status=Appointment.Status.COMPLETED,
    )

    prescription = get_object_or_404(
        Prescription,
        appointment=appointment,
    )

    return render(
        request,
        "appointments/prescription_detail.html",
        {
            "appointment": appointment,
            "prescription": prescription,
        },
    )

@login_required
def order_tests(request, appointment_id):

    if request.user.role != "DOCTOR":
        return redirect("home")

    if request.method != "POST":
        return redirect(
            "appointments:detail",
            appointment_id=appointment_id,
        )

    doctor = get_object_or_404(
        DoctorProfile,
        user=request.user,
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor,
    )

    if appointment.status != Appointment.Status.CONFIRMED:
        messages.error(
            request,
            "Tests can only be ordered for confirmed appointments.",
        )

        return redirect(
            "appointments:detail",
            appointment_id=appointment.id,
        )

    test_types = request.POST.getlist(
        "test_type"
    )

    custom_test_name = request.POST.get(
        "custom_test_name",
        "",
    ).strip()

    instructions = request.POST.get(
        "test_instructions",
        "",
    ).strip()

    if not test_types:
        messages.error(
            request,
            "Please select at least one test.",
        )

        return redirect(
            "appointments:detail",
            appointment_id=appointment.id,
        )

    # TEST FEES
    test_fees = {
        TestOrder.TestType.BLOOD: Decimal("500.00"),
        TestOrder.TestType.URINE: Decimal("300.00"),
        TestOrder.TestType.XRAY: Decimal("800.00"),
        TestOrder.TestType.ULTRASOUND: Decimal("1200.00"),
        TestOrder.TestType.ECG: Decimal("700.00"),
        TestOrder.TestType.CT_SCAN: Decimal("3500.00"),
        TestOrder.TestType.MRI: Decimal("6000.00"),
        TestOrder.TestType.OTHER: Decimal("0.00"),
    }

    # CREATE OR GET TEST BILL
    bill, bill_created = TestBill.objects.get_or_create(
        appointment=appointment,
    )

    tests_created = 0

    for test_type in test_types:

        if test_type not in TestOrder.TestType.values:
            continue

        if test_type == TestOrder.TestType.OTHER:

            if not custom_test_name:
                continue

            test_name = custom_test_name

        else:
            test_name = dict(
                TestOrder.TestType.choices
            )[test_type]

        fee = test_fees.get(
            test_type,
            Decimal("0.00"),
        )

        # CREATE TEST ORDER
        test_order = TestOrder.objects.create(
            appointment=appointment,
            test_type=test_type,
            test_name=test_name,
            fee=fee,
            instructions=instructions,
        )

        # ADD TEST TO BILL
        TestBillItem.objects.create(
            bill=bill,
            test_order=test_order,
            test_name=test_name,
            amount=fee,
        )

        tests_created += 1

    # NO VALID TEST CREATED
    if tests_created == 0:

        if bill_created:
            bill.delete()

        messages.error(
            request,
            "No valid tests were selected.",
        )

        return redirect(
            "appointments:detail",
            appointment_id=appointment.id, # type: ignore
        )

    # CALCULATE FINAL BILL TOTAL
    bill.total_amount = sum(
        item.amount
        for item in bill.items.all()
    )

    bill.save(
        update_fields=[
            "total_amount",
            "updated_at",
        ]
    )

    # APPOINTMENT NOW WAITS FOR TESTS
    appointment.status = (
        Appointment.Status.AWAITING_TESTS
    )

    appointment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        (
            f"{tests_created} test(s) ordered successfully. "
            f"Test bill: ₹{bill.total_amount}"
        ),
    )

    return redirect(
        "appointments:detail",
        appointment_id=appointment.id,
    )

@login_required
def patient_lab_tests(request):

    if request.user.role != "PATIENT":
        return redirect("home")

    test_orders = (
        TestOrder.objects
        .filter(
            appointment__patient=request.user,
        )
        .select_related(
            "appointment",
            "appointment__doctor",
            "appointment__doctor__user",
            "appointment__doctor__department",
            "lab_result",
        )
        .order_by("-ordered_at")
    )

    return render(
        request,
        "appointments/patient_lab_tests.html",
        {
            "test_orders": test_orders,
        },
    )
@login_required
def patient_lab_report_detail(request, test_id):

    if request.user.role != "PATIENT":
        return redirect("home")

    test = get_object_or_404(
        TestOrder.objects.select_related(
            "appointment",
            "appointment__patient",
            "appointment__doctor",
            "appointment__doctor__user",
            "appointment__doctor__department",
            "lab_result",
            "lab_result__tested_by",
        ),
        id=test_id,
        appointment__patient=request.user,
        status__in=[
            TestOrder.Status.REPORT_READY,
            TestOrder.Status.REVIEWED,
        ],
        lab_result__isnull=False,
    )

    return render(
        request,
        "appointments/patient_lab_report_detail.html",
        {
            "test": test,
        },
    )

@login_required
def patient_prescriptions(request):

    if request.user.role != "PATIENT":
        return redirect("home")

    prescriptions = (
        Prescription.objects
        .filter(
            appointment__patient=request.user,
        )
        .select_related(
            "appointment",
            "appointment__doctor",
            "appointment__doctor__user",
            "appointment__doctor__department",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "appointments/patient_prescriptions.html",
        {
            "prescriptions": prescriptions,
        },
    )