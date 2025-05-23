# Generated by Django 5.1 on 2025-02-06 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0007_alter_booking_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('canceled', 'Canceled'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
    ]
