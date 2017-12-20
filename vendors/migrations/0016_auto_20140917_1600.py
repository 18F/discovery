# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0015_auto_20140915_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='samload',
            name='sam_load',
            field=models.DateField(),
        ),
    ]
