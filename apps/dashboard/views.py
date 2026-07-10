from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.accounts.models import CustomUser
from apps.appointments.models import (
    Appointment,
    LabResult,
    TestBill,
    TestOrder,
)
from apps.beds.models import Bed
from apps.doctors.models import Department, DoctorProfile
from apps.emergency.models import Ambulance

from django.views.decorators.http import require_POST


@login_required
def patient_dashboard(request):

    if request.user.role != "PATIENT":
        return redirect("dashboard:doctor")

    if not hasattr(request.user, "patient_profile"):
        return redirect("patients:complete_profile")

    patient = request.user.patient_profile

    appointments = (
        Appointment.objects
        .filter(patient=request.user)
        .select_related(
            "doctor",
            "doctor__user",
            "doctor__department",
            "test_bill",
            "prescription",
        )
        .order_by(
            "appointment_date",
            "appointment_time",
        )
    )

    prescription_appointments = appointments.filter(
        prescription__isnull=False,
    )

    ready_lab_tests = (
        TestOrder.objects
        .filter(
            appointment__patient=request.user,
            status__in=[
                TestOrder.Status.REPORT_READY,
                TestOrder.Status.REVIEWED,
            ],
            lab_result__isnull=False,
        )
        .select_related(
            "appointment",
            "appointment__doctor",
            "appointment__doctor__user",
            "appointment__doctor__department",
            "lab_result",
            "lab_result__tested_by",
        )
        .order_by("-updated_at")
    )
    recent_medical_activity = []

    for appointment in prescription_appointments:
        recent_medical_activity.append({
            "type": "prescription",
            "date": appointment.prescription.created_at, # type: ignore
            "appointment": appointment,
        })

    for test in ready_lab_tests:
        recent_medical_activity.append({
            "type": "lab_report",
            "date": test.updated_at,
            "test": test,
        })

    recent_medical_activity.sort(
        key=lambda item: item["date"],
        reverse=True,
    )

    recent_medical_activity = recent_medical_activity[:5]
    context = {
        "patient": patient,
        "appointments": appointments,
        "appointment_count": appointments.count(),
        "ready_lab_tests": ready_lab_tests,
        "recent_medical_activity": recent_medical_activity,

        "upcoming_appointments": appointments.filter(
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ],
        ).count(),

        "pending_reports": 0,

        "active_prescriptions": prescription_appointments.count(),

        "prescription_appointments": prescription_appointments,
    }

    return render(
        request,
        "dashboard/patient_dashboard.html",
        context,
    )


@login_required
def doctor_dashboard(request):

    if request.user.role != "DOCTOR":
        return redirect("dashboard:patient")

    if not hasattr(request.user, "doctor_profile"):
        return redirect("home")

    doctor = request.user.doctor_profile
    today = timezone.localdate()

    all_appointments = (
        Appointment.objects
        .filter(doctor=doctor)
        .select_related(
            "patient",
            "patient__patient_profile",
        )
    )
    ready_lab_reports = (
        TestOrder.objects
        .filter(
            appointment__doctor=doctor,
            status=TestOrder.Status.REPORT_READY,
            lab_result__isnull=False,
        )
        .select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__patient_profile",
            "lab_result",
            "lab_result__tested_by",
        )
        .order_by("-updated_at")
    )

    selected_filter = request.GET.get(
        "filter",
        "today",
    )

    if selected_filter == "today":
        appointments = all_appointments.filter(
            appointment_date=today,
        )

    elif selected_filter == "upcoming":
        appointments = all_appointments.filter(
            appointment_date__gte=today,
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ],
        )

    else:
        selected_filter = "all"
        appointments = all_appointments

    appointments = appointments.order_by(
        "appointment_date",
        "appointment_time",
    )
    ready_lab_tests = (
    TestOrder.objects
    .filter(
        appointment__doctor=doctor,
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
        "lab_result",
    )
    .order_by("-updated_at")
   )
    for appointment in appointments:

        test_orders = appointment.test_orders.all() # type: ignore

        appointment.has_report_ready = test_orders.filter( # type: ignore
            status__in=[
                TestOrder.Status.REPORT_READY,
                TestOrder.Status.REVIEWED,
            ],
            lab_result__isnull=False,
        ).exists()

        appointment.has_pending_tests = test_orders.filter( # type: ignore
            status__in=[
                TestOrder.Status.ORDERED,
                TestOrder.Status.SAMPLE_COLLECTED,
            ],
        ).exists()
        appointment.has_prescription = hasattr( # type: ignore
            appointment,
            "prescription",
        )

    context = {
        "doctor": doctor,
        "appointments": appointments,
        "selected_filter": selected_filter,
        "ready_lab_tests": ready_lab_tests,
        "ready_lab_reports_count": ready_lab_tests.count(),
        "ready_lab_reports": ready_lab_reports,
        "ready_lab_report_count": ready_lab_reports.count(),

        "today_count": all_appointments.filter(
            appointment_date=today,
        ).count(),

        "upcoming_count": all_appointments.filter(
            appointment_date__gte=today,
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ],
        ).count(),

        "all_count": all_appointments.count(),

        "pending_count": all_appointments.filter(
            status=Appointment.Status.PENDING,
        ).count(),

        "confirmed_count": all_appointments.filter(
            status=Appointment.Status.CONFIRMED,
        ).count(),

        "completed_count": all_appointments.filter(
            status=Appointment.Status.COMPLETED,
        ).count(),
    }

    return render(
        request,
        "dashboard/doctor_dashboard.html",
        context,
    )

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect("home")

    context = {
        "total_doctors": DoctorProfile.objects.count(),

        "total_patients": CustomUser.objects.filter(
            role="PATIENT",
        ).count(),

        "total_appointments": Appointment.objects.count(),

        "pending_appointments": Appointment.objects.filter(
            status=Appointment.Status.PENDING,
        ).count(),

        "confirmed_appointments": Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED,
        ).count(),

        "completed_appointments": Appointment.objects.filter(
            status=Appointment.Status.COMPLETED,
        ).count(),
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context,
    )


