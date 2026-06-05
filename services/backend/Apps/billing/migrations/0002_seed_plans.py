from decimal import Decimal

from django.db import migrations

# Seed defaults. Prices/fees are placeholders the business can adjust in the
# admin; the tiers and data-access levels follow the spec
# (Starter = anonymized data + highest fee; Scale = full data + lowest fee).
PLANS = [
    {
        "slug": "starter",
        "name": "Starter",
        "description": "Entry tier with anonymized customer data.",
        "monthly_price": Decimal("0.00"),
        "rebate_fee_percent": Decimal("20.00"),
        "review_fee": Decimal("0.30"),
        "data_access_level": "anonymized",
        "customer_data_module": False,
        "sort_order": 1,
    },
    {
        "slug": "pro",
        "name": "Pro",
        "description": "Full customer data access and lower fees.",
        "monthly_price": Decimal("99.00"),
        "rebate_fee_percent": Decimal("15.00"),
        "review_fee": Decimal("0.25"),
        "data_access_level": "full",
        "customer_data_module": True,
        "sort_order": 2,
    },
    {
        "slug": "scale",
        "name": "Scale",
        "description": "Highest tier with the lowest fees.",
        "monthly_price": Decimal("299.00"),
        "rebate_fee_percent": Decimal("10.00"),
        "review_fee": Decimal("0.20"),
        "data_access_level": "full",
        "customer_data_module": True,
        "sort_order": 3,
    },
]


def seed_plans(apps, schema_editor):
    Plan = apps.get_model("billing", "Plan")
    for data in PLANS:
        Plan.objects.update_or_create(slug=data["slug"], defaults=data)


def unseed_plans(apps, schema_editor):
    Plan = apps.get_model("billing", "Plan")
    Plan.objects.filter(slug__in=[p["slug"] for p in PLANS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_plans, unseed_plans),
    ]
