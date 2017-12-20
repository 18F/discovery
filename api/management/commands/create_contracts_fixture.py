from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from vendors.models import Vendor
from contract.models import Contract

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        vendors = Vendor.objects.filter(duns__in=["197138274", "090739830"])
        
        with open(settings.BASE_DIR + '/contract/fixtures/fpds_test_vendor.json', 'w') as out:
            data = serializers.serialize('json', vendors, stream=out)

        with open(settings.BASE_DIR + '/api/fixtures/contracts.json', 'w') as out:
            data = serializers.serialize('json', Contract.objects.filter(vendor=vendors), stream=out)