# ==========================================
# ADMIN - MANAGE DOCTORS
# ==========================================

@login_required
def manage_doctors(request):

    if not request.user.is_staff:
        return redirect("home")

    doctors = (
        DoctorProfile.objects
        .select_related(
            "user",
            "department",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    search_query = request.GET.get(
        "search",
        "",
    ).strip()

    department_id = request.GET.get(
        "department",
        "",
    )

    status = request.GET.get(
        "status",
        "",
    )

    if search_query:
        doctors = doctors.filter(
            user__first_name__icontains=search_query
        ) | doctors.filter(
            user__last_name__icontains=search_query
        ) | doctors.filter(
            specialization__icontains=search_query
        ) | doctors.filter(
            doctor_id__icontains=search_query
        )

    if department_id:
        doctors = doctors.filter(
            department_id=department_id
        )

    if status:
        doctors = doctors.filter(
            status=status
        )

    departments = Department.objects.filter(
        is_active=True
    )

    context = {
        "doctors": doctors,
        "departments": departments,
        "total_doctors": doctors.count(),
        "search_query": search_query,
        "selected_department": department_id,
        "selected_status": status,
    }

    return render(
        request,
        "dashboard/manage_doctors.html",
        context,
    )


# ==========================================
# ADMIN - ADD DOCTOR
# ==========================================

@login_required
def add_doctor(request):

    if not request.user.is_staff:
        return redirect("home")

    departments = Department.objects.filter(
        is_active=True
    )

    if request.method == "POST":

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        password = request.POST.get(
            "password",
            "",
        )

        department_id = request.POST.get(
            "department"
        )

        specialization = request.POST.get(
            "specialization",
            "",
        ).strip()

        qualification = request.POST.get(
            "qualification",
            "",
        ).strip()

        experience_years = request.POST.get(
            "experience_years",
            0,
        )

        consultation_fee = request.POST.get(
            "consultation_fee",
            0,
        )

        license_number = request.POST.get(
            "license_number",
            "",
        ).strip()

        bio = request.POST.get(
            "bio",
            "",
        ).strip()


        if not all([
            first_name,
            email,
            password,
            department_id,
            specialization,
            qualification,
            license_number,
        ]):
            messages.error(
                request,
                "Please complete all required fields.",
            )

            return render(
                request,
                "dashboard/add_doctor.html",
                {
                    "departments": departments,
                },
            )


        if CustomUser.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "A user with this email already exists.",
            )

            return render(
                request,
                "dashboard/add_doctor.html",
                {
                    "departments": departments,
                },
            )


        if DoctorProfile.objects.filter(
            license_number=license_number
        ).exists():

            messages.error(
                request,
                "This medical license number already exists.",
            )

            return render(
                request,
                "dashboard/add_doctor.html",
                {
                    "departments": departments,
                },
            )


        department = get_object_or_404(
            Department,
            id=department_id,
            is_active=True,
        )


        user = CustomUser.objects.create_user(
            email=email,
            username=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=CustomUser.Role.DOCTOR,
        )


        DoctorProfile.objects.create(
            user=user,
            department=department,
            specialization=specialization,
            qualification=qualification,
            experience_years=experience_years or 0,
            consultation_fee=consultation_fee or 0,
            license_number=license_number,
            bio=bio,
            status=DoctorProfile.Status.AVAILABLE,
        )


        messages.success(
            request,
            "Doctor added successfully.",
        )

        return redirect(
            "dashboard:manage_doctors"
        )


    return render(
        request,
        "dashboard/add_doctor.html",
        {
            "departments": departments,
        },
    )


# ==========================================
# ADMIN - EDIT DOCTOR
# ==========================================

@login_required
def edit_doctor(request, doctor_id):

    if not request.user.is_staff:
        return redirect("home")

    doctor = get_object_or_404(
        DoctorProfile.objects.select_related(
            "user",
            "department",
        ),
        id=doctor_id,
    )

    departments = Department.objects.filter(
        is_active=True
    )

    if request.method == "POST":

        doctor.user.first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        doctor.user.last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        doctor.user.email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        doctor.user.username = doctor.user.email

        doctor.department = get_object_or_404(
            Department,
            id=request.POST.get("department"),
        )

        doctor.specialization = request.POST.get(
            "specialization",
            "",
        ).strip()

        doctor.qualification = request.POST.get(
            "qualification",
            "",
        ).strip()

        doctor.experience_years = request.POST.get(
            "experience_years",
            0,
        )

        doctor.consultation_fee = request.POST.get(
            "consultation_fee",
            0,
        )

        doctor.license_number = request.POST.get(
            "license_number",
            "",
        ).strip()

        doctor.bio = request.POST.get(
            "bio",
            "",
        ).strip()

        doctor.user.save()
        doctor.save()

        messages.success(
            request,
            "Doctor information updated successfully.",
        )

        return redirect(
            "dashboard:manage_doctors"
        )


    return render(
        request,
        "dashboard/edit_doctor.html",
        {
            "doctor": doctor,
            "departments": departments,
        },
    )


# ==========================================
# ADMIN - TOGGLE DOCTOR STATUS
# ==========================================

@login_required
def toggle_doctor_status(request, doctor_id):

    if not request.user.is_staff:
        return redirect("home")

    if request.method != "POST":
        return redirect(
            "dashboard:manage_doctors"
        )

    doctor = get_object_or_404(
        DoctorProfile,
        id=doctor_id,
    )

    if doctor.status == DoctorProfile.Status.INACTIVE:

        doctor.status = DoctorProfile.Status.AVAILABLE
        doctor.user.is_active = True

        message = "Doctor activated successfully."

    else:

        doctor.status = DoctorProfile.Status.INACTIVE
        doctor.user.is_active = False

        message = "Doctor deactivated successfully."


    doctor.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    doctor.user.save(
        update_fields=[
            "is_active",
        ]
    )

    messages.success(
        request,
        message,
    )

    return redirect(
        "dashboard:manage_doctors"
    )


# ==========================================
# ADMIN - DOCTOR DETAIL
# ==========================================

@login_required
def admin_doctor_detail(request, doctor_id):

    if not request.user.is_staff:
        return redirect("home")

    doctor = get_object_or_404(
        DoctorProfile.objects.select_related(
            "user",
            "department",
        ),
        id=doctor_id,
    )

    appointments = (
        Appointment.objects
        .filter(doctor=doctor)
        .select_related("patient")
        .order_by(
            "-appointment_date",
            "-appointment_time",
        )
    )

    context = {
        "doctor": doctor,
        "appointments": appointments,
        "appointment_count": appointments.count(),
    }

    return render(
        request,
        "dashboard/admin_doctor_detail.html",
        context,
    )

@login_required
def manage_patients(request):

    if not request.user.is_staff:
        return redirect("home")

    patients = (
        CustomUser.objects
        .filter(role=CustomUser.Role.PATIENT)
        .select_related("patient_profile")
        .order_by(
            "first_name",
            "last_name",
        )
    )

    search_query = request.GET.get(
        "search",
        "",
    ).strip()

    if search_query:
        from django.db.models import Q

        patients = patients.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    context = {
        "patients": patients,
        "total_patients": patients.count(),
        "search_query": search_query,
    }

    return render(
        request,
        "dashboard/manage_patients.html",
        context,
    )


@login_required
def admin_patient_detail(request, patient_id):

    if not request.user.is_staff:
        return redirect("home")

    patient = get_object_or_404(
        CustomUser.objects.select_related(
            "patient_profile",
        ),
        id=patient_id,
        role=CustomUser.Role.PATIENT,
    )

    appointments = (
        Appointment.objects
        .filter(patient=patient)
        .select_related(
            "doctor",
            "doctor__user",
            "doctor__department",
        )
        .order_by(
            "-appointment_date",
            "-appointment_time",
        )
    )

    context = {
        "patient": patient,
        "patient_profile": patient.patient_profile, # type: ignore
        "appointments": appointments,
        "appointment_count": appointments.count(),
    }

    return render(
        request,
        "dashboard/admin_patient_detail.html",
        context,
    )

@login_required
def manage_appointments(request):

    if not request.user.is_staff:
        return redirect("home")

    appointments = (
        Appointment.objects
        .select_related(
            "patient",
            "doctor",
            "doctor__user",
            "doctor__department",
        )
        .order_by(
            "-appointment_date",
            "-appointment_time",
        )
    )

    status = request.GET.get(
        "status",
        "",
    )

    selected_date = request.GET.get(
        "date",
        "",
    )

    if status:
        appointments = appointments.filter(
            status=status,
        )

    if selected_date:
        appointments = appointments.filter(
            appointment_date=selected_date,
        )

    context = {
        "appointments": appointments,
        "selected_status": status,
        "selected_date": selected_date,

        "total_count": Appointment.objects.count(),

        "pending_count": Appointment.objects.filter(
            status=Appointment.Status.PENDING,
        ).count(),

        "confirmed_count": Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED,
        ).count(),

        "completed_count": Appointment.objects.filter(
            status=Appointment.Status.COMPLETED,
        ).count(),
    }

    return render(
        request,
        "dashboard/manage_appointments.html",
        context,
    )

