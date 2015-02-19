
####################
#   CIM_Questionnaire
#   Copyright (c) 2013 CoG. All rights reserved.
#
#   Developed by: Earth System CoG
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################

__author__ = "allyn.treshansky"
__date__ = "Dec 9, 2013 4:33:11 PM"

"""
.. module:: utils

Utility fns used by all modules
"""

from django.core.exceptions import ValidationError

from django.forms import model_to_dict
from django.forms.formsets import TOTAL_FORM_COUNT, INITIAL_FORM_COUNT, MAX_NUM_FORM_COUNT
from django.forms.models import BaseModelFormSet, BaseInlineFormSet
from django.forms.fields import MultiValueField

import re
import urllib

from django.core import serializers
from lxml import etree as et


def xpath_fix(node, xpath):
    """Helper function to address lxml smart strings memory leakage issue.

    :param lxml.etree.Element node: An xml element.
    :param str xpath: An xpath statement.

    :returns: Results of xpath expression evaluation.
    :rtype: list or lxml.etree.Element

    """
    if node is None:
        raise ValueError("Xpath expression cannot be evaluated against a null XML node.")
    if xpath is None or not len(xpath):
        raise ValueError("Xpath expression is invalid.")

    return node.xpath(xpath, smart_strings=False)


def get_tag_without_namespace(node):
    """
    gets tag from lxml element but w/out embedded namespace
    (and w/out dealing w/ all the complexity of namespace managers)
    this allows me to perform comparisons (in tests)
    :param node: lxml element node
    :return: string tag
    """
    full_tag = node.tag
    return full_tag.split("}")[-1]


def get_attribute_without_namespace(node,attribute_name):
    """
    gets tag from lxml element but w/out embedded namespace
    (and w/out dealing w/ all the complexity of namespace managers)
    this allows me to perform comparisons (in tests)
    :param node: lxml element node
    :param attribute_name: name of attribute to search for
    :return: attribute value (or None if not found)
    """
    attributes = node.attrib
    for key, value in attributes.iteritems():
        key_without_namespace = key.split("}")[-1]
        if attribute_name == key_without_namespace:
            return value
    return None

#############
# constants #
#############

APP_LABEL = "questionnaire"

LIL_STRING = 128
SMALL_STRING = 256
BIG_STRING = 512
HUGE_STRING = 1024

#: a serializer to use throughout the app; defined once to avoid too many fn calls
JSON_SERIALIZER = serializers.get_serializer("json")()

CIM_NAMESPACES = [
    "xsi",
    "gml",
    "xlink",
    "gco",
    "gmd",
]

CIM_MODEL_STEREOTYPES = [
    "document",
]

CIM_PROPERTY_STEREOTYPES = [
    "attribute",    # should be serialized as an XML attribute rather than element
    "document",     # should be included w/ the "documentProperties" of a model, rather than the "standardProperties"
]

#: the set of document types recognized by the questionnaire
CIM_DOCUMENT_TYPES = [
    "modelcomponent",
    "statisticalmodelcomponent",
    "experiment",
]

#: the set of document types that can be fully processed (ie: end-to-end) by the questionnaire
SUPPORTED_DOCUMENTS = [
    "modelcomponent",
    "statisticalmodelcomponent",
]

#: keys to use for cases where a model has no vocabulary, or where it is the root component of several vocabularies
DEFAULT_VOCABULARY_KEY = "DEFAULT_VOCABULARY"
DEFAULT_COMPONENT_KEY = "DEFAULT_COMPONENT"

MANAGEMENT_FORM_FIELD_NAMES = [
    TOTAL_FORM_COUNT,
    INITIAL_FORM_COUNT,
    MAX_NUM_FORM_COUNT
]

##############
# assertions #
##############


def assert_no_string_nones(dct):
    """
    Asserts no string representations of NoneType (i.e. ``'None'``) are present in the dictionary.

    :param dict dct:
    """
    for k, v in dct.iteritems():
        if v == 'None':
            msg = 'The key "{0}" has value equal to "None" string.'.format(k)
            raise AssertionError(msg)


##################
# error handling #
##################

