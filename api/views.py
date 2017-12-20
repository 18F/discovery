from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db.models import Count

from rest_framework.response import Response
from rest_framework.views import APIView

from contract.models import Contract
from vendors.models import Vendor, Naics, SetAside, SamLoad, Pool
from api.serializers import VendorSerializer, NaicsSerializer, PoolSerializer, ShortVendorSerializer, ContractSerializer, PaginatedContractSerializer, Metadata, MetadataSerializer, ShortPoolSerializer


class GetVendor(APIView):
    """
    This endpoint returns a single vendor by their 9 digit DUNS number. DUNS numbers can be looked up in the [System for Award Management](https://www.sam.gov) by vendor name.
    ---
    GET:
        parameters:
          - name: duns
            description: a nine digit DUNS number that uniquely identifies the vendor (required)
            required: true
            type: string
            paramType: path
    """
    def get(self, request, duns, format=None):
        vendor = Vendor.objects.get(duns=duns) 
        return Response(VendorSerializer(vendor).data) 

class ListVendors(APIView):
    """
    This endpoint returns a list of vendors filtered by a NAICS code. The NAICS code maps to an OASIS pool and is used to retrieve vendors in that pool only.

    OASIS pools are groupings of NAICS codes that have the same small business size standard. Because contracts solicited to OASIS vendors can only be issued to one pool, much of the data is presented as part of a pool grouping. Using the NAICS code is a shortcut, so that you don't have to explicitly map the NAICS code to a pool in OASIS yourself.
    
    Vendors can also be filtered by a particular setaside. Valid values for the setasides are two-character codes which include:

    * A6 (8(a))
    * XX (Hubzone)
    * QF (service disabled veteran owned)
    * A2 (women owned)
    * A5 (veteran owned)
    * 27 (small disadvantaged business).

    ---
    GET:
        parameters:
          - name: naics
            paramType: query
            description: a six digit NAICS code (required)
            required: true
            type: string
          - name: setasides  
            paramType: query
            allowMultiple: true
            description: a comma delimited list of two character setaside codes to filter by.  Ex. setasides=A6,A5  will filter by 8a and veteran owned business.
            required: false
            type: string
          - name: vehicle
            paramType: query
            description: Choices are either oasis or oasissb. Will filter vendors by their presence in either the OASIS unrestricted vehicle or the OASIS Small Business vehicle.
            required: false
            type: string

    """
    def get(self, request, format=None):

        try: 
            naics =  Naics.objects.get(short_code=request.QUERY_PARAMS.get('naics'))
            vehicle = request.QUERY_PARAMS.get('vehicle', None)
            if vehicle:
                pool = [Pool.objects.get(naics=naics, vehicle=vehicle.upper()), ]
            else:
                pool = Pool.objects.filter(naics=naics)

            setasides = request.QUERY_PARAMS.get('setasides', None)
            if setasides:
                setasides = setasides.split(',')
            

            sam_load_results = SamLoad.objects.all().order_by('-sam_load')[:1]
            sam_load = sam_load_results[0].sam_load if sam_load_results else None

            v_serializer = ShortVendorSerializer(self.get_queryset(pool, setasides, naics), many=True, context={'naics': naics})
            v_serializer.data.sort(key=lambda k: k['contracts_in_naics'], reverse=True)
            p_serializer = ShortPoolSerializer(pool)

            return  Response({ 'num_results': len(v_serializer.data), 'pool' : p_serializer.data , 'sam_load':sam_load, 'results': v_serializer.data } )

        except Naics.DoesNotExist:
            return HttpResponseBadRequest("You must provide a valid naics code that maps to an OASIS pool")

    def get_queryset(self, pool, setasides, naics):
        vendors = Vendor.objects.filter(pools__in=pool)
        if setasides:
            for sa in SetAside.objects.filter(code__in=setasides):
                vendors = vendors.filter(setasides=sa)

        return vendors


class ListNaics(APIView):
    """
        This endpoint lists all of the NAICS codes that are relevant to the OASIS family of vehicles. It takes no parameters.
    """
    def get(self, request, format=None):
        serializer = NaicsSerializer(self.get_queryset(), many=True)
        return Response({'num_results': len(serializer.data), 'results': serializer.data})

    def get_queryset(self):
        codes = Naics.objects.all()

        #filters
        q = self.request.QUERY_PARAMS.get('q', None)

        codes = Naics.objects.all().order_by('description')

        if q:
            codes = codes.filter(description__icontains=q)

        return codes

class ListContracts(APIView):
    """ 
    
    This endpoint returns contract history from FPDS for a specific vendor. The vendor's DUNS number is a required parameter. You can also filter contracts by their NAICS code to find contracts relevant to a particular category. 
    
    ---
    GET:
        parameters:
          - name: duns
            description: A 9-digit DUNS number that uniquely identifies a vendor (required).
            required: true
            type: string
            paramType: query
          - name: naics
            description: a six digit NAICS code used to filter by contracts with a certain NAICS
            type: string
            required: false
            paramType: query
          - name: sort
            description: a field to sort on. Choices are date, status, agency, and amount
            type: string
            required: false
            paramType: query
          - name: direction
            description: The sort direction of the results. Choices are asc or desc.
            type: string
            required: false
            paramType: query
          - name: page
            description: the page to start on. Results are paginated in increments of 100. Begins at page=1.
            required: false
            paramType: query

    """
    def get(self, request, format=None):
        contracts = self.get_queryset()

        if contracts == 1:
            return HttpResponseBadRequest("You must provide a vendor DUNS to retrieve contracts.")

        else:
            paginator = Paginator(contracts, 100)
            page = request.QUERY_PARAMS.get('page', 1)
            contracts = paginator.page(page)
            
            serializer = PaginatedContractSerializer(contracts, context={'request': request})
            serializer.data['num_results'] = serializer.data['count']
            del serializer.data['count']

            return Response(serializer.data)

    def get_queryset(self):
        
        duns = self.request.QUERY_PARAMS.get('duns', None)
        naics = self.request.QUERY_PARAMS.get('naics', None)
        dir_map = { 'desc': '-', 'asc': '' }
        sort_map = { 'date': 'date_signed', 'status': 'reason_for_modification', 'agency': 'agency_name', 'amount': 'obligated_amount'}

        if not duns:
            return 1

        vendor = Vendor.objects.get(duns=duns)
        sort = self.request.QUERY_PARAMS.get('sort', None)
        direction = self.request.QUERY_PARAMS.get('direction', None)

        if sort and not direction:
            direction = 'desc'
        
        if not sort or sort not in sort_map:
            sort = 'date'
            direction = 'desc'

        contracts = Contract.objects.filter(vendor=vendor).order_by(dir_map[direction] + sort_map[sort])
        
        if naics:
            #contracts = contracts.filter(NAICS=Naics.objects.filter(code=naics)[0])
            contracts = contracts.filter(NAICS=naics)  #change to above when naics loaded right

        return contracts

class MetadataView(APIView):
    """
        This endpoint returns metadata for the most recent data loads of SAM and FPDS data. It takes no parameters.
    """
    def get(self, request, format=None):
       mds = MetadataSerializer(Metadata())
       return Response(mds.data)
        



