# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0019_auto_20140923_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='setasides',
            field=models.ManyToManyField(null=True, blank=True, to='vendors.SetAside'),
        ),
    ]