# ==========================================
# ADMIN - MANAGE DEPARTMENTS
# ==========================================

@login_required
def manage_departments(request):

    if not request.user.is_staff:
        return redirect("home")

    departments = (
        Department.objects
        .all()
        .order_by("name")
    )

    context = {
        "departments": departments,
        "total_departments": departments.count(),
        "active_departments": departments.filter(
            is_active=True,
        ).count(),
    }

    return render(
        request,
        "dashboard/manage_departments.html",
        context,
    )


# ==========================================
# ADMIN - ADD DEPARTMENT
# ==========================================

@login_required
def add_department(request):

    if not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        if not name:
            messages.error(
                request,
                "Department name is required.",
            )

            return redirect(
                "dashboard:manage_departments"
            )

        if Department.objects.filter(
            name__iexact=name,
        ).exists():

            messages.error(
                request,
                "This department already exists.",
            )

            return redirect(
                "dashboard:manage_departments"
            )

        Department.objects.create(
            name=name,
            description=description,
            is_active=True,
        )

        messages.success(
            request,
            "Department added successfully.",
        )

    return redirect(
        "dashboard:manage_departments"
    )


# ==========================================
# ADMIN - EDIT DEPARTMENT
# ==========================================

@login_required
def edit_department(request, department_id):

    if not request.user.is_staff:
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id,
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        if not name:
            messages.error(
                request,
                "Department name is required.",
            )

            return redirect(
                "dashboard:manage_departments"
            )

        duplicate_exists = (
            Department.objects
            .filter(name__iexact=name)
            .exclude(id=department.id) # type: ignore
            .exists()
        )

        if duplicate_exists:
            messages.error(
                request,
                "Another department with this name already exists.",
            )

            return redirect(
                "dashboard:manage_departments"
            )

        department.name = name
        department.description = description
        department.save()

        messages.success(
            request,
            "Department updated successfully.",
        )

    return redirect(
        "dashboard:manage_departments"
    )