class QuestionnaireError(Exception):
    """
    Custom exception class

    .. note:: As the CIM Questionnaire is a web-application, it often makes more sense to use the :func`questionnaire.questionnaire_error` view with an appropriate message instead of raising an explicit QuestionnaireError

    """

    def __init__(self,msg='unspecified metadata error'):
        self.msg = msg
        
    def __str__(self):
        return "QuestionnaireError: " + self.msg

##############
# validators #
##############


def validate_no_spaces(value):
    """
    validator function to use with charFields;
    ensures there is no whitespace in the field
    """

    # TODO: WHY DOESN'T THIS WORK?
    #if re.match('\s',value):
    if ' ' in value:
        raise ValidationError(u"Value may not contain spaces.")

BAD_CHARS = "\ / < > % # % { } [ ] $ |"
BAD_CHARS_REGEX = "[\\\/<>&#%{}\[\]\$\|]"
BAD_CHARS_LIST = ", ".join(BAD_CHARS.split(' '))


def validate_no_bad_chars(value):
    """
    validator function to use with CharFields;
    ensures none of the above "BAD_CHARS" exist in the field
    :param value:
    :return:
    """
    if re.search(BAD_CHARS_REGEX, value):
        raise ValidationError(u"Value may not contain any of the following characters: '%s'" % (BAD_CHARS))


def validate_password(value):
    # passwords have a minimum length...
    PASSWORD_LENGTH = 6
    if len(value) < PASSWORD_LENGTH:
        raise ValidationError("A password must contain at least %s characters" % PASSWORD_LENGTH)
    # and a mixture of letters and non-letters...
    if not (re.match(r'^.*[A-Za-z]', value) and
            re.match(r'^.*[0-9!@#$%^&*()\-_=+.,?:;></\\\[\]\{\}]', value)):
        raise ValidationError("A password must contain both letters and non-letters")


def validate_no_reserved_words(value):
    """
    validator function to use with charFields;
    ensures specified words are not used
    """
    
    RESERVED_WORDS = [
        # cannot have projects w/ these names, else the URLs won't make sense...
        "admin", "static", "site_media",
        "index", "login", "logout", "register", "user",
        "questionnaire", "mindmaps",
        "customize", "edit", "view", "help",
        "ajax", "api",
        "test",
    ]

    if value.lower() in RESERVED_WORDS:
        raise ValidationError(u"'%s' is a reserved word" % value)


def validate_file_extension(value,valid_extensions):
    """
    Validator function to use with fileFields.
    Ensures the file attemping to be uploaded matches a set of extensions.
    :param value: file being validated
    :param valid_extensions: list of valid extensions
    """
    if not value.name.split(".")[-1] in valid_extensions:
        raise ValidationError(u'Invalid File Extension')


def validate_file_schema(value,schema_path):
    """
    validator function to use with fileFields;
    validates a file against an XML Schema.
    """
    
    contents = et.parse(value)

    try:
        schema = et.XMLSchema(et.parse(schema_path))
    except IOError:
        msg = "Unable to find suitable schema to validate file against (%s)" % schema_path
        raise ValidationError(msg)

    try:
        schema.assertValid(contents)
    except et.DocumentInvalid, e:
        msg = "Invalid File Contents: %s" % str(e)
        raise ValidationError(msg)

###########################
# form/field manipulation #
###########################


def get_form_by_field(formset,field_name,field_value):
    """
    returns the 1st form in a formset whose specified field has the specified value
    :param formset: formset to check
    :param field_name: name of field to check
    :parem field_value: value of field to check
    :return: matching form or None
    """
    for form in formset:
        if form.get_current_field_value(field_name) == field_value:
            return form
    return None


def get_forms_by_field(formset,field_name,field_value):
    """
    returns all forms in a formset whose specified field has the specified value
    :param formset: formset to check
    :param field_name: name of field to check
    :param field_value: value of field to check
    :return: list of matching forms
    """
    forms = []
    for form in formset:
        if form.get_current_field_value(field_name) == field_value:
            forms.append(form)
    return forms


