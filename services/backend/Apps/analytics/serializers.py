from rest_framework import serializers

from Apps.analytics.models import PlatformStat


class SpendSerializer(serializers.Serializer):
    rebate_reward = serializers.DecimalField(max_digits=14, decimal_places=2)
    rebate_fee = serializers.DecimalField(max_digits=14, decimal_places=2)
    review_reward = serializers.DecimalField(max_digits=14, decimal_places=2)
    review_fee = serializers.DecimalField(max_digits=14, decimal_places=2)
    subscription = serializers.DecimalField(max_digits=14, decimal_places=2)
    total = serializers.DecimalField(max_digits=14, decimal_places=2)


class BrandOverviewSerializer(serializers.Serializer):
    reservations = serializers.IntegerField()
    active_reservations = serializers.IntegerField()
    approvals = serializers.IntegerField()
    rejected_receipts = serializers.IntegerField()
    redemptions = serializers.IntegerField()
    reviews = serializers.IntegerField()
    published_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(
        max_digits=3, decimal_places=2, allow_null=True
    )
    spend = SpendSerializer()


class CampaignMetricSerializer(serializers.Serializer):
    campaign_id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField()
    reservations = serializers.IntegerField()
    active_reservations = serializers.IntegerField()
    approvals = serializers.IntegerField()
    rejected_receipts = serializers.IntegerField()
    redemptions = serializers.IntegerField()
    reward_spend = serializers.DecimalField(max_digits=14, decimal_places=2)
    fee_spend = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_spend = serializers.DecimalField(max_digits=14, decimal_places=2)


class ProductMetricSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    name = serializers.CharField()
    redemptions = serializers.IntegerField()
    reviews_count = serializers.IntegerField()
    average_rating = serializers.DecimalField(
        max_digits=3, decimal_places=2, allow_null=True
    )
    reward_spend = serializers.DecimalField(max_digits=14, decimal_places=2)


class PlatformOverviewSerializer(serializers.Serializer):
    brands_total = serializers.IntegerField()
    active_brands = serializers.IntegerField()
    users_total = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    reservations_total = serializers.IntegerField()
    redemptions_total = serializers.IntegerField()
    reviews_total = serializers.IntegerField()
    total_reward_paid = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_fees = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_payouts = serializers.DecimalField(max_digits=14, decimal_places=2)


class PlatformStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformStat
        fields = "__all__"
        read_only_fields = [f.name for f in PlatformStat._meta.fields]
