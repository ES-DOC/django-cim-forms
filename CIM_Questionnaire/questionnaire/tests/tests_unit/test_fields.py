####################
#   ES-DOC CIM Questionnaire
#   Copyright (c) 2014 ES-DOC. All rights reserved.
#
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################

__author__ = 'ben.koziol'
__date__ = "Dec 01, 2014 3:00:00 PM"

"""
.. module:: test_fields

Tests the custom fields specific to the CIM customizer
"""

from CIM_Questionnaire.questionnaire.tests.test_base import TestQuestionnaireBase, TestModel
from CIM_Questionnaire.questionnaire.forms.forms_base import MetadataForm
from CIM_Questionnaire.questionnaire.utils import HUGE_STRING, model_to_data, get_data_from_form
from CIM_Questionnaire.questionnaire.fields import *


######################################################################################
# these next few models & forms are used for testing custom field types              #
# I am testing them in isolation here, away from the complexity of the Questionnaire #
# (hence the use of TestModel and the extra code in setUp/tearDown below             #
######################################################################################

ENUMERATION_CHOICES = "one|two|three|four"
ENUMERATION_FIELD_CHOICES = [(choice, choice) for choice in ENUMERATION_CHOICES.split("|")]


class EnumerationFieldModel(TestModel):

    name = models.CharField(blank=True, null=True, max_length=BIG_STRING, unique=True)

    enumeration_value = EnumerationField(blank=True, null=True)
    enumeration_other_value = models.CharField(max_length=HUGE_STRING, blank=True, null=True)

    open = models.NullBooleanField(default=False, null=True)
    multi = models.NullBooleanField(default=False, null=True)
    nullable = models.NullBooleanField(default=False, null=True)

    def __unicode__(self):
        return u"%s" % self.name


class EnumerationFieldForm(MetadataForm):

    class Meta:
        model = EnumerationFieldModel

    def __init__(self, *args, **kwargs):
        super(EnumerationFieldForm, self).__init__(*args, **kwargs)

        # simulates all the jiggery-pokery that is done in the Questionnaire forms...
        # TODO: MOVE THIS TO A SEPARATE FN

        all_enumeration_choices = ENUMERATION_FIELD_CHOICES

        _open = self.get_current_field_value("open")
        _multi = self.get_current_field_value("multi")
        _nullable = self.get_current_field_value("nullable")

        enumeration_value_field = self.fields["enumeration_value"]

        if _nullable:
            all_enumeration_choices += NULL_CHOICE
        if _open:
            all_enumeration_choices += OTHER_CHOICE
        if _multi:
            enumeration_value_field.set_choices(all_enumeration_choices, multi=True)
        else:
            enumeration_value_field.set_choices(all_enumeration_choices, multi=False)


class CardinalityFieldModel(TestModel):

    name = models.CharField(blank=True, null=True, max_length=BIG_STRING, unique=True)

    cardinality = CardinalityField(blank=True)

    def __unicode__(self):
        return u"%s" % self.name


class CardinalityFieldForm(MetadataForm):

    class Meta:
        model = CardinalityFieldModel

    pass


TEST_FIELD_MODELS = {
    "enumeration_field_model": EnumerationFieldModel,
    "cardinality_field_model": CardinalityFieldModel,
}


#################################
# now for the actual test class #
#################################

