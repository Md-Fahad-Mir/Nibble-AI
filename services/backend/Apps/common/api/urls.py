from django.urls import path

from Apps.common.api.views import HealthCheckView, PublicConfigView

app_name = "common"

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("config/", PublicConfigView.as_view(), name="config"),
]
