from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,render, redirect

from apps.accounts.models import CustomUser

from .forms import PatientProfileForm
from .models import PatientProfile
from .services import generate_patient_id


@login_required
def complete_profile(request):

    if request.user.role != CustomUser.Role.PATIENT:
        return redirect("home")

    if PatientProfile.objects.filter(
        user=request.user
    ).exists():
        return redirect("patients:profile")

    if request.method == "POST":

        form = PatientProfileForm(request.POST)

        if form.is_valid():

            profile = form.save(commit=False)

            profile.user = request.user

            profile.patient_id = generate_patient_id()

            profile.save()

            return redirect("patients:profile")

    else:
        form = PatientProfileForm()

    return render(
        request,
        "patients/complete_profile.html",
        {
            "form": form,
        },
    )


@login_required
def profile(request):

    patient_profile = PatientProfile.objects.get(
        user=request.user
    )

    return render(
        request,
        "patients/profile.html",
        {
            "patient": patient_profile,
        },
    )

@login_required
def edit_profile(request):

    if request.user.role != CustomUser.Role.PATIENT:
        return redirect("home")

    patient = get_object_or_404(
        PatientProfile,
        user=request.user,
    )

    if request.method == "POST":
        form = PatientProfileForm(
            request.POST,
            instance=patient,
        )

        if form.is_valid():
            form.save()

            return redirect("patients:profile")

    else:
        form = PatientProfileForm(
            instance=patient,
        )

    return render(
        request,
        "patients/edit_profile.html",
        {
            "form": form,
            "patient": patient,
        },
    )