def get_form_by_prefix(formset, prefix):
    """
    returns the form in a formset w/ a prefix of prefix
    :param formset: formset to check
    :param prefix: value of prefix to look for
    :return: matching form or none
    """
    for form in formset:
        if form.prefix == prefix:
            return form
    return None


def remove_form_errors(form):
    form.errors["__all__"] = form.error_class()
    for field in form.fields:
        form.errors[field] = form.error_class()


def set_field_widget_attributes(field,widget_attributes):
    for (key,value) in widget_attributes.iteritems():
        field.widget.attrs[key] = value


def update_field_widget_attributes(field,widget_attributes):
    """
    rather than overriding an attribute, this fn appends it to any existing ones
    as with class='old_class new_class'
    """
    for (key,value) in widget_attributes.iteritems():
        try:
            current_attributes = field.widget.attrs[key]
            field.widget.attrs[key] = "%s %s" % (current_attributes,value)
        except KeyError:
            field.widget.attrs[key] = value


# THIS TOOK A WHILE TO FIGURE OUT
# model_to_dict IGNORES FOREIGNKEY FIELDS & MANYTOMANY FIELDS
# THIS FN WILL UPDATE THE MODEL_DATA ACCORDING TO THE "update_fields" ARGUMENT
def get_initial_data(model, update_fields={}):
    _dict = model_to_dict(model)
    _dict.update(update_fields)
    for key, value in _dict.iteritems():
        if isinstance(value, tuple):
            # TODO: SOMETIMES THIS RETURNS A TUPLE INSTEAD OF A STRING, NOT SURE WHY
            _dict[key] = value[0]
    return _dict


# TODO: REPLACE THE ABOVE FN W/ THIS FN IN CODE
def model_to_data(model, exclude=[], include={}):
    model_data = model_to_dict(model)
    model_data.update(include)
    model_data_copy = model_data.copy()
    for key, value in model_data_copy.iteritems():
        if key in exclude:
            model_data.pop(key)
    return model_data


def model_to_data_old(model, exclude=[], include={}):
    """
    serializes model to dictionary (like get_initial_data) but follows fk & m2m fields
    """
    model_data = {}
    for field in model._meta.fields:
        field_name = field.name
        if field_name not in exclude:
            if field_name in include:
                model_data[field_name] = include[field_name]
            else:
                model_data[field_name] = getattr(model,field_name)
    return model_data


def get_data_from_form(form, existing_data={}):

    data = {}

    form_prefix = form.prefix
    for field_name, field in form.fields.iteritems():
        try:
            if field_name in existing_data:
                field_value = existing_data[field_name]
            else:
                field_value = form.get_current_field_value(field_name)
        except:
            if field_name in existing_data:
                field_value = existing_data[field_name]
            else:
                field_value = form.get_current_field_value(field_name)

        if form_prefix:
            field_key = u"%s-%s" % (form_prefix, field_name)
        else:
            field_key = u"%s" % field_name

        # this checks if I am dealing w/ a MultiValueField
        # Django automatically separates this into its constituent fields when gathering data via POST
        # this fn has to do this manually b/c it's usually called outside of the standard GET/POST view paradigm
        # (ie: via the testing framework)
        # TODO: AM I SURE THAT THE FIELD_VALUE WILL ALWAYS BE A LIST AND NOT A TUPLE?
        if isinstance(field, MultiValueField) and isinstance(field_value, list):
            for i, v in enumerate(field_value):
                data[u"%s_%s" % (field_key, i)] = v
        else:
            # obviously, a non-MultiValueField is much easier
            data[field_key] = field_value

    return data


