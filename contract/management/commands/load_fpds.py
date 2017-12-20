from optparse import make_option
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from pyfpds import Contracts

from vendors.models import Vendor
from contract.models import Contract, FPDSLoad
from contract import catch_key_error
from mirage_site.utils import csv_memory

import os
import sys
import signal
import logging
import traceback
import StringIO

import re
import pytz
import json
import csv


def fpds_logger():
    return logging.getLogger('fpds')

def fpds_mem_logger():
    return logging.getLogger('fpds_memory')

def log_memory(message = "Memory"):
    fpds_mem_logger().info(csv_memory(message))

def fpds_data_logger():
    return logging.getLogger('fpds_data')

def log_data(*args):
    line = StringIO.StringIO()
    writer = csv.writer(line)
    writer.writerow(args)
    fpds_data_logger().info(line.getvalue().rstrip())


def display_error(info):
    print("MAJOR ERROR -- PROCESS ENDING EXCEPTION --  {0}".format(info))
    traceback.print_tb(sys.exc_info()[2])
    fpds_logger().debug("MAJOR ERROR -- PROCESS ENDING EXCEPTION -- {0}".format(info))
    
    
def crash_handler(signum, frame):
    if signum == 2: #user exit
        print("SHUTDOWN -- USER TERMINATED PROCESS --")
    else:
        fpds_mem_logger().info("System Crash: {}".format(signum))
        display_error(frame)
    
    sys.exit(1)


@catch_key_error
def get_award_id_obj(award):
    if 'awardID' in award: 
        return award['awardID']
    else:
        return award['OtherTransactionAwardID']['OtherTransactionAwardContractID']


def get_piid(award_id):
    piid = ''
    if 'referencedIDVID' in award_id:
        #part of an IDIQ
        piid = award_id['referencedIDVID']['PIID'] + '_' 
    elif 'PIID' in award_id:
        return award_id['PIID']

    piid += award_id['awardContractID']['PIID']

    return piid


def get_mod(award_id):
    if 'modNumber' in award_id:
        return award_id['modNumber']
    return award_id['awardContractID']['modNumber']


def get_agency_id(award_id):
    if 'awardContractID' in award_id:
        return award_id['awardContractID']['agencyID']['#text']
    else:
        return award_id['agencyID']['#text']


def get_agency_name(award_id):
    if 'awardContractID' in award_id:
        return award_id['awardContractID']['agencyID']['@name']
    else:
        return award_id['agencyID']['@name'] 


@catch_key_error
def get_transaction_number(award_id):
    return award_id['awardContractID']['transactionNumber']


@catch_key_error
def get_ultimate_completion_date(award):
    return award['relevantContractDates']['ultimateCompletionDate']


@catch_key_error
def get_current_completion_date(award):
    return award['relevantContractDates']['currentCompletionDate']


@catch_key_error
def get_annual_revenue(award):
    return award['vendor']['vendorSiteDetails']['vendorOrganizationFactors']['annualRevenue']


@catch_key_error
def get_number_of_employees(award):
    return award['vendor']['vendorSiteDetails']['vendorOrganizationFactors']['numberOfEmployees']


@catch_key_error
def get_last_modified_by(award):
    return award['transactionInformation']['lastModifiedBy']

@catch_key_error
def get_created_by(award):
    return award['transactionInformation']['createdBy']

def poc_is_email(text):
    if text and re.search('@', text):
        return text
    return None
    
def get_point_of_contact(award):
    poc = get_last_modified_by(award)
    if poc is None:
        poc = get_created_by(award)
        
    return poc_is_email(poc)


def get_contract_pricing_name(award):
    
    @catch_key_error
    def get_name(award):
        return award['contractData']['typeOfContractPricing']

    name = get_name(award) 
    if name and isinstance(name, basestring):
        return name

    elif name: 
        return award['contractData']['typeOfContractPricing']['@description']


@catch_key_error
def get_contract_pricing_id(award):
    return award['contractData']['typeOfContractPricing']['#text']


@catch_key_error
def get_reason_for_modification(award):
    return award['contractData']['reasonForModification']['#text']


def get_naics(award):
    
    @catch_key_error
    def get_name(award):
        return award['productOrServiceInformation']['principalNAICSCode']
    
    name = get_name(award)
    
    if name and isinstance(name, basestring):
        return name
    elif name:
        return award['productOrServiceInformation']['principalNAICSCode']['#text']


@catch_key_error
def get_psc(award):
    return award['productOrServiceInformation']['productOrServiceCode']['#text']


def init_load(options):
    if options['load_all'] and options['reinit']:
        FPDSLoad.objects.all().update(initialized=False)
        

