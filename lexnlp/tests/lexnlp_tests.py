"""Common routines for testing NLP functions against test data stored
separately in CSV files.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import csv
import inspect
import os
import time
from datetime import datetime
from typing import Callable, Set, Union, List, Tuple, Any

import nose.tools
import psutil
from memory_profiler import memory_usage

from lexnlp.extract.common.base_path import lexnlp_test_path


DIR_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DIR_BENCHMARKS = os.path.join(DIR_ROOT, 'benchmarks')
FN_BENCHMARKS = os.path.join(DIR_BENCHMARKS, 'benchmarks.csv')
FN_PROBLEMS = os.path.join(DIR_BENCHMARKS, 'problems_hr.txt')
DIR_TEST_DATA = os.path.join(DIR_ROOT, 'test_data')
IN_CELL_CSV_DELIMITER = '|'
IN_CELL_CSV_NONE = ''
SYS_OS_UNAME = os.uname()
try:
    SYS_CPU_FREQ = psutil.cpu_freq()
except FileNotFoundError:
    SYS_CPU_FREQ = None
SYS_CPU_FREQ = SYS_CPU_FREQ.current if SYS_CPU_FREQ else None
SYS_CPU_COUNT = psutil.cpu_count()
SYS_MEM_TOTAL = psutil.virtual_memory().total
SYS_OS_NAME = '{0} {1} ({2})'.format(SYS_OS_UNAME.sysname, SYS_OS_UNAME.release, SYS_OS_UNAME.version)
SYS_NODE_NAME = SYS_OS_UNAME.nodename
SYS_ARCH = SYS_OS_UNAME.machine


def this_test_data_path(create_dirs: bool = False, caller_stack_offset: int = 1):
    """
    Calculate test data file path for the test function which called this one.
    The path/name are calculated using python execution stack trace routines.
    Template: test_data/pack/a/ge/test_file_name/test_function_name.csv
    :param create_dirs: If set to true then all the folders required to writing the test data file will be created.
    :param caller_stack_offset: Offset of the test function in this function's call stack. Should be 1 if this function
    is called straight from the test function. Plus 1 for each next intermediate function call.
    :return:
    """
    stack = inspect.stack()
    module_name = inspect.getmodule(stack[caller_stack_offset][0]).__name__
    file_dir = os.path.normpath(os.path.join(DIR_TEST_DATA, *module_name.split('.')))
    if create_dirs:
        os.makedirs(file_dir, exist_ok=True)
    file_name = os.path.join(file_dir, stack[caller_stack_offset][3] + '.csv')
    return file_name


def iter_test_data_text_and_tuple(file_name: str = None, call_stack_offset: int = 0):
    """
    Reads test data from external file and iterates through pairs of text -> expected value.
    Types of values are lost during write-read to csv operations and they all are returned as strings.
    :param file_name: Optional parameter - to read data from the specified file
    :param call_stack_offset: Optional parameter to allow proper calculation of test data file name when
    this function is called not straight from the test method but from a stack of other methods.
    :return:
    """
    if not file_name:
        file_name = this_test_data_path(create_dirs=False, caller_stack_offset=2 + call_stack_offset)
    print('\n\nLoading test data:\n{0}\n'.format(file_name))

    with open(file_name, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        input_columns = [col for col in reader.fieldnames if col.startswith('input_')]
        expected_output_columns = [col for col in reader.fieldnames[1:] if col not in input_columns]
        cur_text = None
        cur_input_args = None
        cur_expected_value_list = []
        i = -1

        def input_arg(column_name: str) -> str:
            if column_name.startswith('input_'):
                column_name = column_name[len('input_'):]
            if column_name.endswith('_bool'):
                column_name = column_name[:-len('_bool')]
            elif column_name.endswith('_int'):
                column_name = column_name[:-len('_int')]
            elif column_name.endswith('_str'):
                column_name = column_name[:-len('_str')]
            return column_name

        def read_value(column_name: str, value_str: str) -> Any:
            if not value_str:
                return None
            if column_name.endswith('_bool'):
                return value_str.lower() == 'true'
            if column_name.endswith('_int'):
                return int(value_str)
            return value_str

        for line in reader:
            i = i + 1

            # Empty strings are Nones
            for field_name in reader.fieldnames:
                if not line.get(field_name):
                    line[field_name] = None

            text = line.get(reader.fieldnames[0])

            if text and text.startswith('###'):
                continue

            if text:
                # if it is not the first found text
                if cur_text:
                    yield i, cur_text, cur_input_args, cur_expected_value_list

                cur_expected_value_list = []
                cur_text = text
                cur_input_args = {input_arg(key): read_value(key, line.get(key)) for key in input_columns}

            if not cur_text:
                continue

            expected_value_tuple_or_string = tuple(read_value(key, line.get(key)) for key in expected_output_columns)
            if all(item is None for item in expected_value_tuple_or_string):
                expected_value_tuple_or_string = None
            elif len(expected_value_tuple_or_string) == 1:
                expected_value_tuple_or_string = expected_value_tuple_or_string[0]

            if expected_value_tuple_or_string:
                cur_expected_value_list.append(expected_value_tuple_or_string)

        if cur_text:
            yield i, cur_text, cur_input_args, cur_expected_value_list


def write_test_data_text_and_tuple(texts: tuple, values: tuple, column_names: tuple):
    """
    Writes test data to external file for further using in tests.
    File name is calculated by this_test_data_path(..) function (test_data/pack/a/ge/test_file_name/test_method_name).
    Test data is written in CSV format with the special rules to allow multiple expected value tuples per single text.
    Header: Text,Component 1 Title,...,Component N Title
            Text 1,Value Component 1.1 of Text 1,...,Value Component 1.N of Text 1
            ,Value Component 2.1 of Text 1,...,Value Component 2.N of Text 1
            ...
            ,Value Component M.1 of Text 1,...,Value Component M.N of Text 1
            Text 2,Value Component 1.1 of Text 2,...,Value Component 1.N of Text 2
            ,Value Component 2.1 of Text 2,...,Value Component 2.N of Text 2
            ...
            ,Value Component K.1 of Text 2,...,Value Component K.N of Text 2
            ...
    So if there is no text in the first column in a row - this means to match the values to the last filled text above.

    :param texts: Tuple of text stirngs ("texts" column).
    :param values: Tuple of expected values matching texts on the same index (expected values column(s))
    :param column_names: Names of the columns. Should be: Text, Name of First Entry in Values, Name of Second Entry...
    :return:
    """

    file_name = this_test_data_path(create_dirs=True, caller_stack_offset=2)
    with open(file_name, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        for i, text in enumerate(texts):
            multiple_values = values[i]
            first = True
            if not multiple_values:
                writer.writerow((text,))
            else:
                for values_tuple_or_string in multiple_values:
                    if first:
                        first = False
                    else:
                        text = None
                    if isinstance(values_tuple_or_string, (tuple, list)):
                        row = [text]
                        for v in values_tuple_or_string:
                            row.append(v)
                        row = tuple(row)
                    else:
                        row = (text, values_tuple_or_string)
                    writer.writerow(row)
    return file_name


def build_extraction_func_name(func: Callable, **kwargs):
    kwargs_str = ''
    if kwargs:
        kwargs_list = list()
        for key, value in kwargs.items():
            str_value = str(value)
            if len(str_value) < 50:
                value = '\'' + value + '\'' if isinstance(value, str) else str(value)
            elif isinstance(value, list):
                value = 'list(' + str(len(value)) + ' el.)'
            elif isinstance(value, tuple):
                value = 'tuple(' + str(len(value)) + ' el.)'
            elif isinstance(value, set):
                value = 'set(' + str(len(value)) + ' el.)'
            elif isinstance(value, dict):
                value = 'dict(' + str(len(value)) + ' el.)'
            else:
                value = str(type(value))
            kwargs_list.append(key + '=' + value)

        kwargs_str = ', '.join(kwargs_list)
    return func.__name__ + '(text' + ((', ' + kwargs_str) if kwargs_str else '') + ')'


def test_extraction_func_on_test_data(func: Callable,
                                      benchmark_name: str = None,
                                      expected_data_converter: Callable = None,
                                      actual_data_converter: Callable = None,
                                      test_only_expected_in: bool = False,
                                      debug_print: bool = False,
                                      start_from_csv_line: int = None,
                                      test_data_path: str = None,
                                      **kwargs):
    """
    Tests the provided function against the test data loaded from external file.
    The provided function is expected to extract a tuple of some objects from string text.
    Format of the extracted tuple should match the format in test data.
    Test data is expected to be in the file name calculated by this_test_data_path(..) method.
    For each "text -> expected tuple" entry from test data file the result of the provided function is calculated
    and compared against the expected one as lists using "assert_list_equal"
    """
    if not benchmark_name:
        benchmark_name = build_extraction_func_name(func, **kwargs)

    problems = []

    if test_data_path:
        file_name = test_data_path
        if not os.path.isfile(file_name):
            file_name = os.path.join(lexnlp_test_path, file_name)
        if not os.path.isfile(file_name):
            raise FileNotFoundError(f'File "{test_data_path}" was not found')
    else:
        file_name = this_test_data_path(create_dirs=False, caller_stack_offset=2)

    for i, text, input_args, expected in iter_test_data_text_and_tuple(file_name):
        if start_from_csv_line and i < start_from_csv_line - 1:
            continue
        kwargs.update(input_args)
        actual, expected, problem = test_extraction_func(expected, func, text,
                                                         benchmark_name=benchmark_name,
                                                         test_data_file=file_name,
                                                         expected_data_converter=expected_data_converter,
                                                         actual_data_converter=actual_data_converter,
                                                         do_raise=False,
                                                         test_only_expected_in=test_only_expected_in,
                                                         **kwargs)
        if problem:
            problems.append(f'{i+1}) {problem}')
            print(problem)
        elif debug_print:
            print('================================================================================================\n'
                  'Actual:\n{0}\n\n'
                  'Expected:\n{1}\n'
                  '================================================================================================\n'
                  .format(fmt_results(actual), fmt_results(expected)))

    if problems:
        raise AssertionError('Testing NLP function {0} failed. See log for problems:\n{1}'.format(benchmark_name,
                                                                                             FN_PROBLEMS))


def test_extraction_func(expected, func: Callable, text,
                         benchmark_name: str = None,
                         test_data_file: str = None,
                         expected_data_converter: Callable = None,
                         actual_data_converter: Callable = None,
                         do_raise: bool = True,
                         debug_print: bool = False,
                         test_only_expected_in: bool = False,
                         **kwargs):
    if not benchmark_name:
        benchmark_name = build_extraction_func_name(func, **kwargs)

    if expected_data_converter:
        expected = expected_data_converter(expected)
    elif test_only_expected_in:
        expected = expected[0] if expected else None

    actual = benchmark(benchmark_name, func, text, **kwargs)
    if actual_data_converter:
        actual = actual_data_converter(actual)
    actual = set(actual) if actual else None

    if test_only_expected_in:
        problem = assert_in(benchmark_name, text, expected, actual,
                            do_raise=do_raise, test_data_file=test_data_file)
    else:
        expected = set(expected) if expected else None
        problem = assert_set_equal(benchmark_name, text, actual, expected,
                                   do_raise=do_raise,
                                   test_data_file=test_data_file,
                                   debug_print=debug_print)

    return actual, expected, problem


def benchmark_extraction_func(func: Callable, text, **kwargs):
    benchmark_name = build_extraction_func_name(func, **kwargs)
    return benchmark(benchmark_name, func, text, **kwargs)


def benchmark_decorator(function, *args, **kwargs):
    def wrapper():
        benchmark_name = '{}(args={} kwargs={})'.format(function.__name__, args, kwargs)
        res = benchmark(benchmark_name, function, *args, **kwargs)
        return res
    return wrapper


def benchmark(benchmark_name: str, func: Callable, *args, benchmark_file: str = FN_BENCHMARKS, **kwargs):
    ts = time.time()
    mem_res = memory_usage((func, args, kwargs), max_usage=True, retval=True)
    exec_time = time.time() - ts
    res = mem_res[1]
    print(mem_res)
    max_memory_usage = mem_res[0] if isinstance(mem_res[0], (float, int)) else mem_res[0][0]

    benchmark_dir = os.path.dirname(benchmark_file)
    os.makedirs(benchmark_dir, exist_ok=True)
    exists = os.path.isfile(benchmark_file) and os.stat(benchmark_file).st_size
    with open(benchmark_file, 'a' if exists else 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(('date', 'function', 'text_size_chars', 'exec_time_sec', 'max_memory_usage_mb',
                             'sys_cpu_count', 'sys_cpu_freq', 'sys_ram_total', 'sys_os', 'sys_node_name', 'sys_arch'))

        text = args[0] if len(args) > 0 and isinstance(args[0], str) else 'None'
        text_size = len(text) if text else 0
        writer.writerow((datetime.utcnow().isoformat(), benchmark_name, text_size, exec_time, max_memory_usage,
                         SYS_CPU_COUNT, SYS_CPU_FREQ, SYS_MEM_TOTAL,
                         SYS_OS_NAME, SYS_NODE_NAME, SYS_ARCH))
        print('{3}\n{4}\nText size: {0:5d}, Exec Time (s): {1:4.4f}, Max Memory (mb): {2:4.4f}\n'
              .format(text_size, exec_time, max_memory_usage, benchmark_name, fmt_short_text(text, 100)))

    return res


def assert_set_equal(function_name: str,
                     text: str,
                     actual_results: Set,
                     expected_results: Set,
                     problems_file: str = FN_PROBLEMS,
                     do_raise: bool = True,
                     do_write_to_file: bool = True,
                     debug_print: bool = True,
                     test_data_file: str = None) -> Union[str, None]:
    if not expected_results and not actual_results:
        return None
    exx = None
    try:
        nose.tools.assert_set_equal(actual_results, expected_results)
    except AssertionError as ex:
        exx = ex

    if exx:
        title = 'Function {0} returns wrong results on "{1}"'.format(function_name, fmt_short_text(text))
        body = """
