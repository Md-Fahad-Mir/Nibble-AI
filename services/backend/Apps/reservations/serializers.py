from rest_framework import serializers

from Apps.reservations.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    brand_name = serializers.CharField(source="campaign.brand.name", read_only=True)
    product_name = serializers.CharField(
        source="campaign.product.name", read_only=True
    )

    class Meta:
        model = Reservation
        fields = [
            "id",
            "campaign",
            "campaign_name",
            "brand_name",
            "product_name",
            "kind",
            "offer_type",
            "reward_amount",
            "status",
            "expires_at",
            "redeemed_at",
            "created_at",
        ]
        read_only_fields = fields


class CreateReservationSerializer(serializers.Serializer):
    campaign = serializers.UUIDField()
