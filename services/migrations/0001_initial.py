# Generated by Django 5.1 on 2024-10-04 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=100)),
                ('service_img', models.ImageField(upload_to='services/')),
                ('service_description', models.TextField()),
            ],
        ),
    ]
