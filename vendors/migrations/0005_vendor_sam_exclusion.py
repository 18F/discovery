# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0004_vendor_sam_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='sam_exclusion',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
