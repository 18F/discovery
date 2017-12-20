from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.core.management import call_command


@shared_task
def update_vendors():
    call_command('load_vendors')
