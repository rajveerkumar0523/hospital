from django.db import migrations


def create_branches(apps, schema_editor):
    HospitalBranch = apps.get_model("doctors", "HospitalBranch")

    branches = [
        {
            "name": "MediCore Ranchi",
            "city": "Ranchi",
            "address": "Main Road, Ranchi",
            "phone": "9876543210",
        },
        {
            "name": "MediCore Hazaribagh",
            "city": "Hazaribagh",
            "address": "Hazaribagh",
            "phone": "9876543211",
        },
        {
            "name": "MediCore Dhanbad",
            "city": "Dhanbad",
            "address": "Bank More, Dhanbad",
            "phone": "9876543212",
        },
        {
            "name": "MediCore Jamshedpur",
            "city": "Jamshedpur",
            "address": "Sakchi, Jamshedpur",
            "phone": "9876543213",
        },
    ]

    for branch in branches:
        HospitalBranch.objects.get_or_create(
            city=branch["city"],
            defaults=branch,
        )


def remove_branches(apps, schema_editor):
    HospitalBranch = apps.get_model("doctors", "HospitalBranch")

    HospitalBranch.objects.filter(
        city__in=[
            "Ranchi",
            "Hazaribagh",
            "Dhanbad",
            "Jamshedpur",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("doctors", "0004_doctorprofile_gender"),
    ]

    operations = [
        migrations.RunPython(
            create_branches,
            remove_branches,
        ),
    ]