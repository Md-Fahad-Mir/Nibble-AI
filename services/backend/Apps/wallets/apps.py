from django.apps import AppConfig


class WalletsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.wallets"
    label = "wallets"
    verbose_name = "Wallets"

    def ready(self):
        # Connect signal receivers (e.g. referral bonus on email verification).
        from Apps.wallets import signals  # noqa: F401
