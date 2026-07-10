from django.utils import timezone

from .models import PatientProfile


def generate_patient_id():

    year = timezone.now().year

    last_patient = (
        PatientProfile.objects
        .filter(patient_id__startswith=f"PAT-{year}")
        .order_by("-id")
        .first()
    )

    if last_patient:
        last_number = int(
            last_patient.patient_id.split("-")[-1]
        )

        next_number = last_number + 1

    else:
        next_number = 1

    return f"PAT-{year}-{next_number:06d}"