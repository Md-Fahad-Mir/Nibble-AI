from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from Apps.billing.models import Plan
from Apps.billing.serializers import PlanSerializer


@extend_schema(tags=["plans"])
class PlanViewSet(ReadOnlyModelViewSet):
    """Public, read-only catalogue of subscription plans."""

    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    lookup_field = "slug"
