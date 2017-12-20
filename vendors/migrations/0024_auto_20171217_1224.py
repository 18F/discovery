# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0023_auto_20141023_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='setasides',
            field=models.ManyToManyField(to='vendors.SetAside', blank=True),
        ),
    ]
