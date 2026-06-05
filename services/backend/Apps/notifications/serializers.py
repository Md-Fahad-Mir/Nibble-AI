from rest_framework import serializers

from Apps.notifications.models import (
    DeviceToken,
    Notification,
    NotificationPreference,
)


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ["id", "token", "platform", "is_active", "created_at"]
        read_only_fields = ["id", "is_active", "created_at"]


class RegisterDeviceSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=512)
    platform = serializers.ChoiceField(
        choices=DeviceToken.Platform.choices, default=DeviceToken.Platform.WEB
    )


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "push_enabled",
            "receipt_reminders",
            "review_reminders",
            "rewards",
            "new_offers",
            "inactivity",
            "promotional",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "body",
            "data",
            "status",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields
