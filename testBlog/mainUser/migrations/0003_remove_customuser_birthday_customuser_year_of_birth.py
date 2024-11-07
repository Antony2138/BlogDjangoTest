# Generated by Django 5.1.1 on 2024-11-06 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainUser', '0002_alter_customuser_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='birthday',
        ),
        migrations.AddField(
            model_name='customuser',
            name='year_of_birth',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]