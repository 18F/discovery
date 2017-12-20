# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0023_auto_20141023_2039'),
        ('contract', '0020_remove_contract_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='fpdsload',
            name='initialized',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fpdsload',
            name='vendor',
            field=models.OneToOneField(null=True, to='vendors.Vendor'),
            preserve_default=True,
        ),
    ]
