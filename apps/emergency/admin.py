from django.contrib import admin

from .models import Ambulance, EmergencyRequest


@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = (
        "ambulance_number",
        "vehicle_number",
        "driver_name",
        "driver_phone",
        "status",
        "is_active",
    )

    list_filter = (
        "status",
        "is_active",
    )

    search_fields = (
        "ambulance_number",
        "vehicle_number",
        "driver_name",
    )


@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = (
        "patient_name",
        "phone",
        "emergency_type",
        "priority",
        "status",
        "created_at",
    )

    list_filter = (
        "emergency_type",
        "priority",
        "status",
    )