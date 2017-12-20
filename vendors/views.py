from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import TemplateView
from vendors.models import Vendor, Pool, Naics, SetAside
from contract.models import Contract
import csv
import os.path
from titlecase import titlecase

class VendorView(TemplateView):
    pdf_dir = 'mirage_site/static/mirage_site/capability_statements/'
    static_pdf_dir = 'mirage_site/capability_statements/'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        duns = context['vendor_duns']
        capability_statement = self.has_statement(duns)
        context['has_capability_statement'] = capability_statement
        if capability_statement:
            context['capability_statement_url'] = self.get_pdf_path(duns, self.static_pdf_dir)
        return context

    def has_statement(self, duns):
        if os.path.isfile(self.get_pdf_path(duns, self.pdf_dir)):
            return True
        return False

    def get_pdf_path(self, duns, path):
        pdf_path = path
        pdf_path += duns
        pdf_path += '.pdf'
        return pdf_path


def pool_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search_results.csv"'
    writer = csv.writer(response)
    #write results
    vendors = Vendor.objects.all()
    setasides_all = SetAside.objects.all().order_by('far_order')
    filter_text = []
    #naics
    naics = Naics.objects.get(short_code=request.GET['naics-code'])
    vehicle = request.GET['vehicle'].upper()
    pool = Pool.objects.get(naics=naics, vehicle=vehicle)
    vendors = vendors.filter(pools=pool)
    filter_text.append("NAICS code {0}".format(naics))

    #setasides
    if 'setasides' in request.GET:
        setasides = request.GET.getlist('setasides')[0].split(',')
        setaside_objs = SetAside.objects.filter(code__in=setasides)
        for sobj in setaside_objs:
            vendors = vendors.filter(setasides=sobj)

        filter_text.append("Set Aside filters: {0}".format(", ".join(setasides)))

    writer.writerow(("Vehicle: " + vehicle,))
    writer.writerow(("Search Results: {0} Vendors".format(len(vendors)),))
    writer.writerow(filter_text)

    writer.writerow(('',))
    header_row = ['Vendor', 'Location', 'No. of Contracts',]
    header_row.extend([sa_obj.abbreviation for sa_obj in setasides_all])
    writer.writerow(header_row)

    lines = []

    for v in vendors:
        setaside_list = []
        for sa in setasides_all:
            if sa in v.setasides.all():
                setaside_list.append('X')
            else:
                setaside_list.append('')

        v_row = [v.name, v.sam_citystate, Contract.objects.filter(NAICS=naics.code, vendor=v).count()]
        v_row.extend(setaside_list)
        lines.append(v_row)

    lines.sort(key=lambda x: x[2], reverse=True)
    for line in lines:
        writer.writerow(line)

    return response


def vendor_csv(request, vendor_duns):
    vendor = Vendor.objects.get(duns=vendor_duns)
    setasides = SetAside.objects.all().order_by('far_order')

    naics = request.GET.get('naics-code', None)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search_results.csv"'
    writer = csv.writer(response)

    writer.writerow((vendor.name,))
    writer.writerow(('SAM registration expires: ', vendor.sam_expiration_date.strftime("%m/%d/%Y")))
    writer.writerow(('', ))
    writer.writerow([sa_obj.abbreviation for sa_obj in setasides])

    vendor_sa = []
    for sa in  setasides:
        if sa in vendor.setasides.all():
            vendor_sa.append('X')
        else:
            vendor_sa.append('')

    writer.writerow(vendor_sa)
    writer.writerow(('', ))
    writer.writerow(('DUNS', vendor.duns, '', 'Address:', titlecase(vendor.sam_address)))
    writer.writerow(('CAGE Code', vendor.cage, '', '',  titlecase(vendor.sam_citystate[0:vendor.sam_citystate.index(',') + 1]) + vendor.sam_citystate[vendor.sam_citystate.index(',') + 1:]))
    writer.writerow(('Employees', vendor.number_of_employees, '', 'OASIS POC:', vendor.pm_name))
    writer.writerow(('Annual Revenue', vendor.annual_revenue, '', '', vendor.pm_phone))
    writer.writerow(('', '', '', '', vendor.pm_email.lower()))
    writer.writerow(('', ))
    if naics:
        writer.writerow(('This vendor\'s contract history for NAICS {0}'.format(naics), ))
    else:
        writer.writerow(('This vendor\'s contract history for all contracts', ))

    writer.writerow(('Date Signed', 'PIID', 'Agency', 'Type', 'Value ($)', 'Email POC', 'Status'))

    if naics:
        contracts = Contract.objects.filter(vendor=vendor, NAICS=naics).order_by('-date_signed')
    else:
        contracts = Contract.objects.filter(vendor=vendor).order_by('-date_signed')
    for c in contracts:
        if '_' in c.piid:
            piid = c.piid.split('_')[1]
        else:
            piid = c.piid
        writer.writerow((c.date_signed.strftime("%m/%d/%Y"), piid, titlecase(c.agency_name), c.get_pricing_type_display(), c.obligated_amount, (c.point_of_contact or "").lower(), c.get_reason_for_modification_display()))

    return response
