from django.apps import AppConfig


class RebatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.rebates"
    label = "rebates"
    verbose_name = "Rebates"

    def ready(self):
        from Apps.rebates import signals  # noqa: F401
