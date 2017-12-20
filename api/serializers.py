from rest_framework import serializers, pagination
from vendors.models import Vendor, Pool, Naics, SetAside, SamLoad
from contract.models import Contract, FPDSLoad

class SetAsideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetAside
        fields = ('code', 'abbreviation')


class NaicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Naics
        fields = ('code', 'description', 'short_code')


class PoolSerializer(serializers.ModelSerializer):
    naics = NaicsSerializer(many=True)
    class Meta:
        model = Pool
        fields = ('id', 'name', 'number', 'vehicle', 'naics', 'threshold')


class ShortPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pool
        fields = ('id', 'name', 'number', 'vehicle')


class VendorSerializer(serializers.ModelSerializer):
    setasides = SetAsideSerializer(many=True)
    pools = ShortPoolSerializer(many=True)
    class Meta:
        model = Vendor
        fields = ('name', 'duns', 'duns_4', 'cage', 'sam_address', 'sam_citystate', 'pm_name', 'pm_email', 'pm_phone', 'pools', 'setasides', 'sam_status', 'sam_expiration_date', 'sam_activation_date', 'sam_exclusion', 'sam_url', 'annual_revenue', 'number_of_employees')


class ShortVendorSerializer(serializers.ModelSerializer):
    setasides = SetAsideSerializer(many=True)
    contracts_in_naics = serializers.SerializerMethodField('get_contracts_in_naics')    

    class Meta:
        model = Vendor
        fields = ('name', 'duns', 'duns_4', 'sam_address', 'sam_citystate',
            'setasides', 'sam_status', 'sam_exclusion', 'sam_url', 'contracts_in_naics')

    def get_contracts_in_naics(self, obj):
        return Contract.objects.filter(NAICS=self.context['naics'].code, vendor=obj).count()

class ContractSerializer(serializers.ModelSerializer):
    
    pricing_type = serializers.Field(source='get_pricing_type_display')
    piid = serializers.SerializerMethodField('split_piid')
    status = serializers.SerializerMethodField('get_status')
    class Meta:
        model = Contract
        fields = ('piid', 'agency_name', 'NAICS', 'date_signed', 'status', 'obligated_amount', 'point_of_contact', 'pricing_type')
        
    def split_piid(self, obj):
        if '_' in obj.piid:
            return obj.piid.split('_')[1]
        return obj.piid

    def get_status(self, obj):
        return obj.get_reason_for_modification_display()

class PaginatedContractSerializer(pagination.PaginationSerializer):
    
    class Meta:
        object_serializer_class = ContractSerializer

class Metadata(object):
    def __init__(self):
        sam_md = SamLoad.objects.all().order_by('-sam_load')
        fpds_md = FPDSLoad.objects.all().order_by('-load_date')
        if len(sam_md) > 0:
            self.sam_load_date = sam_md[0].sam_load
        else: 
            self.sam_load_date = None
        if len(fpds_md) > 0:
            self.fpds_load_date = fpds_md[0].load_date
        else:
            self.fpds_load_date = None


class MetadataSerializer(serializers.Serializer):
    sam_load_date = serializers.DateField()
    fpds_load_date = serializers.DateField()
    

