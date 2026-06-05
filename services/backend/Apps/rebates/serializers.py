from rest_framework import serializers

from Apps.rebates.models import Redemption


class RedemptionSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Redemption
        fields = [
            "id",
            "reservation",
            "receipt",
            "campaign",
            "campaign_name",
            "brand_name",
            "user_email",
            "reward_amount",
            "fee_amount",
            "status",
            "issued_at",
            "created_at",
        ]
        read_only_fields = fields
