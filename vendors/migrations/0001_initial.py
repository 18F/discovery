# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContractRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('piid', models.CharField(max_length=128, unique=True)),
                ('status', models.CharField(max_length=3, choices=[('P', 'In Progress'), ('C', 'Completed'), ('F', 'Cancelled')])),
                ('date_signed', models.DateField()),
                ('date_completed', models.DateField(null=True)),
                ('obligated_amount', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('description', models.TextField(null=True)),
                ('naics', models.CharField(null=True, max_length=25)),
                ('psc', models.CharField(null=True, max_length=25)),
                ('fpds_email', models.EmailField(null=True, max_length=75)),
                ('fapiis_email', models.EmailField(null=True, max_length=75)),
                ('fapiis_name', models.CharField(null=True, max_length=128)),
                ('vehicle', models.CharField(null=True, max_length=7, choices=[('OASISSB', 'OASIS Small Business'), ('OASIS', 'OASIS Unrestricted')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Naics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('code', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('short_code', models.CharField(max_length=25, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('number', models.CharField(max_length=128)),
                ('vehicle', models.CharField(max_length=7, choices=[('OASISSB', 'OASIS Small Business'), ('OASIS', 'OASIS Unrestricted')])),
                ('threshold', models.CharField(null=True, max_length=128)),
                ('naics', models.ManyToManyField(to='vendors.Naics')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PoolPIID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('piid', models.CharField(max_length=128)),
                ('pool', models.ForeignKey(to='vendors.Pool')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetAside',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('code', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField()),
                ('short_name', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('duns', models.IntegerField()),
                ('duns_4', models.IntegerField()),
                ('oasis_address', models.CharField(null=True, max_length=128)),
                ('oasis_citystate', models.CharField(null=True, max_length=128)),
                ('cm_name', models.CharField(null=True, max_length=128)),
                ('cm_email', models.CharField(null=True, max_length=128)),
                ('cm_phone', models.CharField(null=True, max_length=128)),
                ('pm_name', models.CharField(null=True, max_length=128)),
                ('pm_email', models.CharField(null=True, max_length=128)),
                ('pm_phone', models.CharField(null=True, max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='poolpiid',
            name='vendor',
            field=models.ForeignKey(to='vendors.Vendor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contractrecord',
            name='vendor',
            field=models.ForeignKey(to='vendors.Vendor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vendor',
            name='pools',
            field=models.ManyToManyField(through='vendors.PoolPIID', to='vendors.Pool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vendor',
            name='setasides',
            field=models.ManyToManyField(null=True, to='vendors.SetAside'),
            preserve_default=True,
        ),
    ]
