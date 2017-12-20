# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0022_auto_20141023_2038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='annual_revenue',
            field=models.BigIntegerField(null=True),
        ),
    ]