def get_data_from_formset(formset, existing_data={}):
    data = {}
    current_data = {}

    for form in formset:
        current_data.clear()
        current_data.update(existing_data)

        # in general, this is only needed when calling this fn outside of the interface
        # ie: in the testing framework
        # (the hidden pk & fk fields do not get passed in via the queryset for existing model formsets)
        pk_field_name = formset.model._meta.pk.name
        current_data[pk_field_name] = form.fields[pk_field_name].initial
        if isinstance(formset, BaseInlineFormSet):
            fk_field_name = formset.fk.name
            current_data[fk_field_name] = form.fields[fk_field_name].initial

        if formset.can_delete:
            current_data["DELETE"] = False

        form_data = get_data_from_form(form, current_data)
        data.update(form_data)

    formset_prefix = formset.prefix
    if formset_prefix:
        total_forms_key = u"%s-TOTAL_FORMS" % formset_prefix
        initial_forms_key = u"%s-INITIAL_FORMS" % formset_prefix
    else:
        total_forms_key = u"TOTAL_FORMS"
        initial_forms_key = u"INITIAL_FORMS"
    data[total_forms_key] = formset.total_form_count()
    data[initial_forms_key] = formset.initial_form_count()

    return data


def remove_non_loaded_data(data, loaded_prefixes, management_form_prefix):
    # it is much easier to work out which forms w/in a formset are loaded than which are non-loaded
    # so even though this removes the non-loaded data, I pass it the loaded prefixes
    data_copy = data.copy()
    for key, value in data.iteritems():
        if any(key == u"%s-%s" % (management_form_prefix, management_form_field_name) for management_form_field_name in MANAGEMENT_FORM_FIELD_NAMES):
            # but don't get rid of management form stuff
            continue
        if not any(key.startswith(loaded_key) for loaded_key in loaded_prefixes):
            # if this item doesn't begin w/ one of the loaded_prefixes, then it must be unloaded
            # which means it shouldn't appear in the POST
            data_copy.pop(key)
    return data_copy


def remove_null_data(data):
    data_copy = data.copy()
    for key, value in data.iteritems():
        if value == None:
            data_copy.pop(key)
    return data_copy


#######################
# string manipulation #
#######################


def remove_spaces_and_linebreaks(str):
    return ' '.join(str.split())

####################
# url manipulation #
####################


def add_parameters_to_url(path, **kwargs):
    """
    slightly less error-prone way to add GET parameters to the url
    """
    return path + "?" + urllib.urlencode(kwargs)

####################
# enumerated types #
####################


class EnumeratedType(object):

    def __init__(self, type=None, name=None, cls=None):
        self._type = type  # the key of this type
        self._name = name  # the pretty name of this type
        self._class = cls  # the Python class used by this type (not always relevant)

    def getType(self):
        return self._type

    def getName(self):
        return self._name

    def getClass(self):
        return self._class

    def __unicode__(self):
        name = u'%s' % self._type
        return name

    # comparisons are made via the _type attribute...
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # comparing two enumeratedtypes
            return self.getType() == other.getType()
        else:
            # comparing an enumeratedtype with a string
            return self.getType() == other

    def __ne__(self, other):
        return not self.__eq__(other)


class EnumeratedTypeError(Exception):
    def __init__(self,msg='invalid enumerated type'):
        self.msg = msg
    def __str__(self):
        return "EnumeratedTypeError: " + self.msg


# this used to be based on deque to preserve FIFO order...
# but since I changed to adding fields to this list as needed in class's __init__() fn,
# that doesn't make much sense; so I'm basing it on a simple list
# and adding an ordering fn
class EnumeratedTypeList(list):

    def __getattr__(self, type):
        for et in self:
            if et.getType() == type:
                return et
        raise EnumeratedTypeError("unable to find %s" % str(type))

    def get(self, type):
        for et in self:
            if et.getType() == type:
                return et
        return None
    
    # a method for sorting these lists
    # order is a list of EnumeratatedType._types
    @classmethod
    def comparator(cls, et, etOrderList):
        etType = et.getType()
        if etType in etOrderList:
            # if the type being compared is in the orderList, return it's position
            return etOrderList.index(etType)
        # otherwise return a value greater than the last position of the orderList
        return len(etOrderList)+1

#################
# FuzzyIntegers #
#################


# this is a very clever idea for comparing integers against min/max bounds
# credit goes to http://lukeplant.me.uk/blog/posts/fuzzy-testing-with-assertnumqueries/

