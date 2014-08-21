from django.conf.urls import patterns, include, url
from  webapp import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'webapp.views.index'),
    url(r'^login$', 'webapp.views.login'),
    url(r'^webadmin$', 'webapp.views.webadmin'),
    url(r'^settings$', 'webapp.views.settings'),
    url(r'^saveurl$', 'webapp.views.saveurl'),
    url(r'^sitemapurlview$', 'webapp.views.sitemapurlview'),
    url(r'^logout$', 'webapp.views.logout'),
    url(r'^executescript$', 'webapp.views.executeScript'),

    # url(r'^DataParsingWeb/', include('DataParsingWeb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
