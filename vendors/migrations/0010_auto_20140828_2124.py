# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0009_auto_20140827_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='annual_revenue',
            field=models.CharField(max_length=128, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vendor',
            name='number_of_employees',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
