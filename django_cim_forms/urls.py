#    Django-CIM-Forms
#    Copyright (c) 2012 CoG. All rights reserved.
#
#    Developed by: Earth System CoG
#    University of Colorado, Boulder
#    http://cires.colorado.edu/
#
#    This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].

import django_cim_forms.feeds
from django.conf.urls.defaults import patterns, include, url

from models import *
from feeds import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # the index page (doesn't do anything yet)...
    url(r'^$', 'django_cim_forms.views.index'),

    # ajax calls to server
    url(r'^add_form/$', 'django_cim_forms.views.add_form'),
    url(r'^get_content/$', 'django_cim_forms.views.get_content'),

    # cvs...
    url(r'^cv/(?P<cv_name>\w+)/$', 'django_cim_forms.views_cv.detail'),

    # ATOM feed...
    url(r'^feed/(?P<app_name>[^/]+)/(?P<model_type>[^/]+)/$', MetadataFeed()),
    url(r'^feed/(?P<app_name>[^/]+)/$', MetadataFeed()),

    # these forms can be generated for _any_ model in _any_ application...
    url(r'^(?P<app_name>[^/]+)/(?P<model_name>[^/]+)/$', 'django_cim_forms.views.detail'),
    url(r'^(?P<app_name>[^/]+)/(?P<model_name>[^/]+)/(?P<model_id>\d+)/$', 'django_cim_forms.views.detail'),

    # TEMPORARY URL FOR GENERATING CIM XML
    url(r'^xml/(?P<app_name>[^/]+)/(?P<model_name>[^/]+)/$', 'django_cim_forms.views.serialize', {"format" : "xml"}),
    url(r'^xml/(?P<app_name>[^/]+)/(?P<model_name>[^/]+)/(?P<model_id>\d+)/$', 'django_cim_forms.views.serialize', {"format" : "xml"}),

)
