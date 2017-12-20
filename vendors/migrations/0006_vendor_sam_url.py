# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0005_vendor_sam_exclusion'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='sam_url',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
    ]
