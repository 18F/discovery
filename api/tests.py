from django.test import Client, TestCase
from django.utils import timezone
import json

from vendors.models import SamLoad


class NaicsTest(TestCase):
    """tests for NAICS API endpoint"""
    fixtures = ['naics.json']

    def setUp(self):
        self.c = Client()
        self.path = '/api/naics/'

    def test_request_no_params(self):
        resp = self.c.get(self.path, {'format': 'json'})
        
        self.assertEqual(resp.data['num_results'], 34)
        self.assertEqual(resp.status_code, 200)

    def test_request_q_param(self):
        resp = self.c.get(self.path, {'q': 'test'})
        
        self.assertEqual(resp.data['num_results'], 1)
        self.assertEqual(resp.status_code, 200)


class VendorsTest(TestCase):
    """test for vendor API endpoint"""
    fixtures = ['naics.json', 'setasides.json', 'pools.json', 'vendors.json', 'poolpiids.json']
 
    def setUp(self):
        self.c = Client()
        self.path = '/api/vendors/'
        sl = SamLoad(sam_load=timezone.now())
        sl.save()

    def test_request_no_params(self):
        resp = self.c.get(self.path, {'format': 'json'})
        self.assertEqual(resp.status_code, 400)

    def test_request_valid_naics(self):
        resp = self.c.get(self.path, {'format': 'json', 'naics': '541330'})
        self.assertEqual(resp.status_code, 200)

    def test_request_invalid_naics_returns_400(self):
        resp = self.c.get(self.path, {'format': 'json', 'naics': 'dlasfjosdf'})
        self.assertEqual(resp.status_code, 400)
    
    def test_request_num_results(self):
        resp = self.c.get(self.path, {'format': 'json', 'naics': '541330'})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.data['num_results'], 0)

    def test_request_results(self):
        resp = self.c.get(self.path, {'format': 'json', 'naics': '541330'})
        self.assertEqual(resp.status_code, 200)
        assert 'results' in resp.data

    def test_latest_sam_load_with_data(self):
        resp = self.c.get(self.path, {'format': 'json', 'naics': '541330'})
        self.assertEqual(resp.status_code, 200)
        assert 'sam_load' in resp.data

    def test_sam_load_with_no_data(self):
        SamLoad.objects.all().delete()
        resp = self.c.get(self.path, {'format': 'json', 'naics': '541330'})
        self.assertEqual(resp.status_code, 200)
        assert 'sam_load' in resp.data

    def test_one_pool_returned(self):
        resp = self.c.get(self.path, {'format': 'json', 'vehicle': 'oasissb', 'naics': '541330' })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), resp.data['num_results'])
        self.assertEqual(resp.data['pool'][0]['id'], '1_SB')

    def test_result_length_pool_group(self):
        resp = self.c.get(self.path, {'format': 'json', 'setasides': 'A2', 'vehicle': 'oasissb', 'naics': '541330'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), resp.data['num_results'])


class VendorTest(TestCase):
    """ tests single vendor endpoint """
    fixtures = ['setasides.json', 'vendors.json']

    def setUp(self):
        self.c = Client()
        self.path = '/api/vendor/118498067/'

    def test_vendor_exists(self):
        resp = self.c.get(self.path)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'] , 'Advanced C4 Solutions, Inc. dba AC4S')


class ContractsTest(TestCase):
    """tests for Contracts API endpoint"""
    fixtures = ['naics.json', 'setasides.json', 'pools.json', 'vendors.json', 'poolpiids.json', 'contracts.json']

    def setUp(self):
        self.c = Client()
        self.path = '/api/contracts/'

    def test_no_duns_400(self):
        resp = self.c.get(self.path)
        self.assertEqual(resp.status_code, 400)

    def test_default_pagination(self):
        resp = self.c.get(self.path, {'duns': '007901598'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 100)
        self.assertEqual(resp.data['previous'], None)
        self.assertTrue('page=2' in resp.data['next'])
        self.assertEqual(resp.data['num_results'], 905)

    def test_naics_filter(self):
        resp = self.c.get(self.path, {'duns': '807990382', 'naics': '541611'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['num_results'], 1)

    def test_default_sort(self):
        resp = self.c.get(self.path, {'duns': '807990382', 'sort': 'status'})
        resp2 = self.c.get(self.path, {'duns': '807990382', 'sort': 'status', 'direction': 'desc'})
        #responses should be equal because default sort is desc
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp.data['results'], resp2.data['results'])

    def test_sort_with_all_params(self):
        resp = self.c.get(self.path, {'duns': '807990382', 'sort': 'status', 'direction': 'asc'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'][0]['status'], 'Completed')


class MetadataTest(TestCase):
    """ Tests the metadata endpoint """
    fixtures = ['samloads.json', 'setasides.json', 'vendors.json', 'fpdsloads.json']

    def setUp(self):
        self.c = Client()
        self.path = '/api/metadata/'

    def test_metadata(self):
        resp = self.c.get(self.path)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(None, resp.data['sam_load_date'])
        self.assertNotEqual(None, resp.data['fpds_load_date'])





