from django.contrib import admin

from .models import (
    Department,
    HospitalBranch,
    DoctorAvailability,
    DoctorProfile,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    search_fields = ("name",)

    list_filter = ("is_active",)



@admin.register(HospitalBranch)
class HospitalBranchAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "city",
        "phone",
        "is_active",
    )

    search_fields = (
        "name",
        "city",
    )

    list_filter = (
        "city",
        "is_active",
    )



@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "doctor_id",
        "user",
        "department",
        "branch",
        "gender",
        "specialization",
        "status",
    )

    search_fields = (
        "doctor_id",
        "user__email",
        "user__first_name",
        "user__last_name",
        "specialization",
        "branch__city",
        "branch__name",
    )

    list_filter = (
        "department",
        "branch",
        "gender",
        "status",
    )


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "day_of_week",
        "start_time",
        "end_time",
        "slot_duration",
        "is_active",
    )

    list_filter = (
        "day_of_week",
        "is_active",
    )

    search_fields = (
        "doctor__user__first_name",
        "doctor__user__last_name",
        "doctor__user__email",
    )