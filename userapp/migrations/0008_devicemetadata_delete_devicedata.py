# Generated by Django 4.2.17 on 2025-01-21 06:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("userapp", "0007_device_devicedata"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceMetadata",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("register_name", models.CharField(max_length=100)),
                (
                    "register_type",
                    models.CharField(
                        choices=[
                            ("int", "Integer"),
                            ("float", "Float"),
                            ("bool", "Boolean"),
                        ],
                        max_length=10,
                    ),
                ),
                ("min_value", models.FloatField(blank=True, null=True)),
                ("max_value", models.FloatField(blank=True, null=True)),
                ("latest_value", models.CharField(max_length=255)),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="metadata",
                        to="userapp.device",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(name="DeviceData",),
    ]
