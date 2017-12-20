# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0007_auto_20140722_2125'),
    ]

    operations = [
        migrations.CreateModel(
            name='SamLoad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sam_load', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
