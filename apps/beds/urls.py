from django.urls import path

from . import views


app_name = "beds"


urlpatterns = [
    path(
        "",
        views.bed_list,
        name="list",
    ),
]