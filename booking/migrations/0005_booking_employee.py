# Generated by Django 5.1 on 2025-02-03 17:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_booking_service'),
        ('employee', '0005_employee_location_lat_employee_location_long'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.employee'),
        ),
    ]
