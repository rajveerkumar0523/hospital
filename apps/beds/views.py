from django.shortcuts import render

from apps.doctors.models import Department

from .models import Bed


def bed_list(request):

    beds = (
        Bed.objects
        .select_related(
            "department",
            "patient",
        )
        .order_by(
            "department__name",
            "bed_number",
        )
    )

    department_id = request.GET.get(
        "department",
        "",
    )

    bed_type = request.GET.get(
        "type",
        "",
    )

    status = request.GET.get(
        "status",
        "",
    )

    if department_id:
        beds = beds.filter(
            department_id=department_id
        )

    if bed_type:
        beds = beds.filter(
            bed_type=bed_type
        )

    if status:
        beds = beds.filter(
            status=status
        )

    departments = (
        Department.objects
        .filter(
            is_active=True,
            beds__isnull=False,
        )
        .distinct()
        .order_by("name")
    )

    context = {
        "beds": beds,
        "departments": departments,
        "bed_types": Bed.BedType.choices,

        "total_beds": Bed.objects.count(),

        "available_beds": Bed.objects.filter(
            status=Bed.Status.AVAILABLE
        ).count(),

        "occupied_beds": Bed.objects.filter(
            status=Bed.Status.OCCUPIED
        ).count(),

        "maintenance_beds": Bed.objects.filter(
            status=Bed.Status.MAINTENANCE
        ).count(),

        "selected_department": department_id,
        "selected_type": bed_type,
        "selected_status": status,
    }

    return render(
        request,
        "beds/bed_list.html",
        context,
    )