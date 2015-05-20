####################
#   ES-DOC CIM Questionnaire
#   Copyright (c) 2014 ES-DOC. All rights reserved.
#
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################

__author__ = "allyn.treshansky"
__date__ = "Dec 01, 2014 3:00:00 PM"

"""
.. module:: test_middleware

Tests for custom middleware.  This includes dynamic_sites
"""

from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.conf import settings
from django.contrib.sites.models import Site, get_current_site
from CIM_Questionnaire.questionnaire.middleware.dynamic_sites import DynamicSitesMiddleware
from CIM_Questionnaire.questionnaire.tests.test_base import TestQuestionnaireBase


class Test(TestQuestionnaireBase):

    def setUp(self):
        # no need for any questionnaire-specific stuff
        #super(Test,self).setUp()
        pass

    def tearDown(self):
        # no need for any questionnaire-specific stuff
        #super(Test,self).tearDown()
        pass

    def test_dynamic_sites(self):

        # just testing middleware; don't need a _real_ request...
        factory = RequestFactory()
        test_request = factory.get(reverse("questionnaire_test"))

        dynamic_sites_middleware = DynamicSitesMiddleware()

        dynamic_sites_middleware.process_request(test_request)

        current_site = get_current_site(test_request)
        example_site = Site.objects.get(pk=settings.SITE_ID)

        self.assertEqual(current_site, example_site)

        test_site = Site(name="test_site", domain="testserver")
        test_site.save()

        dynamic_sites_middleware.process_request(test_request)

        current_site = get_current_site(test_request)

        self.assertEqual(current_site, test_site)
        self.assertNotEqual(current_site, example_site)