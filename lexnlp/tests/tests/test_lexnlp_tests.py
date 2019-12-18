"""Unit tests for common routines for testing NLP functions against test data
stored separately in CSV files.
"""

import os
import pytest
import tempfile

from lexnlp.tests import lexnlp_tests
from nose.tools import assert_dict_equal, assert_tuple_equal, assert_equals, assert_in

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_writing_reading_test_data():
    column_names = ('text', 'input_text_languages_str', 'input_int1_int', 'input_arg_bool', 'expected1', 'expected2')
    texts = (None, 'text2', 'text3', '###text4')
    values = ((('l1', '11', 'False', 'e11', 'e12'),),
              (('l2', '22', 'True', 'e21', 'e22'),),
              (('l3', '33', 'False', 'e31', 'e32'), ('l3', '33', 'False', 'e31', 'e32'), 'string'),
              ())
    file_name = None
    try:
        file_name = lexnlp_tests.write_test_data_text_and_tuple(texts, values, column_names)
        actual = [(i, text, input_args, expected)
                  for i, text, input_args, expected in lexnlp_tests.iter_test_data_text_and_tuple(call_stack_offset=1)]
        a2 = actual[0]
        e2 = (2, 'text2', {'text_languages': 'l2', 'arg': True, 'int1': 22}, [('e21', 'e22')])
        print('Actual: {0}'.format(a2))
        print('Expected: {0}'.format(e2))

        assert_equals(a2[0], e2[0])
        assert_equals(a2[1], e2[1])
        assert_dict_equal(a2[2], e2[2])
        assert_equals(len(a2[3]), len(e2[3]))
        assert_tuple_equal(a2[3][0], e2[3][0])

    finally:
        if file_name:
            os.remove(file_name)


def test_assert_set_equal():
    set1 = {'a', 'b', 'c'}
    set2 = {'a', 'b', 'd'}

    lexnlp_tests.assert_set_equal("test1()", 'text1', set1, {'a', 'b', 'c'},
                                  do_raise=True,
                                  do_write_to_file=False,
                                  debug_print=True)

    _handle, file_name = tempfile.mkstemp()
    try:
        problem = lexnlp_tests.assert_set_equal("test1()", 'text1', set1, set2,
                                                problems_file=file_name,
                                                do_raise=False,
                                                do_write_to_file=True)
        assert_in('But it should return', problem)
        assert os.stat(file_name).st_size > 0
    finally:
        os.remove(file_name)

    with pytest.raises(AssertionError):
        lexnlp_tests.assert_set_equal("test1()", 'text1', set1, set2,
                                      problems_file=file_name,
                                      do_raise=True, do_write_to_file=False,
                                      debug_print=True)


def test_assert_in():
    set1 = {'a', 'b', 'c'}

    lexnlp_tests.assert_in("test1()", 'text1', 'c', set1, do_raise=True, do_write_to_file=False)

    _handle, file_name = tempfile.mkstemp()
    try:
        problem = lexnlp_tests.assert_in("test1()", 'text1', 'd', set1, problems_file=file_name, do_raise=False,
                                         do_write_to_file=True)
        assert_in('wrong', problem)
        assert os.stat(file_name).st_size > 0
    finally:
        os.remove(file_name)

    with pytest.raises(AssertionError):
        lexnlp_tests.assert_in("test1()", 'text1', 'd', set1, do_raise=True, do_write_to_file=False)


def test_build_extraction_func_name():
    name = lexnlp_tests.build_extraction_func_name(test_assert_in, set1={'h', ''.join([str(i) for i in range(10000)])})
    assert_equals('test_assert_in(text, set1=set(2 el.))', name)

    name = lexnlp_tests.build_extraction_func_name(test_assert_in, dict1={'h': ''.join([str(i) for i in range(10000)])})
    assert_equals('test_assert_in(text, dict1=dict(1 el.))', name)

    name = lexnlp_tests.build_extraction_func_name(test_assert_in, tuple1=tuple(str(i) for i in range(10000)))
    assert_equals('test_assert_in(text, tuple1=tuple(10000 el.))', name)

    name = lexnlp_tests.build_extraction_func_name(test_assert_in, f=lambda d: d * d)
    assert_equals('test_assert_in(text, f=<class \'function\'>)', name)

    name = lexnlp_tests.build_extraction_func_name(test_assert_in)
    assert_equals('test_assert_in(text)', name)


def test_test_extraction_func_on_test_data():

    def func(text):
        return text + "!"

    with pytest.raises(AssertionError):
        lexnlp_tests.test_extraction_func_on_test_data(func, start_from_csv_line=3)
