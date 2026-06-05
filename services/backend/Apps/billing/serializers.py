from rest_framework import serializers

from Apps.billing.models import Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "monthly_price",
            "rebate_fee_percent",
            "review_fee",
            "data_access_level",
            "customer_data_module",
            "sort_order",
        ]
        read_only_fields = fields
