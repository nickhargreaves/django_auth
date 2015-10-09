# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_auth', '0003_auto_20151007_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.CharField(default=b'000', max_length=40),
        ),
    ]
