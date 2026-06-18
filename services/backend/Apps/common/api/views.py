"""Operational endpoints that are not tied to any business domain."""

from django.conf import settings
from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Liveness/readiness probe.

    Returns service metadata and reports database connectivity so load
    balancers and uptime checks can distinguish "app up" from "db down".
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Health check",
        description="Returns service status and database connectivity.",
        responses={200: None, 503: None},
        tags=["ops"],
    )
    def get(self, request):
        db_ok = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            db_ok = False

        payload = {
            "status": "ok" if db_ok else "degraded",
            "service": "nibblai-backend",
            "version": "0.1.0",
            "database": "ok" if db_ok else "unavailable",
        }
        http_status = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(payload, status=http_status)


class PublicConfigView(APIView):
    """Public, client-readable platform tunables (so copy isn't hardcoded)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(summary="Public config", responses={200: None}, tags=["ops"])
    def get(self, request):
        return Response(
            {
                "claim_window_days": settings.RESERVATION_EXPIRY_DAYS,
                "review_reward_amount": str(settings.REVIEW_REWARD_AMOUNT),
                "referral_bonus_amount": str(settings.REFERRAL_BONUS_AMOUNT),
                "payout_min_amount": str(settings.PAYOUT_MIN_AMOUNT),
            }
        )
