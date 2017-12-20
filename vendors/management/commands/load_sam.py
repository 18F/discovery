from optparse import make_option
from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from vendors.models import Vendor, Pool, SetAside, SamLoad
from mirage_site.utils import csv_memory

import os
import sys
import logging
import traceback
import warnings
import StringIO

import requests
import json
import csv


warnings.filterwarnings('ignore')


def vendor_logger():
    return logging.getLogger('vendor')

def vendor_mem_logger():
    return logging.getLogger('vendor_memory')

def log_memory(message = "Memory"):
    vendor_mem_logger().info(csv_memory(message))

def sam_data_logger():
    return logging.getLogger('sam_data')

def log_data(*args):
    line = StringIO.StringIO()
    writer = csv.writer(line)
    writer.writerow([unicode(s).encode("utf-8") for s in args])
    sam_data_logger().info(line.getvalue().rstrip())


def display_error(info):
    print("MAJOR ERROR -- PROCESS ENDING EXCEPTION --  {}".format(info))
    traceback.print_tb(sys.exc_info()[2])
    vendor_logger().debug("MAJOR ERROR -- PROCESS ENDING EXCEPTION -- {}".format(info))


def get_value(obj, key, vendor):
    try:
        return obj[key]

    except KeyError as e:
        vendor_logger().debug("There was a key error on {}: {}".format(vendor.duns, e))
        return None


def get_root_sam_url(duns_4):
    return settings.SAM_API_URL + duns_4

def get_sam_url(duns_4):
    return get_root_sam_url(duns_4) + '?api_key=' + settings.SAM_API_KEY


class Command(BaseCommand):

    option_list = BaseCommand.option_list \
                  + (make_option('--pause', action='store', type=int, dest='pause', default=1, help="Number of seconds to pause before each query to the SAM API"), ) \
                  + (make_option('--tries', action='store', type=int, dest='tries', default=3, help="Number of tries to query the SAM API before exiting"), )
    
    
    def get_vendor_ids(self):
        return Vendor.objects.filter().order_by('id').values_list('id', flat=True)
    
    
    def load_sam_data(self, duns_4, options):
        logger = vendor_logger()
        
        sam_data = {}
        loaded = True
        
        sam_url = get_sam_url(duns_4)
        log_url = get_root_sam_url(duns_4)
        
        #don't kill the api
        if options['pause'] > 0:
            sleep(options['pause'])
        
        #request data
        logger.debug("Fetching vendor at {}".format(log_url))
        request = requests.get(sam_url)

        #catch and log key problems
        if request.status_code == 403:
            if 'Message' in request.json():
                logger.debug("There was a 403 error on {}. Registration information forbidden".format(log_url))
            else:
                raise Exception('Data.gov API key is invalid')
        
        #return data object    
        try:
            sam_data = request.json()

        except ValueError:
            #the api did not return anything. Sleep and try again? (recursive goodness!)
            if options['tries'] > 0:
                options['tries'] -= 1
                options['pause'] = 5
                sam_data, loaded = self.load_sam_data(duns_4, options)
                
        if 'sam_data' in sam_data:
            sam_data = sam_data['sam_data']
        
        elif 'Error' in sam_data:
            logger.debug("SAM API returned an error for {}, and duns {}".format(log_url, duns_4))
            loaded = False
        else:
            logger.debug("Could not load data from {} for unknown reason".format(log_url))
            loaded = False
                
        return sam_data, loaded


    def update_vendor(self, vid, options):
        logger = vendor_logger()
        
        vendor = Vendor.objects.get(id=vid)
        sam_data, sam_loaded = self.load_sam_data(vendor.duns_4, options)
        
        if 'registration' in sam_data:
            print("[ {} ] - Updating SAM vendor: {}".format(vid, vendor.name))
            log_memory("Starting vendor [ {} | {} ]".format(vid, vendor.name))
        
            reg = sam_data['registration']
            
            vendor.sam_status = get_value(reg, 'status', vendor)
            vendor.sam_activation_date = get_value(reg, 'activationDate', vendor)
            vendor.sam_expiration_date = get_value(reg, 'expirationDate', vendor)
            vendor.sam_exclusion = get_value(reg, 'hasKnownExclusion', vendor)
            vendor.cage = get_value(reg, 'cage', vendor)
            
            addr = get_value(reg, 'samAddress', vendor)
            if addr:
                vendor.sam_address = get_value(addr, 'Line1', vendor)
                vendor.sam_citystate = "{}, {} {}".format(get_value(addr, 'City', vendor),
                                                          get_value(addr, 'stateorProvince', vendor),
                                                          get_value(addr, 'Zip', vendor))

            vendor.sam_url = get_value(reg, 'corporateUrl', vendor)
            if vendor.sam_url and vendor.sam_url[:3].lower() == "www" :
                vendor.sam_url = 'http://' + vendor.sam_url

            setasides = get_value(reg, 'businessTypes', vendor)
            for code in setasides:
                try:
                    sa = SetAside.objects.get(code__iexact=code)
                    if sa not in vendor.setasides.all():
                        vendor.setasides.add(sa)

                except SetAside.DoesNotExist:
                    continue
            
            vendor.save()           
            
            log_memory("Final vendor [ {} | {} ]".format(vid, vendor.name))
            log_data(vendor.name,
                vendor.duns,
                vendor.duns_4,
                vendor.cm_name,
                vendor.cm_phone,
                vendor.cm_email,
                vendor.pm_name,
                vendor.pm_phone,
                vendor.pm_email,
                vendor.sam_status,
                vendor.sam_activation_date,
                vendor.sam_expiration_date,
                vendor.sam_exclusion,
                vendor.cage,
                vendor.sam_address,
                vendor.sam_citystate,
                vendor.sam_url,
                ":".join([str(sa.pk) for sa in vendor.setasides.all()])
            )
        else:
            logger.debug("'registration' key is missing for {} / {}".format(vid, vendor.duns_4))
        

    def handle(self, *args, **options):
        print("-------BEGIN LOAD_SAM PROCESS-------")
        log_memory('Start')        
        log_data('Name', 
            'DUNS', 
            'DUNS+4', 
            'CM Name', 
            'CM Phone', 
            'CM Email', 
            'PM Name', 
            'PM Phone', 
            'PM Email', 
            'SAM Status', 
            'SAM Activation Date', 
            'SAM Expiration Date', 
            'SAM Exclusion', 
            'Cage Code', 
            'SAM Address', 
            'SAM Citystate', 
            'SAM URL', 
            'Setasides'
        )

        try:
            vendor_ids = self.get_vendor_ids()
            
            for vid in vendor_ids:
                self.update_vendor(vid, options)

            sam_load = SamLoad(sam_load=timezone.now())
            sam_load.save()

        except Exception as e:
            display_error(e)

        print("-------END LOAD_SAM PROCESS-------")
        log_memory('End')
