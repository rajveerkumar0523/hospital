from django.urls import path

from . import views


app_name = "reception"


urlpatterns = [

    path(
        "",
        views.reception_dashboard,
        name="dashboard",
    ),

    path(
        "payment/<int:bill_id>/",
        views.collect_test_payment,
        name="collect_test_payment",
    ),

]