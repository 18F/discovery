# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0013_auto_20140903_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='sam_expiration_date',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
