from django.conf import settings
from django.db import models

from apps.doctors.models import Department


class Bed(models.Model):

    class BedType(models.TextChoices):
        GENERAL = "GENERAL", "General"
        ICU = "ICU", "ICU"
        PRIVATE = "PRIVATE", "Private"
        EMERGENCY = "EMERGENCY", "Emergency"

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        OCCUPIED = "OCCUPIED", "Occupied"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    bed_number = models.CharField(
        max_length=20,
        unique=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="beds",
    )

    bed_type = models.CharField(
        max_length=20,
        choices=BedType.choices,
        default=BedType.GENERAL,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_beds",
        limit_choices_to={"role": "PATIENT"},
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "department__name",
            "bed_number",
        ]

    def __str__(self):
        return f"{self.bed_number} - {self.get_bed_type_display()}" # type: ignore