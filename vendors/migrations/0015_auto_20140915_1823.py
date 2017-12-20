# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0014_vendor_sam_expiration_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contractrecord',
            name='vendor',
        ),
        migrations.DeleteModel(
            name='ContractRecord',
        ),
    ]
