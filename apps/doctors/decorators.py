from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from apps.accounts.models import CustomUser


def doctor_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # LOGGED-OUT USER
        if not request.user.is_authenticated:
            return redirect("accounts:staff_portal")

        # DOCTOR
        if request.user.role == CustomUser.Role.DOCTOR:
            return view_func(
                request,
                *args,
                **kwargs,
            )

        # OTHER LOGGED-IN USERS
        messages.error(
            request,
            "Only doctors can access this page.",
        )

        # ADMIN
        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard:admin")

        # PATIENT
        if request.user.role == CustomUser.Role.PATIENT:
            return redirect("dashboard:patient")

        return redirect("home")

    return wrapper