def last_load(vendor, options):
    first_date = datetime.now() - timedelta(weeks=(52 * int(options['years'])))
    
    try:
        load = FPDSLoad.objects.get(vendor_id=vendor.id)
        load_date = first_date.date() if options['load_all'] and options['reinit'] else load.load_date 
        
        return {'load_date': load_date, 'initialized': load.initialized}
        
    except FPDSLoad.DoesNotExist:
        pass
    
    return {'load_date': first_date.date(), 'initialized': False}


def create_load(vendor, load_date):
    try:
        initialized = True if load_date >= datetime.now().date() else False
        
        load = FPDSLoad.objects.get(vendor_id=vendor.id)
        load.load_date = load_date
        load.initialized = initialized
        load.save()

    except FPDSLoad.DoesNotExist:
        FPDSLoad.objects.create(vendor_id=vendor.id, load_date=load_date, initialized=initialized)


class Command(BaseCommand):

    date_now = datetime.now().date()

    option_list = BaseCommand.option_list \
                  + (make_option('--id', action='store', type=int,  dest='id', default=1, help="load contracts for vendors greater or equal to this id"), ) \
                  + (make_option('--load_all', action='store_true', dest='load_all', default=False, help="Force load of all contracts"), ) \
                  + (make_option('--reinit', action='store_true', dest='reinit', default=False, help="Reinitialize all vendor contract data"), ) \
                  + (make_option('--years', action='store', type=int, dest='years', default=10, help="Number of years back to populate database"), ) \
                  + (make_option('--weeks', action='store', type=int, dest='weeks', default=520, help="Weekly interval to process incoming data"), ) \
                  + (make_option('--count', action='store', type=int, dest='count', default=500, help="Number of records to return from each load of the FPDS_NG ATOM feed"), ) \
                  + (make_option('--pause', action='store', type=int, dest='pause', default=1, help="Number of seconds to pause before each query to the FPDS-NG ATOM feed"), )


    def init_contract(self, raw_entry):
        fpds_contract = raw_entry['content']
        last_modified = raw_entry['modified']
        
        #get contract award information
        if 'IDV' in fpds_contract:
            return None, {} # don't get IDV records

        try:
            award = fpds_contract['award']
                    
        except KeyError:
            try:
                award = fpds_contract['OtherTransactionAward']
            except KeyError:
                return None, {}
                        
        if 'contractDetail' in award:
            award = award['contractDetail'] # for OtherTransactionAward, details are nested one more level
    
        award_id = get_award_id_obj(award)
        if award_id is None:
            return None, {}
        
        piid = get_piid(award_id)
    
        record = {
            'modified_date': last_modified.strftime("%Y-%m-%d %H:%M:%S"),
            'mod_number': get_mod(award_id), 
            'transaction_number': get_transaction_number(award_id),
            'ultimate_completion_date': get_ultimate_completion_date(award), 
            'current_completion_date': get_current_completion_date(award), 
            'signed_date': award['relevantContractDates']['signedDate'],
            'agency_id': get_agency_id(award_id),
            'agency_name': get_agency_name(award_id),
            'obligated_amount': award['dollarValues']['obligatedAmount'],
            'annual_revenue': get_annual_revenue(award),
            'number_of_employees': get_number_of_employees(award),
            'last_modified_by': get_last_modified_by(award),
            'point_of_contact': get_point_of_contact(award),
            'reason_for_modification': get_reason_for_modification(award),
            'type_of_contract_pricing_name': get_contract_pricing_name(award),
            'type_of_contract_pricing_id': get_contract_pricing_id(award),
            'naics' : get_naics(award),
            'psc': get_psc(award),
        }                        
        return piid, record
    
    
    def update_contract(self, piid, records, v):
        records = sorted(records, key=lambda x: (x['mod_number'], x['transaction_number']))
        con, created = Contract.objects.get_or_create(piid=piid, vendor=v)
        total = 0 # amount obligated
        
        for mod in records:
            total += float(mod.get('obligated_amount'))
            
            con.date_signed = mod.get('signed_date') 
            con.completion_date = mod.get('current_completion_date') or mod.get('ultimate_completion_date')
            con.agency_id = mod.get('agency_id')
            con.agency_name = mod.get('agency_name')
            con.pricing_type = mod.get('type_of_contract_pricing_id')
            con.pricing_type_name = mod.get('type_of_contract_pricing_name')
            
            if mod.get('reason_for_modification') in ['X', 'E', 'F']:
                con.reason_for_modification = mod.get('reason_for_modification')
            else:
                if con.completion_date:
                    date_obj = datetime.strptime(con.completion_date, '%Y-%m-%d %H:%M:%S')
                    today = datetime.utcnow()
                    if date_obj:
                        if date_obj > today:
                            con.reason_for_modification = 'C2'
                        else:
                            con.reason_for_modification = 'C1'
            
            if mod.get('last_modified_by') and '@' in mod['last_modified_by'].lower():
                #only add if it's an actual email, make this a better regex
                con.last_modified_by = mod['last_modified_by']
            
            poc = poc_is_email(mod.get('point_of_contact'))    
            if poc:
                con.point_of_contact = poc
            
            #ADD NAICS -- need to add other naics as objects to use foreignkey
            con.PSC = mod.get('psc')
            con.NAICS = mod.get('naics')

            ar = mod.get('annual_revenue') or None
            ne = mod.get('number_of_employees') or None
            
            if ar:
                v.annual_revenue = int(ar)
            if ne:
                v.number_of_employees = int(ne)
        
        con.obligated_amount = total
        con.save()
        
        return records    
    
    
    def get_vendor_ids(self, starting_id=1):
        return Vendor.objects.filter(id__gte=starting_id).order_by('id').values_list('id', flat=True)
        
    
    def update_vendor(self, vid, load_to, options):
        logger = fpds_logger()
        
        vendor = Vendor.objects.get(id=vid)
        contracts = Contracts(logger=logger.debug)      
        load_info = last_load(vendor, options)
        
        if load_to <= load_info['load_date']: #already loaded more data than requested
            load_to = load_info['load_date'] + timedelta(weeks = int(options['weeks']))
        if load_to > self.date_now: #load_to can't be in the future
            load_to = self.date_now
        if load_info['load_date'] == self.date_now: #need to request at least one day
            load_info['load_date'] = load_info['load_date'] - timedelta(days = 1)
            
        if not (options['load_all'] and load_info['initialized']):
            print("[ {} ] - Updating vendor {} ({}) from {} to {}".format(vid, vendor.name, vendor.duns, load_info['load_date'], load_to))
            log_memory("Starting [ {} ] {} - {}".format(vid, vendor.name, vendor.duns))
            
            by_piid = {}
            
            v_index = 0
            contracts_processed = 0
            missing_modified = 0
            
            while True:
                v_con, v_index = contracts.get_page(v_index, int(options['count']), vendor_duns=vendor.duns, last_modified_date=[load_info['load_date'], load_to], _sleep=int(options['pause']))
            
                log_memory("Loading [ {} ] {} - {}".format(vid, vendor.name, vendor.duns))
                
                for vc in v_con:
                    piid, contract_record = self.init_contract(vc)
                    
                    if piid is None:
                        continue
                    
                    contracts_processed += 1
                    if not contract_record['modified_date']:
                        missing_modified += 1
                    
                    if piid in by_piid:
                        by_piid[piid].append(contract_record)
                    else:
                        by_piid[piid] = [contract_record, ]
                                
                if v_index == 0:
                    break
             
            for piid, records in by_piid.items():
                logger.debug("================{0}===Vendor {1}=================\n".format(piid, vendor.duns))
                logger.debug(contracts.pretty_print(by_piid[piid]))
        
                self.update_contract(piid, records, vendor)
                
            #save updates to annual revenue, number of employees
            vendor.save()
            create_load(vendor, load_to)
            
            print(" --- completed with: {} PIID(s), {} contract(s) processed".format(len(by_piid.keys()), contracts_processed))
            log_memory("Final [ {} ] {} - {}".format(vid, vendor.name, vendor.duns))
            log_data(vid, vendor.duns, vendor.name, load_info['load_date'], load_to, contracts_processed, len(by_piid.keys()), missing_modified)

    
    def update_vendors(self, vendor_ids, load_to, options):
        success = True
        
        log_data("Vendor ID", 
            "DUNS", 
            "Name", 
            "Start Date", 
            "End Date", 
            "Contracts", 
            "PIIDs", 
            "Missing Modified Timestamp"
        )
        
        for vid in vendor_ids:
            self.update_vendor(vid, load_to, options)
            
        return success
       

    def handle(self, *args, **options):
        print("-------BEGIN LOAD_FPDS PROCESS-------")
        log_memory('Start')
        
        signal.signal(signal.SIGSEGV, crash_handler) #catch segmentation faults
        
        try:
            #allow to start from a certain vendor
            vid = int(options['id'])
            
            vendor_ids = self.get_vendor_ids(vid)
            all_vendor_ids = self.get_vendor_ids() if vid > 1 else vendor_ids
            
            #process vendor contracts
            init_load(options)
            
            if options['load_all']:
                #repeat every incrementally until end if load_all
                first_date = self.date_now - timedelta(weeks=(52 * int(options['years'])))
                load_to = first_date
                
                while self.date_now > load_to: #while load_to is in the past
                    load_to = load_to + timedelta(weeks = int(options['weeks']))
                    if self.date_now < load_to: #load_to can't be in the future
                        load_to = self.date_now
                    
                    self.update_vendors(vendor_ids, load_to, options)
                    
                    #reset vendor ids so we start processing at the beginning again
                    vendor_ids = all_vendor_ids
            else:
                #load everything since last update
                self.update_vendors(vendor_ids, self.date_now, options)
            
        except Exception as e:
            display_error(e)
        
        print("-------END LOAD_FPDS PROCESS-------")
        log_memory('End')
