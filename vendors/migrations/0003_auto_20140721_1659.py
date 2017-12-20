# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0002_auto_20140721_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='duns_4',
            field=models.CharField(max_length=13),
        ),
    ]
