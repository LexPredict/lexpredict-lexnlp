#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Languages unit tests.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.all_locales.languages import Locale


class TestLocales(TestCase):

    def test_locales_convert(self):
        data = [
            {'input': 'en', 'output_locale_code': 'EN'},
            {'input': 'en-US', 'output_locale_code': 'US'},
            {'input': 'en/Gb', 'output_locale_code': 'GB'},
            {'input': 'En_us', 'output_locale_code': 'US'},
        ]
        output_language_code = 'en'
        for item in data:
            locale_obj = Locale(item['input'])
            self.assertEqual(locale_obj.language, output_language_code)
            self.assertEqual(locale_obj.locale_code, item['output_locale_code'])
