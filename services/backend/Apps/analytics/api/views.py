"""Analytics endpoints: brand dashboards (tenant-scoped) + platform (admin)."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Apps.analytics import serializers as s
from Apps.analytics import services
from Apps.analytics.models import PlatformStat
from Apps.brands.access import get_brand_or_404, require_membership
from Apps.common.permissions import IsPlatformAdmin


@extend_schema(tags=["analytics"])
class BrandOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.BrandOverviewSerializer})
    def get(self, request, brand_id):
        brand = get_brand_or_404(brand_id)
        require_membership(request.user, brand)
        return Response(s.BrandOverviewSerializer(services.brand_overview(brand)).data)


@extend_schema(tags=["analytics"])
class BrandCampaignAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.CampaignMetricSerializer(many=True)})
    def get(self, request, brand_id):
        brand = get_brand_or_404(brand_id)
        require_membership(request.user, brand)
        rows = []
        for campaign in brand.campaigns.all():
            rows.append(
                {
                    "campaign_id": campaign.id,
                    "name": campaign.name,
                    "status": campaign.status,
                    **services.campaign_metrics(campaign),
                }
            )
        return Response(s.CampaignMetricSerializer(rows, many=True).data)


@extend_schema(tags=["analytics"])
class BrandProductAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.ProductMetricSerializer(many=True)})
    def get(self, request, brand_id):
        brand = get_brand_or_404(brand_id)
        require_membership(request.user, brand)
        rows = []
        for product in brand.products.all():
            rows.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    **services.product_metrics(product),
                }
            )
        return Response(s.ProductMetricSerializer(rows, many=True).data)


@extend_schema(tags=["admin-analytics"])
class PlatformOverviewView(APIView):
    permission_classes = [IsPlatformAdmin]

    @extend_schema(responses={200: s.PlatformOverviewSerializer})
    def get(self, request):
        return Response(s.PlatformOverviewSerializer(services.platform_overview()).data)


@extend_schema(tags=["admin-analytics"])
class PlatformSnapshotListView(APIView):
    permission_classes = [IsPlatformAdmin]

    @extend_schema(responses={200: s.PlatformStatSerializer(many=True)})
    def get(self, request):
        return Response(
            s.PlatformStatSerializer(PlatformStat.objects.all(), many=True).data
        )
