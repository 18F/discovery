# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='duns',
            field=models.CharField(max_length=9),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='duns_4',
            field=models.CharField(max_length=12),
        ),
    ]