class FuzzyInt(int):

    def __new__(cls, lowest, highest):
        obj = super(FuzzyInt, cls).__new__(cls, highest)
        obj.lowest = lowest
        obj.highest = highest
        return obj

    def __eq__(self, other):
        return other >= self.lowest and other <= self.highest

    def __repr__(self):
        return "[%d..%d]" % (self.lowest, self.highest)

#####################################
# deal w/ hierarchies of components #
#####################################

from mptt.fields import TreeForeignKey


# TODO: I DON'T THINK THIS DECORATOR IS BEING USED ANYMORE
def hierarchical(cls):
    TreeForeignKey(cls, null=True, blank=True, related_name='bens_children').contribute_to_class(cls,'parent')
    #ForeignKey(cls, null=True, blank=True,related_name="children").contribute_to_class(cls,'parent')
    return cls

######################################
# removes duplicates from a sequence #
# but preserves order                #
######################################


def ordered_set(sequence):
    seen_items = set()
    #seen_add = seen.add
    return [item for item in sequence if item not in seen_items and not seen_items.add(item)]

####################################################
# gets index from list only if exists              #
# (used to deal w/ XML nodes in registration fns)  #
####################################################


def get_index(list, i):
    try:
        return list[i]
    except IndexError:
        return None

###########################################
# finds matching item in list             #
# (using this fn instead of standard loop #
# b/c it doesn't traverse the whole list) #
###########################################


def find_in_sequence(fn, sequence):
    for item in sequence:
        if fn(item) == True:
            return item
    return None


########################
# flatten a dictionary #
########################

def get_joined_keys_dict(dct):
    """
    Convert 2D dictionary to 1D dictionary joining keys by an underscore.

    >>> dct = {'a': {'b': 1, 'c': 2}}
    >>> get_joined_keys_dict(dct)
    >>> {'a_b': 1, 'a_c': 2}

    :param dict dct: The input dictionary to collapse.
    :rtype: dict
    """

    ret = {}
    for k, v in dct.iteritems():
        for k2, v2 in v.iteritems():
            ret[u'{0}_{1}'.format(k, k2)] = v2
    return ret

###########################
# iterate through options #
###########################

from collections import namedtuple
import itertools


def itr_row(key, sequence):
    for element in sequence:
        yield ({key: element})


def itr_product_keywords(keywords, as_namedtuple=False):
    if as_namedtuple:
        yld_tuple = namedtuple('ITesterKeywords', keywords.keys())

    iterators = [itr_row(ki, vi) for ki, vi in keywords.iteritems()]
    for dictionaries in itertools.product(*iterators):
        yld = {}
        for dictionary in dictionaries:
            yld.update(dictionary)
        if as_namedtuple:
            yld = yld_tuple(**yld)
        yield yld

# sample usage...
#
# def test_iter(self):
#
#         test_document_type = "modelcomponent"
#
#         test_proxy = MetadataModelProxy.objects.get(version=self.version, name__iexact=test_document_type)
#
#         test_vocabularies = self.project.vocabularies.filter(document_type__iexact=test_document_type)
#
#         test_customizer = self.create_customizer_set_with_subforms(self.project, self.version, test_proxy, properties_with_subforms=["author"])
#         (model_customizer,standard_category_customizers,standard_property_customizers,nested_scientific_category_customizers,nested_scientific_property_customizers) = \
#             MetadataCustomizer.get_existing_customizer_set(test_customizer, test_vocabularies)
#         scientific_property_customizers = get_joined_keys_dict(nested_scientific_property_customizers)
#
#
#         standard_property_displayed_values = [True, False]
#         standard_property_inherited_values = [True, False]
#         standard_property_values_to_iterate_over = {
#             "displayed" : standard_property_displayed_values,
#             "inherited" : standard_property_inherited_values,
#         }
#
#         for k in itr_product_keywords(standard_property_values_to_iterate_over):
#                 # TODO: CAN I DO SOMETHING LIKE standard_property_customizers[i].__dict__.update(k)
#               for field_name, field_value in k.iteritems():
#                   standard_property_customizers[i].setattr(field_name,field_value)
#
#               if an-exeception-happens:
#                   if k has invalid values:
#                       continue
#                   else:
#                       raise
#             import ipdb; ipdb.set_trace()

