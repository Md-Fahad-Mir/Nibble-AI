from decimal import Decimal

from rest_framework import serializers

from Apps.wallets.models import LedgerEntry, Wallet


class WalletSerializer(serializers.ModelSerializer):
    held = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            "id",
            "kind",
            "currency",
            "balance",
            "held",
            "available",
            "updated_at",
        ]
        read_only_fields = fields

    def get_held(self, obj) -> Decimal:
        return obj.held_amount()

    def get_available(self, obj) -> Decimal:
        return obj.available()


class LedgerEntrySerializer(serializers.ModelSerializer):
    signed_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "entry_type",
            "amount",
            "signed_amount",
            "category",
            "balance_after",
            "reference_type",
            "reference_id",
            "description",
            "created_at",
        ]
        read_only_fields = fields


class FundWalletSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, min_value=Decimal("0.01")
    )
    # Optional client-supplied key so a retried funding request is not
    # double-posted (the ledger dedupes on this key).
    idempotency_key = serializers.CharField(
        required=False, allow_blank=True, max_length=128
    )
