# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0017_pool_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='setaside',
            name='far_order',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
