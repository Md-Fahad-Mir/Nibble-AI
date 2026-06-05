"""Read-side queries for notifications."""

from Apps.notifications.models import Notification


def notifications_for_user(user, *, unread_only: bool = False):
    qs = Notification.objects.filter(user=user)
    if unread_only:
        qs = qs.filter(read_at__isnull=True)
    return qs
