"""Redemption history: consumer (own) + brand (tenant-scoped)."""

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Apps.brands.access import get_brand_or_404, require_membership
from Apps.rebates import serializers as s
from Apps.rebates.selectors import (
    get_user_redemption,
    redemptions_for_brand,
    redemptions_for_user,
)


@extend_schema(tags=["redemptions"])
class RedemptionListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.RedemptionSerializer(many=True)})
    def get(self, request):
        return Response(
            s.RedemptionSerializer(redemptions_for_user(request.user), many=True).data
        )


@extend_schema(tags=["redemptions"])
class RedemptionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.RedemptionSerializer})
    def get(self, request, redemption_id):
        redemption = get_user_redemption(request.user, redemption_id)
        if redemption is None:
            raise NotFound("Redemption not found.")
        return Response(s.RedemptionSerializer(redemption).data)


@extend_schema(tags=["redemptions"])
class BrandRedemptionListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.RedemptionSerializer(many=True)})
    def get(self, request, brand_id):
        brand = get_brand_or_404(brand_id)
        require_membership(request.user, brand)
        return Response(
            s.RedemptionSerializer(redemptions_for_brand(brand), many=True).data
        )
