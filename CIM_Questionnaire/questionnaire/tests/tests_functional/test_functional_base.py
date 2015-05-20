####################
#   ES-DOC CIM Questionnaire
#   Copyright (c) 2014 ES-DOC. All rights reserved.
#
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################

__author__ = 'allyn.treshansky'
__date__ = "May 15, 2015 3:00:00 PM"

"""
.. module:: test_functional_base

base class for functional tests; provides LiveServerTestCase

"""

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver


TEST_TIMEOUT = 10  # seconds


class TestFunctionalBase(LiveServerTestCase):
    """
    base class for functional tests; Uses selenium to drive a Firefox instance.
    By convention, some tests that are common to multiple pages
    are prefixed w/ "check" rather than "test"
    (so that they're not run automatically but can be called explicitly).
    """

    fixtures = ['questionnaire_testdata.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(TEST_TIMEOUT)
        super(TestFunctionalBase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(TestFunctionalBase, cls).tearDownClass()

    # I SUPSECT THAT THINGS MIGHT GO A BIT WONKY
    # B/C OF THE AMOUNT OF JQUERY LOADING & AJAX STUFF THAT THE APP DOES;
    # IN THAT CASE, I HAVE A HOOK HERE FOR A TIMEOUT FN
    # - OTHER THAN THE IMPLICIT TIMEOUT ABOVE -
    # BUT I'M NOT SURE HOW TO COMPLETE IT
    # (THE LINKS GIVE MORE INFO)
    # def wait_for_js_to_load(self):
    #     from selenium.webdriver.support.wait import WebDriverWait
    #     from selenium.webdriver.support import expected_conditions as ec
    #     from selenium.webdriver.common.by import By
    #
    #     something like this...
    #
    #     WebDriverWait(self.selenium, TEST_TIMEOUT).until(
    #         lambda driver: driver.find_element_by_tag_name('my_dynamic_element'), timeout=TEST_TIMEOUT)
    #
    #     or else something like this...
    #
    #     try:
    #         element = WebDriverWait(self.selenium, TEST_TIMEOUT).until(
    #             ec.presence_of_element_located((By.ID, "my_dynamic_element"))
    #         )
    #     finally:
    #         self.selenium.quit()
    #
    # http://selenium-python.readthedocs.org/en/latest/waits.html
    # http://sqa.stackexchange.com/questions/7420/the-code-of-wait-method-for-ajax-call-to-complete
    # https://code.google.com/p/selenium/wiki/FrequentlyAskedQuestions#Q:_WebDriver_fails_to_find_elements_/_Does_not_block_on_page_loa
    # http://selenide.org/

    #######################################################################
    # fns to hide details of whatever test domain LiveServerTestCase uses #
    #######################################################################

    def get_url(self, path=""):
        """
        returns a URL to use w/ tests
        :param path: path to append after the protocol+domain+port
        :return:
        """
        url = u"%s/%s" % (self.live_server_url, path.lstrip("/"))
        return url

    def set_url(self, path):
        """
        :param path: path to goto
        :return: None
        """
        if "//" in path:
            self.selenium.get(path)
        else:
            self.selenium.get(self.get_url(path))

    def assertURL(self, path):
        """
        :param path: asserts path matches the current url
        :return:
        """
        msg = "URLs do not match"

        current_url = self.selenium.current_url.rstrip("/")

        if "//" in path:
            test_url = path.rstrip("/")
        else:
            test_url = self.get_url(path).rstrip("/")

        self.assertEqual(test_url, current_url, msg=msg)

    ###################################
    # checking generic custom widgets #
    ###################################

    def is_initialized(self, webelement):
        """
        checks if widget has been initialized via JS
        :param webelement: selenium webelement representing widget
        :return: boolean
        """
        widget_classes = webelement.get_attribute("class").split(" ")
        for widget_class in widget_classes:
            if widget_class.startswith("initialized_"):
                return True
        return False

    ################################
    # checking multiselect widgets #
    ################################

    def is_multiselect_single(self, webelement):
        """
        :param webelement: selenium webelement representing multiselect widget
        :return: boolean
        """
        multiselect_classes = webelement.get_attribute("class").split(" ")
        return "single" in multiselect_classes

    def is_multiselect_multiple(self, webelement):
        """
        :param webelement: selenium webelement representing multiselect widget
        :return: boolean
        """
        multiselect_classes = webelement.get_attribute("class").split(" ")
        return "multiple" in multiselect_classes

    def is_multiselect_required(self, webelement):
        """
        :param webelement: selenium webelement representing multiselect widget
        :return: boolean
        """
        multiselect_classes = webelement.get_attribute("class").split(" ")
        return "selection_required" in multiselect_classes

    def get_multiselect_header(self, webelement):
        """
        :param webelement: selenium webelement representing multiselect widget
        :return: the header (button) of the widget
        """
        multiselect_header = webelement.find_element_by_css_selector(".multiselect_header")
        return multiselect_header

    def get_multiselect_content(self, webelement):
        """
        :param webelement: selenium webelement representing multiselect widget
        :return: the content (choices) of the widget
        """
        multiselect_content = webelement.find_element_by_css_selector(".multiselect_content")
        return multiselect_content

    def get_multiselect_options(self, webelement):
        """
        :param webelement: selenium webelement representing multiselect widget
        :return: the selected options of the widget
        """
        content = self.get_multiselect_content(webelement)
        options = content.find_elements_by_css_selector("ul li")
        return options

    def get_multiselect_values(self, webelement):
        """
        :param webelement: selenium webelement representing multiselect widget
        :return: the selected options of the widget
        """
        options = self.get_multiselect_options(webelement)
        selected_options = [option for option in options if option.get_attribute("selected")]
        return selected_options

    def set_multiselect_values(self, webelement, values):
        """
        :param webelement: selenium webelement representing multiselect widget
        :param values: string values to select
        :return: None
        """
        options = self.get_multiselect_options(webelement)
        for option in options:
            option_text = option.text
            option_input = option.find_element_by_tag_name("input")
            option_selected = option.get_attribute("selected")
            if option_text in values:
                if not option_selected:
                    option_input.click()
            else:
                if option_selected:
                    option_input.click()

    ######################
    # checking help icons #
    ######################

    def check_help_button(self, webelement):
        """
        tests that the help_button functions as expected
        :param webelement: selenium webelement representing field section
        :return:
        """

        msg = "help_button does not function"

        help_dialog = self.selenium.find_element_by_id("help_dialog")
        help_button = webelement.find_element_by_css_selector("div.help_button")

        self.assertFalse(help_dialog.is_displayed(), msg=msg)
        help_button.click()
        self.assertTrue(help_dialog.is_displayed(), msg=msg)

        help_dialog_close_button = help_dialog.find_element_by_xpath("../div/button")
        help_dialog_close_button.click()
        self.assertFalse(help_dialog.is_displayed(), msg=msg)