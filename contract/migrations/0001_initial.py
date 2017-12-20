# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='FPDSContract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('piid', models.CharField(max_length=128)),
                ('date_signed', models.DateField()),
                ('completion_date', models.DateField(null=True)),
                ('agency_id', models.IntegerField()),
                ('agency_name', models.CharField(max_length=128)),
                ('pricing_type', models.CharField(choices=[('A', 'Fixed Price Redetermination'), ('B', 'Fixed Price Level of Effort'), ('J', 'Firm Fixed Price'), ('K', 'Fixed Price with Economic Price Adjustment'), ('L', 'Fixed Price Incentive'), ('M', 'Fixed Price Award Fee'), ('R', 'Cost Plus Award Fee'), ('S', 'Cost No Fee'), ('T', 'Cost Sharing'), ('U', 'Cost Plus Fixed Fee'), ('V', 'Cost Plus Incentive Fee'), ('Y', 'Time and Materials'), ('Z', 'Labor Hours'), ('1', 'Order Dependent'), ('2', 'Combination'), ('3', 'Other')], null=True, max_length=2)),
                ('obligated_amount', models.DecimalField(max_digits=128, null=True, decimal_places=2)),
                ('last_modified_by', models.EmailField(null=True, max_length=75)),
                ('PSC', models.CharField(null=True, max_length=128)),
                ('NAICS', models.ForeignKey(to='vendors.Naics', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
