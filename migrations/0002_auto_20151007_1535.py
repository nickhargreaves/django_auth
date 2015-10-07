# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default=b'000', max_length=12),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='sms_activation',
            field=models.CharField(default=b'000', max_length=12),
        ),
    ]
