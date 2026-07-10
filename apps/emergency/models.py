

from django.conf import settings
from django.db import models


class EmergencyRequest(models.Model):

    class EmergencyType(models.TextChoices):
        ACCIDENT = "ACCIDENT", "Accident"
        CARDIAC = "CARDIAC", "Cardiac Emergency"
        BREATHING = "BREATHING", "Breathing Problem"
        BLEEDING = "BLEEDING", "Severe Bleeding"
        NEUROLOGICAL = "NEUROLOGICAL", "Neurological Emergency"
        PREGNANCY = "PREGNANCY", "Pregnancy Emergency"
        OTHER = "OTHER", "Other Emergency"

    class Priority(models.TextChoices):
        CRITICAL = "CRITICAL", "Critical"
        HIGH = "HIGH", "High"
        MODERATE = "MODERATE", "Moderate"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        AMBULANCE_DISPATCHED = (
            "AMBULANCE_DISPATCHED",
            "Ambulance Dispatched",
        )
        ARRIVED = "ARRIVED", "Arrived"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emergency_requests",
    )

    patient_name = models.CharField(
        max_length=150,
    )

    phone = models.CharField(
        max_length=15,
    )

    emergency_type = models.CharField(
        max_length=30,
        choices=EmergencyType.choices,
    )

    location = models.TextField()

    description = models.TextField(
        blank=True,
    )

    ambulance_required = models.BooleanField(
        default=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.HIGH,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.patient_name} - "
            f"{self.get_emergency_type_display()}"
        )
    
  

class Ambulance(models.Model):

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        ON_DUTY = "ON_DUTY", "On Duty"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    ambulance_number = models.CharField(
        max_length=20,
        unique=True,
    )

    driver_name = models.CharField(
        max_length=150,
    )

    driver_phone = models.CharField(
        max_length=15,
    )

    vehicle_number = models.CharField(
        max_length=20,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.ambulance_number} - "
            f"{self.get_status_display()}"
        )