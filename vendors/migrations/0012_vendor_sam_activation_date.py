# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0011_vendor_cage'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='sam_activation_date',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
