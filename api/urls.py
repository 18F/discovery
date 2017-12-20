from django.conf.urls import patterns, include, url
from django.views.decorators.cache import cache_page
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = patterns('',
    url(r'^vendors/$', cache_page(60*60*12)(views.ListVendors.as_view())),
    url(r'^vendor/(?P<duns>\w+)', views.GetVendor.as_view()),
    url(r'^naics/$', views.ListNaics.as_view()),
    url(r'^contracts/$', views.ListContracts.as_view()),
    url(r'^metadata/$', views.MetadataView.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
