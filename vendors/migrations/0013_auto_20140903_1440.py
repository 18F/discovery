# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0012_vendor_sam_activation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='sam_activation_date',
            field=models.DateTimeField(null=True),
        ),
    ]
