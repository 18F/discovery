# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0010_auto_20140828_2124'),
        ('contract', '0009_auto_20140827_2204'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAPIISRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('piid', models.CharField(db_index=True, max_length=128)),
                ('agency_id', models.CharField(max_length=128, null=True)),
                ('agency_name', models.CharField(max_length=128, null=True)),
                ('NAICS', models.CharField(max_length=128, null=True)),
                ('PSC', models.CharField(max_length=128, null=True)),
                ('record_type', models.CharField(max_length=128, null=True)),
                ('record_code', models.CharField(max_length=1, null=True)),
                ('vendor', models.ForeignKey(to='vendors.Vendor', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
