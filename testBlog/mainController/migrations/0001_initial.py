# Generated by Django 5.1.1 on 2024-11-02 11:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Meet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('time_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainController.chank')),
            ],
            options={
                'verbose_name': 'Записи',
                'verbose_name_plural': 'Записи',
            },
        ),
    ]
