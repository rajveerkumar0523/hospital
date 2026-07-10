from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.appointments.models import TestBill


@login_required
def reception_dashboard(request):

    if request.user.role != "RECEPTIONIST":
        return redirect("home")

    today = timezone.localdate()

    pending_bills = (
        TestBill.objects
        .filter(
            payment_status=TestBill.PaymentStatus.UNPAID,
        )
        .select_related(
            "appointment",
            "appointment__patient",
            "appointment__doctor",
            "appointment__doctor__user",
        )
        .prefetch_related("items")
        .order_by("-created_at")[:5]
    )

    today_payments = (
        TestBill.objects
        .filter(
            payment_status=TestBill.PaymentStatus.PAID,
            paid_at__date=today,
        )
        .select_related(
            "appointment",
            "appointment__patient",
            "collected_by",
        )
        .order_by("-paid_at")[:5]
    )

    pending_bill_count = TestBill.objects.filter(
        payment_status=TestBill.PaymentStatus.UNPAID,
    ).count()

    payments_collected = TestBill.objects.filter(
        payment_status=TestBill.PaymentStatus.PAID,
        paid_at__date=today,
    ).count()

    today_collection = (
        TestBill.objects
        .filter(
            payment_status=TestBill.PaymentStatus.PAID,
            paid_at__date=today,
        )
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    patients_served = (
        TestBill.objects
        .filter(
            payment_status=TestBill.PaymentStatus.PAID,
            paid_at__date=today,
        )
        .values("appointment__patient_id")
        .distinct()
        .count()
    )

    context = {
        "pending_bills": pending_bills,
        "today_payments": today_payments,
        "pending_bill_count": pending_bill_count,
        "payments_collected": payments_collected,
        "today_collection": today_collection,
        "patients_served": patients_served,
    }

    return render(
        request,
        "reception/receptionist_dashboard.html",
        context,
    )

@login_required
def collect_test_payment(request, bill_id):

    if request.user.role != "RECEPTIONIST":
        return redirect("home")

    bill = get_object_or_404(
        TestBill.objects
        .select_related(
            "appointment",
            "appointment__patient",
        )
        .prefetch_related(
            "items",
        ),
        id=bill_id,
        payment_status=TestBill.PaymentStatus.UNPAID,
    )

    if request.method == "POST":

        payment_method = request.POST.get(
            "payment_method",
            "",
        ).strip()

        if payment_method != "CASH":
            messages.error(
                request,
                "Please select Cash as the payment method.",
            )

            return redirect(
                "reception:collect_test_payment",
                bill_id=bill.id,
            )

        bill.payment_status = TestBill.PaymentStatus.PAID
        bill.payment_method = "CASH"
        bill.paid_at = timezone.now()
        bill.collected_by = request.user

        bill.save(
            update_fields=[
                "payment_status",
                "payment_method",
                "paid_at",
                "collected_by",
            ]
        )

        messages.success(
            request,
            f"₹{bill.total_amount} cash payment collected successfully.",
        )

        return redirect(
            "reception:dashboard"
        )

    return render(
        request,
        "reception/collect_payment.html",
        {
            "bill": bill,
        },
    )