class Test(TestQuestionnaireBase):

    def setUp(self):
        for model_name, model_class in TEST_FIELD_MODELS.iteritems():
            create_fn_name = model_class.create_fn_name
            try:
                model_create_fn = getattr(model_class, create_fn_name)
                model_create_fn()
            except AttributeError:
                msg = "%s has no %s method" % (model_name, create_fn_name)
                raise TypeError(msg)
        super(Test, self).setUp()

    def tearDown(self):
        for model_name, model_class in TEST_FIELD_MODELS.iteritems():
            delete_fn_name = model_class.delete_fn_name
            try:
                model_delete_fn = getattr(model_class, delete_fn_name)
                model_delete_fn()
            except AttributeError:
                msg = "%s has no %s method" % (model_name, delete_fn_name)
                raise TypeError(msg)
        super(Test, self).tearDown()

    ######################################
    # ...and now for the actual tests... #
    ######################################

    def test_enumeration_field(self):

        enumeration_model_single = EnumerationFieldModel(name="one", multi=False)
        enumeration_model_multi = EnumerationFieldModel(name="two", multi=True)

        enumeration_form_data_single = model_to_data(enumeration_model_single, include={"loaded": True, })
        enumeration_form_data_multi = model_to_data(enumeration_model_multi, include={"loaded": True, })

        enumeration_form_single = EnumerationFieldForm(initial=enumeration_form_data_single)
        enumeration_form_multi = EnumerationFieldForm(initial=enumeration_form_data_multi)

        post_data_single = get_data_from_form(enumeration_form_single)
        post_data_multi = get_data_from_form(enumeration_form_multi)

        new_data = post_data_single.copy()
        new_data.update({
            "name": "one",
            "enumeration_value": None,
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertTrue(validity)
        enumeration_field_model = enumeration_form.save()
        self.assertEqual(enumeration_field_model.enumeration_value, [])

        new_data = post_data_single.copy()
        new_data.update({
            "name": "two",
            "enumeration_value": "one",
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertTrue(validity)
        enumeration_model = enumeration_form.save()
        self.assertEqual(enumeration_model.enumeration_value, [u"one"])

        new_data = post_data_single.copy()
        new_data.update({
            "name": "three",
            "enumeration_value": "invalid",
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertFalse(validity)

        new_data = post_data_single.copy()
        new_data.update({
            "name": "four",
            "enumeration_value": ["one", "two"]
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertFalse(validity)

        new_data = post_data_multi.copy()
        new_data.update({
            "name": "five",
            "enumeration_value": None,
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertTrue(validity)
        enumeration_model = enumeration_form.save()
        self.assertEqual(enumeration_model.enumeration_value, [])

        new_data = post_data_multi.copy()
        new_data.update({
            "name": "six",
            "enumeration_value": ["one"],
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertTrue(validity)
        enumeration_model = enumeration_form.save()
        self.assertEqual(enumeration_model.enumeration_value, [u"one"])

        new_data = post_data_multi.copy()
        new_data.update({
            "name": "seven",
            "enumeration_value": ["one", "two"],
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertTrue(validity)
        enumeration_model = enumeration_form.save()
        self.assertEqual(enumeration_model.enumeration_value, [u"one", u"two"])

        new_data = post_data_multi.copy()
        new_data.update({
            "name": "eight",
            "enumeration_value": ["one", "invalid"],
        })
        enumeration_form = EnumerationFieldForm(data=new_data)
        validity = enumeration_form.is_valid(loaded=enumeration_form.get_current_field_value("loaded"))
        self.assertFalse(validity)

    def test_cardinality_field(self):

        cardinality_name = "cardinality_test"

        cardinality_0_to_1 = [u"0", u"1"]  # valid cardinality
        cardinality_0_to_many = [u"0", u"*"]  # valid cardinality
        cardinality_5_to_1 = [u"5", u"1"]  # invalid cardinality; working through forms should catch it
        cardinality_100_to_foo = [u"100", u"foo"]  # invalid cardinality; working through forms should catch it
        cardinality_none = [None, None]  # invalid cardinality; working through forms should catch it

        # testing creation of cardinality fields through forms rather than models

        cardinality_field_model = CardinalityFieldModel(name=",".join(cardinality_0_to_1), cardinality=cardinality_0_to_1)
        cardinality_form_data = cardinality_field_model.get_form_data()
        cardinality_form = CardinalityFieldForm(initial=cardinality_form_data, prefix=cardinality_name)
        post_data = get_data_from_form(cardinality_form)
        cardinality_form = CardinalityFieldForm(data=post_data, initial=cardinality_form_data, prefix=cardinality_name)
        validity = cardinality_form.is_valid(loaded=cardinality_form.get_current_field_value("loaded"))
        self.assertTrue(validity)
        cardinality_field_model = cardinality_form.save()
        self.assertEqual(cardinality_field_model.cardinality.split("|"), cardinality_0_to_1)

        cardinality_field_model = CardinalityFieldModel(name=",".join(cardinality_0_to_many), cardinality=cardinality_0_to_many)
        cardinality_form_data = cardinality_field_model.get_form_data()
        cardinality_form = CardinalityFieldForm(initial=cardinality_form_data, prefix=cardinality_name)
        post_data = get_data_from_form(cardinality_form)
        cardinality_form = CardinalityFieldForm(data=post_data, initial=cardinality_form_data, prefix=cardinality_name)
        validity = cardinality_form.is_valid(loaded=cardinality_form.get_current_field_value("loaded"))
        self.assertTrue(validity)
        cardinality_field_model = cardinality_form.save()
        self.assertEqual(cardinality_field_model.cardinality.split("|"), cardinality_0_to_many)

        cardinality_field_model = CardinalityFieldModel(name=",".join(cardinality_5_to_1), cardinality=cardinality_5_to_1)
        cardinality_form_data = cardinality_field_model.get_form_data()
        cardinality_form = CardinalityFieldForm(initial=cardinality_form_data, prefix=cardinality_name)
        post_data = get_data_from_form(cardinality_form)
        cardinality_form = CardinalityFieldForm(data=post_data, initial=cardinality_form_data, prefix=cardinality_name)
        validity = cardinality_form.is_valid(loaded=cardinality_form.get_current_field_value("loaded"))
        self.assertFalse(validity)

        cardinality_field_model = CardinalityFieldModel(name=",".join(cardinality_100_to_foo), cardinality=cardinality_100_to_foo)
        cardinality_form_data = cardinality_field_model.get_form_data()
        cardinality_form = CardinalityFieldForm(initial=cardinality_form_data, prefix=cardinality_name)
        post_data = get_data_from_form(cardinality_form)
        cardinality_form = CardinalityFieldForm(data=post_data, initial=cardinality_form_data, prefix=cardinality_name)
        validity = cardinality_form.is_valid(loaded=cardinality_form.get_current_field_value("loaded"))
        self.assertFalse(validity)

        cardinality_field_model = CardinalityFieldModel(name="cardinality_none", cardinality=cardinality_none)
        cardinality_form_data = cardinality_field_model.get_form_data()
        cardinality_form = CardinalityFieldForm(initial=cardinality_form_data, prefix=cardinality_name)
        post_data = get_data_from_form(cardinality_form)
        cardinality_form = CardinalityFieldForm(data=post_data, initial=cardinality_form_data, prefix=cardinality_name)
        validity = cardinality_form.is_valid(loaded=cardinality_form.get_current_field_value("loaded"))
        self.assertTrue(validity)

        cardinality_field_model = cardinality_form.save()
        self.assertEqual(cardinality_field_model.cardinality, "|")