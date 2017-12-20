# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0021_auto_20171208_0423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='point_of_contact',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
