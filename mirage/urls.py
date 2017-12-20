from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles import views
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

from api import urls as api_urls
from vendors.views import VendorView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^api/', include(api_urls)),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^results/$', TemplateView.as_view(template_name='pool.html')),
    url(r'^results/csv', 'vendors.views.pool_csv', name="pool-csv"),
    url(r'^vendor/(?P<vendor_duns>\w+)/$', VendorView.as_view(template_name='vendor.html')),
    url(r'^vendor/(?P<vendor_duns>\w+)/csv/$', 'vendors.views.vendor_csv', name="vendor-csv"),   
    url(r'^admin/', include(admin.site.urls)),    
)

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
