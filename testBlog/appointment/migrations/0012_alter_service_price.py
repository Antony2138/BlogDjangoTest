# Generated by Django 5.1.1 on 2025-05-10 23:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0011_alter_archivedappointmentrequest_staff_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='price',
            field=models.DecimalField(decimal_places=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
