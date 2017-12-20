# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0006_vendor_sam_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendor',
            old_name='oasis_address',
            new_name='sam_address',
        ),
        migrations.RenameField(
            model_name='vendor',
            old_name='oasis_citystate',
            new_name='sam_citystate',
        ),
    ]
