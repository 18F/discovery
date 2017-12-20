from django.test import TestCase, RequestFactory
from vendors.models import Vendor
from vendors.views import VendorView
from django.core.management import call_command


def make_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class VendorLoadTest(TestCase):
    """Tests that the load_vendors management command works and loads all the correct fields"""
    fixtures = ['naics.json', 'setasides.json', 'pools.json']

    def test_load(self):
        call_command('load_vendors', vpp=1)


    def test_sam_expiration_not_null(self):
        null_vendors = Vendor.objects.filter(sam_expiration_date=None).count()
        self.assertEqual(null_vendors, 0)


    def test_pm_not_null(self):
        null_vendors = Vendor.objects.filter(pm_email=None).count()
        self.assertEqual(null_vendors, 0)


class VendorViewTest(TestCase):
    def test_has_capability_statement_false(self):
        request = RequestFactory().get('/vendor/0000')
        view = VendorView(template_name='vendor.html')
        view = make_view(view, request)
        context = view.get_context_data(vendor_duns='0000')
        self.assertFalse(context['has_capability_statement'])

    def test_has_capability_statement(self):
        request = RequestFactory().get('/vendor/805875718')
        view = VendorView(template_name='vendor.html')
        view = make_view(view, request)
        context = view.get_context_data(vendor_duns='805875718')
        self.assertTrue(context['has_capability_statement'])
        self.assertEqual(context['capability_statement_url'],
                         'mirage_site/capability_statements/805875718.pdf')