# ==========================================
# ADMIN - TOGGLE DEPARTMENT
# ==========================================

@login_required
def toggle_department(request, department_id):

    if not request.user.is_staff:
        return redirect("home")

    if request.method != "POST":
        return redirect(
            "dashboard:manage_departments"
        )

    department = get_object_or_404(
        Department,
        id=department_id,
    )

    department.is_active = not department.is_active

    department.save(
        update_fields=["is_active"]
    )

    if department.is_active:
        messages.success(
            request,
            "Department activated successfully.",
        )
    else:
        messages.success(
            request,
            "Department deactivated successfully.",
        )

    return redirect(
        "dashboard:manage_departments"
    )

@login_required
def admin_reports(request):

    if not request.user.is_staff:
        return redirect("home")

    appointments = Appointment.objects.all()

    departments = (
        Department.objects
        .filter(is_active=True)
        .prefetch_related("doctors")
    )

    doctors = (
        DoctorProfile.objects
        .select_related("user", "department")
        .order_by("user__first_name")
    )

    context = {
        "total_appointments": appointments.count(),

        "pending_count": appointments.filter(
            status=Appointment.Status.PENDING
        ).count(),

        "confirmed_count": appointments.filter(
            status=Appointment.Status.CONFIRMED
        ).count(),

        "completed_count": appointments.filter(
            status=Appointment.Status.COMPLETED
        ).count(),

        "cancelled_count": appointments.filter(
            status=Appointment.Status.CANCELLED
        ).count(),

        "total_doctors": doctors.count(),

        "total_patients": CustomUser.objects.filter(
            role=CustomUser.Role.PATIENT
        ).count(),

        "departments": departments,
        "doctors": doctors,
    }

    return render(
        request,
        "dashboard/admin_reports.html",
        context,
    )

