from optparse import make_option
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from vendors.models import Vendor, Pool, PoolPIID, SetAside
from mirage_site.utils import csv_memory

import os
import sys
import logging
import traceback
import StringIO

import requests
import re
import xmltodict
import csv


def vendor_logger():
    return logging.getLogger('vendor')

def vendor_mem_logger():
    return logging.getLogger('vendor_memory')

def log_memory(message = "Memory"):
    vendor_mem_logger().info(csv_memory(message))

def vendor_data_logger():
    return logging.getLogger('vendor_data')

def log_data(*args):
    line = StringIO.StringIO()
    writer = csv.writer(line)
    writer.writerow(args)
    vendor_data_logger().info(line.getvalue().rstrip())


def display_error(info):
    print("MAJOR ERROR -- PROCESS ENDING EXCEPTION --  {0}".format(info))
    traceback.print_tb(sys.exc_info()[2])
    vendor_logger().debug("MAJOR ERROR -- PROCESS ENDING EXCEPTION -- {0}".format(info))


def replace_x(duns):
    return duns.replace('X', '0').replace('x', '0')

def duns_plus_4(duns):
    return replace_x(duns) + '0000'


class Command(BaseCommand):

    option_list = BaseCommand.option_list \
                  + (make_option('--pause', action='store', type=int, dest='pause', default=1, help="Number of seconds to pause before each query to the SAM API"), ) \
                  + (make_option('--vpp', action='store', type=int, dest='vpp', default=0, help="Number of vendors to load per pool (useful for creating fixtures)"), ) \
                  + (make_option('--tries', action='store', type=int, dest='tries', default=3, help="Number of tries to query the SAM API before exiting"), )


    def load_temp_setasides(self):
        reader = csv.reader(open(os.path.join(settings.BASE_DIR, 'vendors/docs/temp_8a_hubzone.csv')))
        
        for line in reader:
            try:
                v = Vendor.objects.get(duns=line[1])      
            except Vendor.DoesNotExist:
                print("Could not find vendor: {}".format(line[1]))
                return

            try:
                sa = SetAside.objects.get(code=line[2])
            except SetAside.DoesNotExist:
                print("Could not find setaside: {}".format(line[2]))
                return

            if sa not in v.setasides.all():
                v.setasides.add(sa)


    def update_vendor(self, record, pool_data, options):
        logger = vendor_logger()
        
        name = record[0]
        piid = record[1]
        duns = replace_x(record[2])
        
        vendor, created = Vendor.objects.get_or_create(duns=duns)
         
        print("[ {} ] - Updating vendor: {} from pool {}".format(vendor.id, name, pool_data.id))
        log_memory("Starting vendor [ {} - {} ]".format(pool_data.id, vendor.id))
              
        #update vendor object
        attr_dict = {
            'name': record[0],
            'duns': duns,
            'duns_4': duns_plus_4(duns),
            'cm_name': record[3],
            'cm_phone': record[4],
            'cm_email': record[5],
            'pm_name': record[6],
            'pm_phone': record[7],
            'pm_email': record[8]
        }

        for k, v in list(attr_dict.items()):
            if v and v != '' and v != ' ':
                setattr(vendor, k, v)

        vendor.save()

        #update pool relationship
        poolpiid, ppcreated = PoolPIID.objects.get_or_create(vendor=vendor, pool=pool_data, piid=piid)
        
        log_memory("Final vendor [ {} - {} ]".format(pool_data.id, vendor.id))
        log_data(*attr_dict.values())
        
        if created:
            logger.debug("Successfully created {}".format(vendor.name))
            return 1
        else:
            logger.debug("Vendor {} already in database".format(vendor.name))
            return 0


    def update_pool(self, vehicle, pool, data_path, options):
        logger = vendor_logger()
        
        data_stream = open(data_path, 'r')
        reader = csv.reader(data_stream)
        new_vendor_count = 0
        pool_count = 0
        
        # Skip header.
        next(reader)
        
        print("[ {} ] - Updating pool vendors".format(pool))
        log_memory("Starting pool [ {} ]".format(pool))
        
        vendors_per_pool = int(options['vpp'])

        try:
            pool_data = Pool.objects.get(number=pool, vehicle__iexact=vehicle)
            
            for line in reader:
                new_vendor_count += self.update_vendor(line, pool_data, options)
                pool_count += 1
                
                if vendors_per_pool > 0 and pool_count == vendors_per_pool:
                    break

        except Pool.DoesNotExist as e:
            logger.debug("Pool {} not found for spreadsheet".format(pool))
            data_stream.close()
            raise(e)

        except Pool.MultipleObjectsReturned as e:
            logger.debug("More than one pool matched {}. Integrity error!".format(pool))
            data_stream.close()
            raise(e)
        
        print(" --- completed pool {} with: {} vendor(s) processed".format(pool, pool_count))
        log_memory("Final pool [ {} ]".format(pool))
        data_stream.close()
        
        return new_vendor_count


    def update_vehicle(self, vehicle, options):
        vehicle_dir = os.path.join(settings.BASE_DIR, 'vendors/docs/{0}/pools'.format(vehicle))
        new_vendor_count = 0
        
        for pool_file in os.listdir(vehicle_dir):
            data_path = os.path.join(vehicle_dir, pool_file)
            pool = re.match('Pool (.*).csv', pool_file).group(1)
            
            new_vendor_count += self.update_pool(vehicle, pool, data_path, options)
        
        return new_vendor_count
        

    def handle(self, *args, **options):
        new_vendor_count = 0
        
        print("-------BEGIN LOAD_VENDORS PROCESS-------")
        log_memory('Start')        
        log_data('Name', 
            'DUNS', 
            'DUNS+4', 
            'CM Name', 
            'CM Phone', 
            'CM Email', 
            'PM Name', 
            'PM Phone', 
            'PM Email'
        )

        try:
            for vehicle in settings.VEHICLES:
                new_vendor_count += self.update_vehicle(vehicle, options)

            #load extra SAM fields
            call_command('load_sam', **options)
            
            #load extra setaside information after vendors are initialized?
            #TODO: need to figure out what this is about.
            self.load_temp_setasides()
        
        except Exception as e:
            display_error(e)
        
        print("New vendors: {}".format(new_vendor_count))
        print("-------END LOAD_VENDORS PROCESS-------")
        log_memory('End')
