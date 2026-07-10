from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import CustomUser
from apps.appointments.models import LabResult, TestOrder




@login_required
def laboratory_dashboard(request):

    if request.user.role != "LAB_TECHNICIAN":
        return redirect("home")


    # ==========================================
    # PENDING TESTS
    # ==========================================

    pending_tests = (
        TestOrder.objects
        .filter(
            bill_item__bill__payment_status="PAID",
            status__in=[
                TestOrder.Status.ORDERED,
                TestOrder.Status.SAMPLE_COLLECTED,
            ],
        )
        .select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__patient_profile",
            "appointment__doctor",
            "appointment__doctor__user",
        )
        .order_by(
            "appointment__patient_id",
            "-ordered_at",
        )
    )


    # SAME PATIENT KE PENDING TESTS GROUP KARNA

    patients_map = {}

    for test in pending_tests:

        patient = test.appointment.patient

        if patient.id not in patients_map:

            patients_map[patient.id] = {
                "patient": patient,
                "tests": [],
                "test_count": 0,
            }

        patients_map[patient.id]["tests"].append(test)
        patients_map[patient.id]["test_count"] += 1


    patient_queue = list(
        patients_map.values()
    )


    # ==========================================
    # COMPLETED / TESTED REPORTS
    # ==========================================

    completed_tests = (
        TestOrder.objects
        .filter(
            bill_item__bill__payment_status="PAID",
            status__in=[
                TestOrder.Status.REPORT_READY,
                TestOrder.Status.REVIEWED,
            ],
            lab_result__isnull=False,
        )
        .select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__patient_profile",
            "appointment__doctor",
            "appointment__doctor__user",
            "lab_result",
        )
        .order_by(
            "appointment__patient_id",
            "-updated_at",
        )
    )


    # SAME PATIENT KE COMPLETED REPORTS GROUP KARNA

    completed_patients_map = {}

    for test in completed_tests:

        patient = test.appointment.patient

        if patient.id not in completed_patients_map:

            completed_patients_map[patient.id] = {
                "patient": patient,
                "tests": [],
                "test_count": 0,
                "latest_test": test,
            }

        completed_patients_map[
            patient.id
        ]["tests"].append(test)

        completed_patients_map[
            patient.id
        ]["test_count"] += 1


    completed_patient_queue = list(
        completed_patients_map.values()
    )


    # ==========================================
    # CONTEXT
    # ==========================================

    context = {
        "patient_queue": patient_queue,
        "patient_count": len(patient_queue),
        "pending_test_count": pending_tests.count(),

        "completed_patient_queue": completed_patient_queue,
        "completed_patient_count": len(
            completed_patient_queue
        ),
        "completed_test_count": completed_tests.count(),
    }


    return render(
        request,
        "laboratory/dashboard.html",
        context,
    )


@login_required
def patient_tests(request, patient_id):

    if request.user.role != "LAB_TECHNICIAN":
        return redirect("home")

    patient = get_object_or_404(
        CustomUser.objects.select_related(
            "patient_profile",
        ),
        id=patient_id,
        role=CustomUser.Role.PATIENT,
    )

    tests = (
        TestOrder.objects
        .filter(
            appointment__patient=patient,
            bill_item__bill__payment_status="PAID",
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

    pending_tests = tests.filter(
        status__in=[
            TestOrder.Status.ORDERED,
            TestOrder.Status.SAMPLE_COLLECTED,
        ],
    )

    completed_tests = tests.filter(
        status__in=[
            TestOrder.Status.REPORT_READY,
            TestOrder.Status.REVIEWED,
        ],
    )

    context = {
        "patient": patient,
        "pending_tests": pending_tests,
        "completed_tests": completed_tests,
        "pending_count": pending_tests.count(),
        "completed_count": completed_tests.count(),
    }

    return render(
        request,
        "laboratory/patient_tests.html",
        context,
    )

@login_required
def test_detail(request, test_id):

    if request.user.role != "LAB_TECHNICIAN":
        return redirect("home")

    test = get_object_or_404(
        TestOrder.objects.select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__patient_profile",
            "appointment__doctor",
            "appointment__doctor__user",
            "appointment__doctor__department",
            "lab_result",
        ),
        id=test_id,
        bill_item__bill__payment_status="PAID",
    )

    if request.method == "POST":

        result_status = request.POST.get(
            "result_status",
            "",
        ).strip()

        result_value = request.POST.get(
            "result_value",
            "",
        ).strip()

        unit = request.POST.get(
            "unit",
            "",
        ).strip()

        reference_range = request.POST.get(
            "reference_range",
            "",
        ).strip()

        findings = request.POST.get(
            "findings",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        remarks = request.POST.get(
            "remarks",
            "",
        ).strip()


        # REQUIRED FIELDS

        if not result_status or not findings:

            messages.error(
                request,
                "Result status and findings are required.",
            )

            return render(
                request,
                "laboratory/test_detail.html",
                {
                    "test": test,
                },
            )


        # VALIDATE RESULT STATUS

        valid_statuses = {
            value
            for value, label
            in LabResult.ResultStatus.choices
        }

        if result_status not in valid_statuses:

            messages.error(
                request,
                "Invalid result status.",
            )

            return redirect(
                "laboratory:test_detail",
                test_id=test.id,
            )


        # CREATE OR UPDATE RESULT

        LabResult.objects.update_or_create(
            test_order=test,
            defaults={
                "result_status": result_status,
                "result_value": result_value,
                "unit": unit,
                "reference_range": reference_range,
                "findings": findings,
                "description": description,
                "remarks": remarks,
                "tested_by": request.user,
            },
        )


        # MARK TEST AS COMPLETED

        test.status = TestOrder.Status.REPORT_READY

        test.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


        messages.success(
            request,
            "Test result saved successfully.",
        )


        # RETURN TO SAME PATIENT

        return redirect(
            "laboratory:patient_tests",
            patient_id=test.appointment.patient_id,
        )


    return render(
        request,
        "laboratory/test_detail.html",
        {
            "test": test,
        },
    )