@login_required
def manage_beds(request):

    if not request.user.is_staff:
        return redirect("home")

    beds = (
        Bed.objects
        .select_related(
            "department",
            "patient",
        )
        .order_by(
            "department__name",
            "bed_number",
        )
    )
    paginator = Paginator(
        beds,
        10,
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    departments = Department.objects.filter(
        is_active=True
    )

    # PATIENTS WITHOUT AN ASSIGNED BED
    patients = (
        CustomUser.objects
        .filter(
            role=CustomUser.Role.PATIENT,
            assigned_beds__isnull=True,
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )

    context = {
        "beds": page_obj,
        "page_obj": page_obj,
        "departments": departments,
        "patients": patients,
        "bed_types": Bed.BedType.choices,

        "total_beds": beds.count(),

        "available_beds": beds.filter(
            status=Bed.Status.AVAILABLE
        ).count(),

        "occupied_beds": beds.filter(
            status=Bed.Status.OCCUPIED
        ).count(),

        "maintenance_beds": beds.filter(
            status=Bed.Status.MAINTENANCE
        ).count(),
    }

    return render(
        request,
        "dashboard/manage_beds.html",
        context,
    )

@login_required
def add_bed(request):

    if not request.user.is_staff:
        return redirect("home")

    if request.method != "POST":
        return redirect("dashboard:manage_beds")

    bed_number = request.POST.get(
        "bed_number",
        "",
    ).strip()

    department_id = request.POST.get(
        "department",
        "",
    )

    bed_type = request.POST.get(
        "bed_type",
        "",
    )

    if not all([
        bed_number,
        department_id,
        bed_type,
    ]):
        messages.error(
            request,
            "Please fill all required bed details.",
        )

        return redirect(
            "dashboard:manage_beds"
        )

    if Bed.objects.filter(
        bed_number__iexact=bed_number
    ).exists():

        messages.error(
            request,
            "This bed number already exists.",
        )

        return redirect(
            "dashboard:manage_beds"
        )

    department = get_object_or_404(
        Department,
        id=department_id,
        is_active=True,
    )

    Bed.objects.create(
        bed_number=bed_number,
        department=department,
        bed_type=bed_type,
        status=Bed.Status.AVAILABLE,
    )

    messages.success(
        request,
        "Bed added successfully.",
    )

    return redirect(
        "dashboard:manage_beds"
    )
@login_required
def manage_ambulances(request):

    if not request.user.is_staff:
        return redirect("home")

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

        "maintenance_ambulances": ambulances.filter(
            status=Ambulance.Status.MAINTENANCE
        ).count(),

        "status_choices": Ambulance.Status.choices,
    }

    return render(
        request,
        "dashboard/manage_ambulances.html",
        context,
    )

@login_required
def update_ambulance_status(request, ambulance_id):

    if not request.user.is_staff:
        return redirect("home")

    if request.method != "POST":
        return redirect(
            "dashboard:manage_ambulances"
        )

    ambulance = get_object_or_404(
        Ambulance,
        id=ambulance_id,
        is_active=True,
    )

    new_status = request.POST.get(
        "status",
        "",
    )

    valid_statuses = [
        value
        for value, label
        in Ambulance.Status.choices
    ]

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid ambulance status.",
        )

        return redirect(
            "dashboard:manage_ambulances"
        )

    ambulance.status = new_status

    ambulance.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        (
            f"{ambulance.ambulance_number} "
            f"status updated successfully."
        ),
    )

    return redirect(
        "dashboard:manage_ambulances"
    )


