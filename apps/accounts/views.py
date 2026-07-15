from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import PatientSignupForm
from .models import CustomUser


from django.conf import settings

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = PatientSignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = CustomUser.Role.PATIENT
            user.username = user.email
            user.save()

            messages.success(
                request,
                "Account created successfully. Please login.",
            )

            return redirect("accounts:login")

    else:
        form = PatientSignupForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )


def login_view(request):

    # ALREADY LOGGED-IN USER
    if request.user.is_authenticated:

        current_user = CustomUser.objects.get(
            pk=request.user.pk
        )

        if current_user.is_staff or current_user.is_superuser:
            return redirect("dashboard:admin")

        if current_user.role == CustomUser.Role.DOCTOR:
            return redirect("dashboard:doctor")

        if current_user.role == CustomUser.Role.PATIENT:
            return redirect("dashboard:patient")

        return redirect("home")


    # LOGIN FORM SUBMIT
    if request.method == "POST":

        email = request.POST.get(
            "email",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )


        #check username and password
        # user = authenticate(
        #     request,
        #     email=email,
        #     password=password,
        # )

        # check username only
        if settings.DEBUG:
            user = (
                CustomUser.objects
                .filter(
                    email__iexact=email,
                    is_active=True,
                )
                .first()
            )
        else:
            user = authenticate(
                request,
                email=email,
                password=password,
            )


        if user is not None:

            # DOCTOR — USE STAFF PORTAL
            if user.role == CustomUser.Role.DOCTOR: # type: ignore

                messages.error(
                    request,
                    "Doctor accounts must sign in through the Staff Portal.",
                )

                return redirect(
                    "accounts:staff_portal"
                )


            # ADMIN — BLOCK FROM PATIENT LOGIN
            if user.is_staff or user.is_superuser:

                messages.error(
                    request,
                    "Please use the authorized internal portal.",
                )

                return redirect(
                    "accounts:staff_portal"
                )


            # PATIENT
            if user.role == CustomUser.Role.PATIENT:

                login(request, user)

                if not hasattr(
                    user,
                    "patient_profile",
                ):
                    return redirect(
                        "patients:complete_profile"
                    )

                return redirect(
                    "dashboard:patient"
                )


            messages.error(
                request,
                "This account cannot use Patient Login.",
            )


        else:
            messages.error(
                request,
                "Invalid email or password.",
            )


    return render(
        request,
        "accounts/login.html",
    )


def logout_view(request):
    logout(request)

    return redirect("home")

def staff_portal_view(request):

    # ALREADY LOGGED-IN USER
    if request.user.is_authenticated:

        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard:admin")

        if request.user.role == CustomUser.Role.DOCTOR:
            return redirect("dashboard:doctor")

        logout(request)

        messages.error(
            request,
            "This portal is only for authorized hospital staff.",
        )

        return redirect("accounts:staff_portal")


    # STAFF LOGIN FORM SUBMIT
    if request.method == "POST":

        email = request.POST.get(
            "email",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        # user = authenticate(
        #     request,
        #     email=email,
        #     password=password,
        # )

         
        if settings.DEBUG:
            user = (
                CustomUser.objects
                .filter(
                    email__iexact=email,
                    is_active=True,
                )
                .first()
            )
        else:
            user = authenticate(
                request,
                email=email,
                password=password,
            )

        if user is None:
            messages.error(
                request,
                "Invalid email or password.",
            )

            return render(
                request,
                "accounts/staff_portal.html",
            )


        # ADMIN
        if user.is_staff or user.is_superuser:
            login(request, user)

            return redirect(
                "dashboard:admin"
            )


        # RECEPTIONIST
        if user.role == CustomUser.Role.RECEPTIONIST:
            login(request, user)

            return redirect(
                "reception:dashboard"
            )

        # LAB TECHNICIAN
        if user.role == CustomUser.Role.LAB_TECHNICIAN:
            login(request, user)

            return redirect(
                "laboratory:dashboard"
            )


        # DOCTOR
        if user.role == CustomUser.Role.DOCTOR:

            if not hasattr(
                user,
                "doctor_profile",
            ):
                messages.error(
                    request,
                    "Doctor profile is not configured.",
                )

                return render(
                    request,
                    "accounts/staff_portal.html",
                )

            login(request, user)

            return redirect(
                "dashboard:doctor"
            )


        # ALL OTHER ROLES / PATIENT
        messages.error(
            request,
            "This account cannot access the Staff Portal.",
        )


    return render(
        request,
        "accounts/staff_portal.html",
    )