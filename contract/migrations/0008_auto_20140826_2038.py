# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0008_samload'),
        ('contract', '0007_auto_20140826_1829'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAPIISRecord',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('piid', models.CharField(max_length=128, db_index=True)),
                ('agency_id', models.CharField(max_length=128, null=True)),
                ('agency_name', models.CharField(max_length=128, null=True)),
                ('NAICS', models.CharField(max_length=128, null=True)),
                ('PSC', models.CharField(max_length=128, null=True)),
                ('record_type', models.CharField(max_length=2, null=True, choices=[('C', 'Termination for Default'), ('P', 'Termination for Cause')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='fpdscontract',
            name='vendor',
            field=models.ForeignKey(to='vendors.Vendor', default=691),
            preserve_default=False,
        ),
    ]