@login_required
def receptionist_dashboard(request):

    if request.user.role != "RECEPTIONIST":
        return redirect("home")

    return redirect("reception:dashboard")

@login_required
def lab_technician_dashboard(request):

    if request.user.role != "LAB_TECHNICIAN":
        return redirect("home")

    paid_tests = (
        TestOrder.objects
        .filter(
            bill_item__bill__payment_status=(
                TestBill.PaymentStatus.PAID
            ),
        )
        .select_related(
            "appointment",
            "appointment__patient",
            "appointment__doctor",
            "appointment__doctor__user",
        )
        .order_by("-ordered_at")
    )

    pending_tests = paid_tests.filter(
        status__in=[
            TestOrder.Status.ORDERED,
            TestOrder.Status.SAMPLE_COLLECTED,
        ],
    )

    tested_tests = (
        paid_tests
        .filter(
            status__in=[
                TestOrder.Status.REPORT_READY,
                TestOrder.Status.REVIEWED,
            ],
            lab_result__isnull=False,
        )
        .select_related(
            "lab_result",
            "lab_result__tested_by",
        )
        .order_by(
            "-lab_result__completed_at"
        )
    )

    context = {
        "pending_tests": pending_tests,
        "tested_tests": tested_tests,

        "pending_test_count": pending_tests.count(),
        "tested_test_count": tested_tests.count(),
    }

    return render(
        request,
        "dashboard/lab_technician_dashboard.html",
        context,
    )

@login_required
def lab_test_detail(request, test_id):

    if request.user.role != "LAB_TECHNICIAN":
        return redirect("home")

    test = get_object_or_404(
        TestOrder.objects.select_related(
            "appointment",
            "appointment__patient",
            "appointment__doctor",
            "appointment__doctor__user",
            "appointment__doctor__department",
        ),
        id=test_id,
        bill_item__bill__payment_status=(
            TestBill.PaymentStatus.PAID
        ),
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

        if not result_status or not findings:
            messages.error(
                request,
                "Result status and findings are required.",
            )

            return render(
                request,
                "dashboard/lab_test_detail.html",
                {
                    "test": test,
                },
            )

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
                "dashboard:lab_test_detail",
                test_id=test.id, # type: ignore
            )

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

        return redirect(
            "dashboard:lab_technician"
        )

    return render(
        request,
        "dashboard/lab_test_detail.html",
        {
            "test": test,
        },
    )

