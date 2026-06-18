from django.urls import path

from Apps.notifications.api import views

app_name = "notifications"

urlpatterns = [
    path("device-tokens/", views.DeviceTokenListCreateView.as_view(), name="device-list"),
    path("device-tokens/<uuid:token_id>/", views.DeviceTokenDeleteView.as_view(), name="device-delete"),
    path("notification-preferences/", views.NotificationPreferenceView.as_view(), name="preferences"),
    path("notifications/", views.NotificationListView.as_view(), name="notification-list"),
    path("notifications/unread-count/", views.NotificationUnreadCountView.as_view(), name="notification-unread-count"),
    path("notifications/read-all/", views.NotificationReadAllView.as_view(), name="notification-read-all"),
    path("notifications/<uuid:notification_id>/read/", views.NotificationReadView.as_view(), name="notification-read"),
]
