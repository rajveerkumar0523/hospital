from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HospitalBranch(models.Model):

    name = models.CharField(
        max_length=100,
    )

    city = models.CharField(
        max_length=100,
    )

    address = models.TextField()

    phone = models.CharField(
        max_length=15,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.name} ({self.city})"

class DoctorProfile(models.Model):

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        INACTIVE = "INACTIVE", "Inactive"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="doctors",
    )

    branch = models.ForeignKey(
        HospitalBranch,
        on_delete=models.PROTECT,
        related_name="doctors",
        null=True,
        blank=True,
    )

    doctor_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    specialization = models.CharField(
        max_length=150,
    )

    qualification = models.CharField(
        max_length=200,
    )

    experience_years = models.PositiveIntegerField(
        default=0,
    )

    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    license_number = models.CharField(
        max_length=100,
        unique=True,
    )

    bio = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.MALE,
    )


    def save(self, *args, **kwargs):
        if not self.doctor_id:
            last_doctor = (
                DoctorProfile.objects
                .order_by("-id")
                .first()
            )

            next_number = (
                last_doctor.id + 1 # type: ignore
                if last_doctor
                else 1
            )

            self.doctor_id = f"DOC-{next_number:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Dr. {self.user.get_full_name()} "
            f"({self.specialization})"
        )


class DoctorAvailability(models.Model):

    class Day(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="availabilities",
    )

    day_of_week = models.PositiveSmallIntegerField(
        choices=Day.choices,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    slot_duration = models.PositiveIntegerField(
        default=30,
        help_text="Duration in minutes",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "doctor",
            "day_of_week",
            "start_time",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "doctor",
                    "day_of_week",
                    "start_time",
                ],
                name="unique_doctor_schedule",
            )
        ]

    def __str__(self):
        return (
            f"{self.doctor} - "
            f"{self.get_day_of_week_display()} " # type: ignore
            f"{self.start_time} to {self.end_time}"
        )