from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.core.management import call_command


@shared_task
def update_fpds(years=10, weeks=520, count=500, pause=1):
    call_command('load_fpds', 
                 years=years, 
                 weeks=weeks, 
                 count=count, 
                 pause=pause
    )
