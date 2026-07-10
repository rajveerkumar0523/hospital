from django.conf import settings
from django.db import models



class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"

        AWAITING_TESTS = (
            "AWAITING_TESTS",
            "Awaiting Tests",
    )

        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
        limit_choices_to={"role": "PATIENT"},
    )

    doctor = models.ForeignKey(
        "doctors.DoctorProfile",
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    reason = models.TextField(
        max_length=500,
    )

    status = models.CharField(
        max_length=20,
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
        ordering = [
            "-appointment_date",
            "-appointment_time",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "doctor",
                    "appointment_date",
                    "appointment_time",
                ],
                condition=models.Q(
                    status__in=[
                        "PENDING",
                        "CONFIRMED",
                    ]
                ),
                name="unique_active_doctor_slot",
            )
        ]

    def __str__(self):
        return (
            f"{self.patient.get_full_name()} - "
            f"{self.doctor} - "
            f"{self.appointment_date}"
        )


class Prescription(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="prescription",
    )

    diagnosis = models.TextField()

    medicines = models.TextField(
        help_text="Enter medicines with dosage and duration.",
    )

    instructions = models.TextField(
        blank=True,
    )

    follow_up_date = models.DateField(
        null=True,
        blank=True,
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
            f"Prescription - "
            f"{self.appointment.patient.get_full_name()} - "
            f"{self.appointment.appointment_date}"
        )


class TestOrder(models.Model):

    class TestType(models.TextChoices):
        BLOOD = "BLOOD", "Blood Test"
        URINE = "URINE", "Urine Test"
        XRAY = "XRAY", "X-Ray"
        ULTRASOUND = "ULTRASOUND", "Ultrasound"
        ECG = "ECG", "ECG"
        CT_SCAN = "CT_SCAN", "CT Scan"
        MRI = "MRI", "MRI"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        ORDERED = "ORDERED", "Ordered"

        SAMPLE_COLLECTED = (
            "SAMPLE_COLLECTED",
            "Sample Collected",
        )

        REPORT_READY = (
            "REPORT_READY",
            "Report Ready",
        )

        REVIEWED = "REVIEWED", "Reviewed"

    test_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        null=True,
        blank=True,
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="test_orders",
    )

    test_type = models.CharField(
        max_length=30,
        choices=TestType.choices,
    )

    test_name = models.CharField(
        max_length=150,
    )

    fee = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0, # type: ignore
    )

    instructions = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ORDERED,
    )

    ordered_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new and not self.test_id:

            self.test_id = (
                f"LAB-"
                f"{self.ordered_at:%Y%m%d}-"
                f"{self.pk:06d}"
            )

            super().save(
                update_fields=["test_id"]
            )
    class Meta:
        ordering = ["-ordered_at"]

    def __str__(self):
        return (
            f"{self.test_name} - "
            f"{self.appointment.patient.get_full_name()}"
        )
    
class TestBill(models.Model):

    class PaymentStatus(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PAID = "PAID", "Paid"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        UPI = "UPI", "UPI"
        ONLINE = "ONLINE", "Online"

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="test_bill",
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0, # type: ignore
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
    )

    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collected_test_payments",
        limit_choices_to={
            "role": "RECEPTIONIST",
        },
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"Test Bill #{self.id} - " # type: ignore
            f"{self.appointment.patient.get_full_name()}"
        )
    
class TestBillItem(models.Model):

    bill = models.ForeignKey(
        TestBill,
        on_delete=models.CASCADE,
        related_name="items",
    )

    test_order = models.OneToOneField(
        TestOrder,
        on_delete=models.CASCADE,
        related_name="bill_item",
    )

    test_name = models.CharField(
        max_length=150,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return (
            f"{self.test_name} - ₹{self.amount}"
        )
    
class LabResult(models.Model):

    class ResultStatus(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        ABNORMAL = "ABNORMAL", "Abnormal"
        POSITIVE = "POSITIVE", "Positive"
        NEGATIVE = "NEGATIVE", "Negative"
        INCONCLUSIVE = "INCONCLUSIVE", "Inconclusive"

    test_order = models.OneToOneField(
        TestOrder,
        on_delete=models.CASCADE,
        related_name="lab_result",
    )

    result_status = models.CharField(
        max_length=20,
        choices=ResultStatus.choices,
    )

    result_value = models.CharField(
        max_length=100,
        blank=True,
    )

    unit = models.CharField(
        max_length=50,
        blank=True,
    )

    reference_range = models.CharField(
        max_length=150,
        blank=True,
    )

    findings = models.TextField()

    description = models.TextField(
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    tested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="completed_lab_tests",
        limit_choices_to={
            "role": "LAB_TECHNICIAN",
        },
    )

    completed_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )
    whatsapp_sent = models.BooleanField(
    default=False,
)

    whatsapp_sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.test_order.test_id} - "
            f"{self.test_order.test_name}"
        )