# Generated by Django 5.1.1 on 2025-04-11 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainUser', '0006_remove_customuser_social_link_tg_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='confirmed_credentials',
            field=models.BooleanField(default=False),
        ),
    ]
