# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-17 07:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('statistics', '0002_delete_test'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Hostname', models.CharField(max_length=255)),
                ('Password', models.CharField(max_length=255)),
            ],
        ),
    ]