@login_required
def lab_report_pdf(request, test_id):

    test = get_object_or_404(
        TestOrder.objects.select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__patient_profile",
            "appointment__doctor",
            "appointment__doctor__user",
            "appointment__doctor__department",
            "lab_result",
            "lab_result__tested_by",
        ),
        id=test_id,
        status__in=[
            TestOrder.Status.REPORT_READY,
            TestOrder.Status.REVIEWED,
        ],
    )

    # Only patient, ordering doctor, lab technician, or admin
    is_patient = (
        request.user == test.appointment.patient
    )

    is_doctor = (
        request.user.role == "DOCTOR"
        and hasattr(request.user, "doctor_profile")
        and request.user.doctor_profile == test.appointment.doctor
    )

    is_lab_staff = (
        request.user.role == "LAB_TECHNICIAN"
    )

    if not (
        is_patient
        or is_doctor
        or is_lab_staff
        or request.user.is_staff
        or request.user.is_superuser
    ):
        return HttpResponse(
            "You are not allowed to access this report.",
            status=403,
        )

    result = test.lab_result # type: ignore
    patient_user = test.appointment.patient
    patient = patient_user.patient_profile
    doctor = test.appointment.doctor

    buffer = BytesIO()

    filename = (
        f"{test.test_id or 'LAB-' + str(test.id)}" # type: ignore
        f"-{test.test_name.replace(' ', '-')}-Report.pdf"
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="{filename}"'
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    normal = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#24364F"),
    )

    small = ParagraphStyle(
        "ReportSmall",
        parent=normal,
        fontSize=7.5,
        leading=10,
    )

    hospital_name = ParagraphStyle(
        "HospitalName",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=25,
        textColor=colors.HexColor("#0F2B50"),
    )

    doctor_style = ParagraphStyle(
        "DoctorDetails",
        parent=normal,
        alignment=TA_RIGHT,
    )

    title_style = ParagraphStyle(
        "TestTitle",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        alignment=TA_CENTER,
        spaceAfter=5,
    )

    story = []

    # HEADER

    left_header = [
        Paragraph("MediCore", hospital_name),
        Paragraph(
            "<b>Smart Hospital & Diagnostic Centre</b>",
            normal,
        ),
        Paragraph(
            "Hazaribagh, Jharkhand",
            normal,
        ),
    ]

    doctor_name = (
        doctor.user.get_full_name()
        or doctor.user.email
    )

    right_header = [
        Paragraph(
            f"<b>Dr. {doctor_name}</b>",
            doctor_style,
        ),
        Paragraph(
            doctor.specialization,
            doctor_style,
        ),
        Paragraph(
            f"Department of {doctor.department.name}",
            doctor_style,
        ),
        Paragraph(
            "Consultant Doctor",
            doctor_style,
        ),
    ]

    header_table = Table(
        [[left_header, right_header]],
        colWidths=[
            92 * mm,
            86 * mm,
        ],
    )

    header_table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),
        ])
    )

    story.append(header_table)

    story.append(
        Table(
            [[""]],
            colWidths=[178 * mm],
            rowHeights=[1],
            style=[
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#173A63"),
                ),
            ],
        )
    )

    story.append(Spacer(1, 7 * mm))

    # PATIENT DETAILS

    patient_name = (
        patient_user.get_full_name()
        or patient_user.email
    )

    patient_id = getattr(
        patient,
        "patient_id",
        "—",
    )

    gender = getattr(
        patient,
        "gender",
        "—",
    )

    age = getattr(
        patient,
        "age",
        None,
    )

    age_text = (
        f"{age} Years"
        if age
        else "—"
    )

    report_date = timezone.localtime(
        result.completed_at
    ).strftime("%d/%m/%Y")

    test_identifier = (
        test.test_id
        if getattr(test, "test_id", None)
        else f"LAB-{test.id}" # type: ignore
    )

    patient_data = [
        [
            Paragraph("<b>NAME</b>", small),
            Paragraph(patient_name, normal),
            Paragraph("<b>AGE</b>", small),
            Paragraph(age_text, normal),
            Paragraph("<b>SEX</b>", small),
            Paragraph(str(gender), normal),
        ],
        [
            Paragraph("<b>PATIENT ID</b>", small),
            Paragraph(patient_id, normal),
            Paragraph("<b>DATE</b>", small),
            Paragraph(report_date, normal),
            Paragraph("<b>TEST ID</b>", small),
            Paragraph(test_identifier, normal), # type: ignore
        ],
        [
            Paragraph("<b>REF. BY</b>", small),
            Paragraph(
                f"Dr. {doctor_name}",
                normal,
            ),
            Paragraph("<b>PHONE</b>", small),
            Paragraph(
                patient_user.phone or "—",
                normal,
            ),
            "",
            "",
        ],
    ]

    patient_table = Table(
        patient_data,
        colWidths=[
            20 * mm,
            46 * mm,
            13 * mm,
            26 * mm,
            14 * mm,
            49 * mm,
        ],
    )

    patient_table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4,
            ),
        ])
    )

    story.append(patient_table)
    story.append(Spacer(1, 5 * mm))

    # TEST TITLE

    story.append(
        Paragraph(
            test.test_name.upper(),
            title_style,
        )
    )

    story.append(Spacer(1, 4 * mm))

    # RESULT TABLE

    table_data = [
        [
            "TESTS",
            "RESULTS",
            "UNIT",
            "REFERENCE RANGE",
        ]
    ]

    table_data.append([
    test.test_name,
    result.result_value or result.get_result_status_display(),
    result.unit or "—",
    result.reference_range or "—",
])
    result_table = Table(
        table_data,
        colWidths=[
            67 * mm,
            34 * mm,
            28 * mm,
            49 * mm,
        ],
        repeatRows=1,
    )

    result_table.setStyle(
        TableStyle([
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5,
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.HexColor("#102B4E"),
            ),
            (
                "LINEBELOW",
                (0, 0),
                (-1, 0),
                0.8,
                colors.HexColor("#8A98AA"),
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F7F9FC"),
                ],
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
        ])
    )

    story.append(result_table)
    story.append(Spacer(1, 7 * mm))

    # FINDINGS

    if result.findings:

        story.append(
            Paragraph(
                "<b>FINDINGS</b>",
                normal,
            )
        )

        story.append(Spacer(1, 2 * mm))

        story.append(
            Paragraph(
                result.findings,
                normal,
            )
        )

        story.append(Spacer(1, 5 * mm))

    if result.description:

        story.append(
            Paragraph(
                "<b>IMPRESSION / INTERPRETATION</b>",
                normal,
            )
        )

        story.append(Spacer(1, 2 * mm))

        story.append(
            Paragraph(
                result.description,
                normal,
            )
        )

    story.append(Spacer(1, 18 * mm))

    # SIGNATURE

    technician_name = (
        result.tested_by.get_full_name()
        if result.tested_by
        else "Lab Technician"
    )

    signature_table = Table(
        [
            [
                "",
                Paragraph(
                    (
                        "<b>Digitally Verified</b><br/>"
                        f"{technician_name}<br/>"
                        "Lab Technician<br/>"
                        "MediCore Laboratory"
                    ),
                    doctor_style,
                ),
            ]
        ],
        colWidths=[
            105 * mm,
            73 * mm,
        ],
    )

    story.append(signature_table)

    story.append(Spacer(1, 12 * mm))

    # FOOTER NOTE

    story.append(
        Table(
            [[""]],
            colWidths=[178 * mm],
            rowHeights=[1],
            style=[
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#173A63"),
                ),
            ],
        )
    )

    story.append(Spacer(1, 2 * mm))

    story.append(
        Paragraph(
            (
                "This is a digitally generated laboratory report. "
                "Results should be interpreted together with clinical "
                "findings and consultation with the treating doctor."
            ),
            small,
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)

    return response

@login_required
@require_POST
def send_lab_report_whatsapp(request, test_id):

    if request.user.role != CustomUser.Role.LAB_TECHNICIAN:
        return HttpResponse(
            "Access denied.",
            status=403,
        )

    test = get_object_or_404(
        TestOrder.objects.select_related(
            "appointment",
            "appointment__patient",
            "lab_result",
        ),
        id=test_id,
        status__in=[
            TestOrder.Status.REPORT_READY,
            TestOrder.Status.REVIEWED,
        ],
    )

    patient = test.appointment.patient

    if not patient.phone:
        messages.error(
            request,
            "Patient phone number is not available.",
        )

        return redirect(
            "dashboard:lab_test_detail",
            test_id=test.id, # type: ignore
        )

    messages.info(
        request,
        "WhatsApp API is not connected yet.",
    )

    return redirect(
        "dashboard:lab_test_detail",
        test_id=test.id, # type: ignore
    )


@login_required
def doctor_lab_report(request, appointment_id):

    if request.user.role != "DOCTOR":
        return redirect("home")

    doctor = request.user.doctor_profile

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "patient",
            "patient__patient_profile",
            "doctor",
            "doctor__user",
        ),
        id=appointment_id,
        doctor=doctor,
    )

    reports = (
        TestOrder.objects
        .filter(
            appointment=appointment,
            status__in=[
                TestOrder.Status.REPORT_READY,
                TestOrder.Status.REVIEWED,
            ],
            lab_result__isnull=False,
        )
        .select_related(
            "lab_result",
            "lab_result__tested_by",
        )
        .order_by("-updated_at")
    )

    context = {
        "appointment": appointment,
        "patient": appointment.patient,
        "reports": reports,
    }

    return render(
        request,
        "dashboard/doctor_lab_report.html",
        context,
    )