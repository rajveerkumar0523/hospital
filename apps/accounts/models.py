from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
        NURSE = "NURSE", "Nurse"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        LAB_TECHNICIAN = "LAB_TECHNICIAN", "Lab Technician"
        EMERGENCY_STAFF = "EMERGENCY_STAFF", "Emergency Staff"
        AMBULANCE_DRIVER = "AMBULANCE_DRIVER", "Ambulance Driver"

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.PATIENT,
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} - {self.role}"
  
    