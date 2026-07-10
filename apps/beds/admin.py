from django.contrib import admin

from .models import Bed


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):

    list_display = (
        "bed_number",
        "department",
        "bed_type",
        "status",
        "patient",
    )

    list_filter = (
        "status",
        "bed_type",
        "department",
    )

    search_fields = (
        "bed_number",
        "patient__first_name",
        "patient__last_name",
        "patient__email",
    )