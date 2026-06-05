from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.admin_panel"
    label = "platform"
    verbose_name = "Platform Admin"
