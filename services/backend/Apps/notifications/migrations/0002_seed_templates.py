from django.db import migrations

TEMPLATES = [
    {
        "type": "receipt_reminder",
        "title": "Upload your receipt",
        "body": "Don't forget to upload your receipt for {brand} to claim your reward.",
    },
    {
        "type": "review_reminder",
        "title": "Finish your review",
        "body": "Complete your review of {product} to earn ${amount}.",
    },
    {
        "type": "rewards_waiting",
        "title": "You have rewards waiting",
        "body": "Review {product} and earn ${amount}. Don't miss out!",
    },
    {
        "type": "new_offers",
        "title": "New offers available",
        "body": "{brand} just launched a new offer. Check it out!",
    },
    {
        "type": "inactive",
        "title": "We miss you",
        "body": "You haven't logged in recently — new rewards are waiting for you.",
    },
    {
        "type": "promotional",
        "title": "{title}",
        "body": "{message}",
    },
]


def seed(apps, schema_editor):
    NotificationTemplate = apps.get_model("notifications", "NotificationTemplate")
    for data in TEMPLATES:
        NotificationTemplate.objects.update_or_create(
            type=data["type"],
            defaults={"title": data["title"], "body": data["body"], "is_active": True},
        )


def unseed(apps, schema_editor):
    NotificationTemplate = apps.get_model("notifications", "NotificationTemplate")
    NotificationTemplate.objects.filter(
        type__in=[t["type"] for t in TEMPLATES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("notifications", "0001_initial")]

    operations = [migrations.RunPython(seed, unseed)]
