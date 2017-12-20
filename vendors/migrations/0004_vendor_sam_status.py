# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0003_auto_20140721_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='sam_status',
            field=models.CharField(null=True, max_length=128),
            preserve_default=True,
        ),
    ]
