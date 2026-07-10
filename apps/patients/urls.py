from django.urls import path

from . import views


app_name = "patients"


urlpatterns = [
    path(
        "complete-profile/",
        views.complete_profile,
        name="complete_profile",
    ),

    path(
        "profile/",
        views.profile,
        name="profile",
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),
]