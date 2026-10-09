
from django.urls import path
from .views import analytics_dashboard, ai_business_analyst

urlpatterns = [
    path(
        "<str:dataset_id>/",
        analytics_dashboard,
        name="analytics_dashboard"
    ),
    path(
        "<str:dataset_id>/ai/",
        ai_business_analyst,
        name="ai_business_analyst"
    ),
]