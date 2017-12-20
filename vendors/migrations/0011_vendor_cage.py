# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0010_auto_20140828_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='cage',
            field=models.CharField(max_length=15, null=True),
            preserve_default=True,
        ),
    ]
