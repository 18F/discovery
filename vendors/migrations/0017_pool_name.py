# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0016_auto_20140917_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='pool',
            name='name',
            field=models.CharField(default='Pool', max_length=128),
            preserve_default=True,
        ),
    ]