-----------------------------------------------------------------------------------------------------------------------
{data_file_note}*Problem:*
Try executing NLP function *{function_name}* on text:
{{code}}
{text}
{{code}}


It returns (actual result):
{{code}}
{actual}
{{code}}


But it should return (expected result):
{{code}}
{expected}
{{code}}


*Desired Outcome:*
Check the function.
If the expected data is correct then fix the function. Otherwise, fix the expected data.
=======================================================================================================================
        """.format(function_name=function_name,
                   text=text,
                   actual=fmt_results(actual_results),
                   expected=fmt_results(expected_results),
                   data_file_note='Test data file: {0}\n\n'.format(os.path.relpath(test_data_file, DIR_ROOT))
                   if test_data_file else '')
        problem = title + body

        if do_write_to_file:
            with open(problems_file, 'a', encoding='utf8') as f:
                f.write(problem)
                f.write('\n\n')

        if debug_print:
            print(problem)

        if do_raise:
            raise exx or AssertionError()
        return problem


def fmt_short_text(text: str, max_len: int = 40):
    orig_len = len(text)
    text = text[:max_len]
    text = text.replace('\t', ' ')
    text = text.replace('\n', ' ')
    while '  ' in text:
        text = text.replace('  ', ' ')
    if orig_len > max_len:
        text = text + '...'
    return text


def fmt_results(results: Union[Set, List, Tuple]):
    return '\n'.join([str(r) for r in results]) if results else ''


def assert_in(function_name: str,
              text: str,
              expected_in,
              actual_results: Set,
              problems_file: str = FN_PROBLEMS,
              do_raise: bool = True,
              do_write_to_file: bool = True,
              test_data_file: str = None) -> Union[str, None]:
    exx = None
    try:
        nose.tools.assert_in(expected_in, actual_results)
    except AssertionError as ex:
        exx = ex

    if exx:
        title = 'Function {0} returns wrong results on "{1}"'.format(function_name, fmt_short_text(text))
        body = """
-----------------------------------------------------------------------------------------------------------------------
{data_file_note}*Problem:*
Try executing NLP function *{function_name}* on text:
{{code}}
{text}
{{code}}


It returns (actual result):
{{code}}
{actual}
{{code}}


But its results should also contain:
{{code}}
{expected_in}
{{code}}


*Desired Outcome:*
Check the function.
If the expected data is correct then fix the function. Otherwise, fix the expected data. 
=======================================================================================================================
        """.format(function_name=function_name,
                   text=text,
                   actual=fmt_results(actual_results),
                   expected_in=expected_in,
                   data_file_note='Test data file: {0}\n\n'.format(os.path.relpath(test_data_file, DIR_ROOT))
                   if test_data_file else '')
        problem = title + body

        if do_write_to_file:
            with open(problems_file, 'a', encoding='utf8') as f:
                f.write(problem)
                f.write('\n\n')

        if do_raise:
            raise exx or AssertionError()
        return problem
