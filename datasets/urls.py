
from django.urls import path

from .views import (
    upload_dataset,
    dataset_history,
    dataset_preview,
)


urlpatterns = [

    path("upload/",upload_dataset,name="upload_dataset"),
    path("",dataset_history,name="dataset_history"),
    path("<str:dataset_id>/",dataset_preview,name="dataset_preview"),

]
