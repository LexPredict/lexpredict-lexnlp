#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Regulation unit tests for English.

This module implements unit tests for the regulation extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
    * test_parse_comission should pick one and only one record
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Imports
import os
from unittest import TestCase
from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.en.regulations import get_regulations
from lexnlp.tests import lexnlp_tests
from lexnlp.tests.dictionary_comparer import DictionaryComparer


class TestRegulations(TestCase):
    def test_parse_comission(self):
        text = """
    Pursuant to section 10(d) of the Federal Advisory Committee Act, as amended, notice is hereby given of the following meetings.
    The meetings will be closed to the public in accordance with the provisions set forth in sections 552b(c)(4) and 552b(c)(6), Title 5 U.S.C., as amended. 
    The grant applications and the discussions could disclose confidential trade secrets or commercial property such as patentable material, 
    and personal information concerning individuals associated with the grant applications, the disclosure of which would constitute a clearly unwarranted invasion of personal privacy.
    Name of Committee: Center for Scientific Review Special Emphasis Panel; Small Business: Cancer Biotherapeutics Development.
    """
        ret = list(get_regulations(text))
        self.assertEqual(0, len(ret))

    def test_get_regulations_csv(self):
        """
        Test default get regulations behavior.
        :return:
        """
        test_data_path = os.path.join(lexnlp_test_path,
                                      'lexnlp/extract/en/tests/test_regulations/test_get_regulations.csv')
        lexnlp_tests.test_extraction_func_on_test_data(get_regulations,
                                                       expected_data_converter=lambda d:
                                                       [(reg_type, reg_code) for reg_type, reg_code, _reg_str in d],
                                                       return_source=False,
                                                       as_dict=False,
                                                       test_data_path=test_data_path)
        lexnlp_tests.test_extraction_func_on_test_data(get_regulations,
                                                       expected_data_converter=lambda d:
                                                       [(reg_type, reg_code, reg_str) for reg_type, reg_code, reg_str in d],
                                                       return_source=True,
                                                       as_dict=False,
                                                       test_data_path=test_data_path)

        cmp = DictionaryComparer(check_order=True)
        errors = []

        for (i, text, _input_args, expected) in \
                lexnlp_tests.iter_test_data_text_and_tuple(file_name=test_data_path):
            expected = [{'regulation_type': reg_type,
                         'regulation_code': reg_code,
                         'regulation_text': reg_str}
                        for reg_type, reg_code, reg_str in expected]
            actual = list(lexnlp_tests.benchmark_extraction_func(get_regulations,
                                                                 text,
                                                                 return_source=True,
                                                                 as_dict=True))

            line_errors = cmp.compare_list_of_dicts(expected, actual)
            if line_errors:
                line_errors_str = '\n'.join(line_errors)
                errors.append(f'Regulation tests, line [{i + 1}] errors:\n' +
                              line_errors_str)

        if errors:
            raise Exception('\n\n'.join(errors))
