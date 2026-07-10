from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path(
        "patient/",
        views.patient_dashboard,
        name="patient",
    ),

    path(
    "doctor/",
    views.doctor_dashboard,
    name="doctor",
),
path(
    "admin/",
    views.admin_dashboard,
    name="admin",
),
path(
    "admin/doctors/",
    views.manage_doctors,
    name="manage_doctors",
),
path(
    "admin/doctors/",
    views.manage_doctors,
    name="manage_doctors",
),

path(
    "admin/doctors/add/",
    views.add_doctor,
    name="add_doctor",
),

path(
    "admin/doctors/<int:doctor_id>/",
    views.admin_doctor_detail,
    name="admin_doctor_detail",
),

path(
    "admin/doctors/<int:doctor_id>/edit/",
    views.edit_doctor,
    name="edit_doctor",
),

path(
    "admin/doctors/<int:doctor_id>/toggle-status/",
    views.toggle_doctor_status,
    name="toggle_doctor_status",
),
path(
    "admin/patients/",
    views.manage_patients,
    name="manage_patients",
),

path(
    "admin/patients/<int:patient_id>/",
    views.admin_patient_detail,
    name="admin_patient_detail",
),
path(
    "admin/appointments/",
    views.manage_appointments,
    name="manage_appointments",
),
path(
    "admin/departments/",
    views.manage_departments,
    name="manage_departments",
),

path(
    "admin/departments/add/",
    views.add_department,
    name="add_department",
),

path(
    "admin/departments/<int:department_id>/edit/",
    views.edit_department,
    name="edit_department",
),

path(
    "admin/departments/<int:department_id>/toggle/",
    views.toggle_department,
    name="toggle_department",
),
path(
    "admin/reports/",
    views.admin_reports,
    name="admin_reports",
),
path(
    "admin/beds/",
    views.manage_beds,
    name="manage_beds",
),

path(
    "admin/beds/add/",
    views.add_bed,
    name="add_bed",
),
path(
    "ambulances/",
    views.manage_ambulances,
    name="manage_ambulances",
),
path(
    "ambulances/<int:ambulance_id>/status/",
    views.update_ambulance_status,
    name="update_ambulance_status",
),
path(
    "receptionist/",
    views.receptionist_dashboard,
    name="receptionist",
),
path(
    "lab-technician/",
    views.lab_technician_dashboard,
    name="lab_technician",
),
path(
    "lab-technician/test/<int:test_id>/",
    views.lab_test_detail,
    name="lab_test_detail",
),
path(
    "lab-technician/test/<int:test_id>/report/pdf/",
    views.lab_report_pdf,
    name="lab_report_pdf",
),
path(
    "lab-technician/test/<int:test_id>/send-whatsapp/",
    views.send_lab_report_whatsapp,
    name="send_lab_report_whatsapp",
),
path(
    "doctor/appointment/<int:appointment_id>/lab-report/",
    views.doctor_lab_report,
    name="doctor_lab_report",
),
]
