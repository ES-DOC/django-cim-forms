####################
#   ES-DOC CIM Questionnaire
#   Copyright (c) 2017 ES-DOC. All rights reserved.
#
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################


"""
.. module:: apps

defines the code to run once-and-only-once when the application is 1st loaded
using a custom class to ensure all of my custom signals are picked up

"""

from django.apps import AppConfig
from django.conf import settings
from lxml import etree as et
import json

from Q.questionnaire import APP_LABEL


class QConfig(AppConfig):
    name = APP_LABEL
    verbose_name = 'Questionnaire Application'

    def ready(self):
        from Q.questionnaire.q_constants import PROFANITIES_LIST, QCONFIG_SCHEMA

        # don't want naughty words in the questionnaire...
        with open(settings.STATIC_ROOT + APP_LABEL + "/xml/profanities.xml", 'r') as file:
            words = et.parse(file).xpath("//word", smart_strings=False)
            for word in words:
                PROFANITIES_LIST.append(word.text)
        file.closed

        # access the ontology schema from w/in the questionnaire...
        with open(settings.STATIC_ROOT + APP_LABEL + "/schemas/qconfig_ontology.schema.json", 'r') as file:
            QCONFIG_SCHEMA.update(json.load(file))
        file.closed

        # setup any extra signal-processing...
        # (as per https://docs.djangoproject.com/en/1.8/topics/signals/#connecting-receiver-functions)
        from Q.questionnaire.signals import *

