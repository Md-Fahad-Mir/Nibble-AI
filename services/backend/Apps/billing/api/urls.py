from rest_framework.routers import DefaultRouter

from Apps.billing.api.views import PlanViewSet

app_name = "billing"

router = DefaultRouter()
router.register("plans", PlanViewSet, basename="plan")

urlpatterns = router.urls
