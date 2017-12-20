# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0018_setaside_far_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='setaside',
            name='description',
        ),
        migrations.AddField(
            model_name='setaside',
            name='abbreviation',
            field=models.CharField(max_length=10, null=True),
            preserve_default=True,
        ),
    ]
