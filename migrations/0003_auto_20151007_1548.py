# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_auth', '0002_auto_20151007_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default=b'000', max_length=40),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sms_activation',
            field=models.CharField(default=b'000', max_length=40),
        ),
    ]
