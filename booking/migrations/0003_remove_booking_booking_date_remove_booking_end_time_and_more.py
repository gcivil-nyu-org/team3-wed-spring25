# Generated by Django 4.2.19 on 2025-03-13 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0002_booking_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="booking",
            name="booking_date",
        ),
        migrations.RemoveField(
            model_name="booking",
            name="end_time",
        ),
        migrations.RemoveField(
            model_name="booking",
            name="start_time",
        ),
        migrations.AlterField(
            model_name="booking",
            name="total_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.CreateModel(
            name="BookingSlot",
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
                ("start_date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_date", models.DateField()),
                ("end_time", models.TimeField()),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="slots",
                        to="booking.booking",
                    ),
                ),
            ],
        ),
    ]
