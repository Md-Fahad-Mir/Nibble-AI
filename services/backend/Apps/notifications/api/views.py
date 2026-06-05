"""Consumer notification endpoints: device tokens, preferences, history."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Apps.notifications import serializers as s
from Apps.notifications.models import DeviceToken
from Apps.notifications.selectors import notifications_for_user
from Apps.notifications.services import get_preference


@extend_schema(tags=["notifications"])
class DeviceTokenListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.DeviceTokenSerializer(many=True)})
    def get(self, request):
        return Response(
            s.DeviceTokenSerializer(request.user.device_tokens.all(), many=True).data
        )

    @extend_schema(request=s.RegisterDeviceSerializer, responses={201: s.DeviceTokenSerializer})
    def post(self, request):
        serializer = s.RegisterDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # Upsert by token; re-registering reactivates and reassigns ownership.
        device, _ = DeviceToken.objects.update_or_create(
            token=data["token"],
            defaults={
                "user": request.user,
                "platform": data["platform"],
                "is_active": True,
            },
        )
        return Response(s.DeviceTokenSerializer(device).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["notifications"])
class DeviceTokenDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request, token_id):
        device = request.user.device_tokens.filter(id=token_id).first()
        if device is None:
            raise NotFound("Device token not found.")
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["notifications"])
class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: s.NotificationPreferenceSerializer})
    def get(self, request):
        return Response(s.NotificationPreferenceSerializer(get_preference(request.user)).data)

    @extend_schema(request=s.NotificationPreferenceSerializer, responses={200: s.NotificationPreferenceSerializer})
    def patch(self, request):
        pref = get_preference(request.user)
        serializer = s.NotificationPreferenceSerializer(pref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(tags=["notifications"])
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("unread", bool, description="Only unread.")],
        responses={200: s.NotificationSerializer(many=True)},
    )
    def get(self, request):
        unread = request.query_params.get("unread") in ("1", "true", "True")
        notifications = notifications_for_user(request.user, unread_only=unread)
        return Response(s.NotificationSerializer(notifications, many=True).data)


@extend_schema(tags=["notifications"])
class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: None})
    def post(self, request, notification_id):
        from django.utils import timezone

        notification = request.user.notifications.filter(id=notification_id).first()
        if notification is None:
            raise NotFound("Notification not found.")
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at", "updated_at"])
        return Response({"detail": "Marked as read."})


@extend_schema(tags=["notifications"])
class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: None})
    def post(self, request):
        from django.utils import timezone

        count = request.user.notifications.filter(read_at__isnull=True).update(
            read_at=timezone.now()
        )
        return Response({"marked_read": count})
