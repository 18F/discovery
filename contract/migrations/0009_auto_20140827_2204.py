# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0009_auto_20140827_2204'),
        ('contract', '0008_auto_20140826_2038'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('piid', models.CharField(db_index=True, max_length=128)),
                ('agency_id', models.CharField(max_length=128, null=True)),
                ('agency_name', models.CharField(max_length=128, null=True)),
                ('NAICS', models.CharField(max_length=128, null=True)),
                ('PSC', models.CharField(max_length=128, null=True)),
                ('date_signed', models.DateTimeField(null=True)),
                ('completion_date', models.DateTimeField(null=True)),
                ('pricing_type', models.CharField(max_length=2, null=True, choices=[('A', 'Fixed Price Redetermination'), ('B', 'Fixed Price Level of Effort'), ('J', 'Firm Fixed Price'), ('K', 'Fixed Price with Economic Price Adjustment'), ('L', 'Fixed Price Incentive'), ('M', 'Fixed Price Award Fee'), ('R', 'Cost Plus Award Fee'), ('S', 'Cost No Fee'), ('T', 'Cost Sharing'), ('U', 'Cost Plus Fixed Fee'), ('V', 'Cost Plus Incentive Fee'), ('Y', 'Time and Materials'), ('Z', 'Labor Hours'), ('1', 'Order Dependent'), ('2', 'Combination'), ('3', 'Other')])),
                ('obligated_amount', models.DecimalField(decimal_places=2, null=True, max_digits=128)),
                ('status', models.CharField(max_length=128, null=True)),
                ('point_of_contact', models.EmailField(max_length=75, null=True)),
                ('vendor', models.ForeignKey(to='vendors.Vendor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='FAPIISRecord',
        ),
        migrations.AlterField(
            model_name='fpdscontract',
            name='piid',
            field=models.CharField(db_index=True, max_length=128),
        ),
    ]
