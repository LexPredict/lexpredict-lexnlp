__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import ast
import codecs
import os
import types
import regex as re
from ast import literal_eval as make_tuple
from collections import OrderedDict
from datetime import date, datetime
from typing import Callable, Type, List, Any, Tuple, Union

from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.extract.common.base_path import lexnlp_test_path


class TypedAntTestCase:
    def __init__(self):
        self.text = ''
        self.total = -1
        self.field_checks = []  # type: List[TypedFieldCheck]
        self.text_filled = False

    @property
    def is_completed(self):
        return self.total >= 0

    def __repr__(self):
        checks = '\n'.join([str(c) for c in self.field_checks])
        return f'{self.text}----\ntotal={self.total}\n{checks}'


class TypedFieldCheck:
    """
    Class is used to check one annotation's attribute against provided value
    E.g., "0)date.month<6" means:
            - check first annotation within the sample
            - check that annotation's month value strictly less than 6

       or "..)coords.1>0" means:
            - check that coords[1] > 0 for all (..) annotations in this sample
    """
    datetime_formats = ['%Y.%m.%d %H:%M:%S', '%Y-%m-%d %H:%M:%S',
                        '%Y.%m.%d %H:%M', '%Y-%m-%d %H:%M']

    date_formats = ['%Y.%m.%d', '%Y-%m-%d']

    reg_compare_split = re.compile(r'!=|<=|>=|=|<|>')

    comparison_name = {
        '=': 'equal to',
        '<=': 'less or equal to',
        '>=': 'greater or equal to',
        '!=': 'not equal to',
        '<': 'less than',
        '>': 'greater than'
    }

    def __init__(self,
                 index: int = 0,
                 path: List[str] = None,
                 value: str = '',
                 comparison: str = '=',
                 check_all: bool = False):
        self.index = index  # annotation index within the sample
        self.check_all = check_all  # check all annotations, index is ignored
        self.path = path or []  # checking value's path
        self.value = value  # value to compare
        self.comparison = comparison  # comparing operation
        self.compare_equal = self.comparison in ('=', '<=', '>=')
        self.compare_not_equal = self.comparison == '!='
        self.last_error = None

    def __repr__(self):
        path = '.'.join(self.path)
        index_path = '..' if self.check_all else str(self.index)
        return f'{index_path}){path}{self.comparison}{self.value}'

    @property
    def comparison_string(self) -> str:  # ['coords', '1'] -> 'coords.1'
        return self.comparison_name[self.comparison]

    @property
    def path_string(self) -> str:  # 'equal' or 'less' or ...
        return '.'.join(self.path)

    def get_ant_field_value(self, ant: TextAnnotation) -> Any:
        val = ant
        for part in self.path:
            index = TextAnnotation.get_int_value(part, -1)
            if index >= 0:
                val = val[index]
                continue
            if part.endswith('()'):
                val = getattr(val, part.strip('()'))
                val = val()
            elif hasattr(val, part):
                val = getattr(val, part)
        return None if val == ant else val

    def compare_values(self, val: Any) -> Tuple[bool, bool]:
        if val is None:
            if not self.value:
                return self.compare_equal, True
            return self.compare_not_equal, True

        if val == self.value:
            return self.compare_equal, True

        try:
            if isinstance(val, tuple):
                cmp_value = make_tuple(self.value)
            elif isinstance(val, (date, datetime)):
                cmp_value = self.parse_date(type(val))
            elif isinstance(val, (bool, dict)):
                cmp_value = ast.literal_eval(self.value)
            else:
                cmp_value = None if not self.value else type(val)(self.value)

            if self.comparison == '=':
                return val == cmp_value, True
            if self.comparison == '<':
                return val < cmp_value, True
            if self.comparison == '>':
                return val > cmp_value, True
            if self.comparison == '<=':
                return val <= cmp_value, True
            if self.comparison == '>=':
                return val >= cmp_value, True
            if self.comparison == '!=':
                return val != cmp_value, True
        except:  # pylint:disable=bare-except
            self.last_error = f'{self.path_string}: cannot cast "{self.value}" to {type(val).__name__}'
            return False, False

    def parse_date(self, val_type: Type) -> Union[date, datetime]:
        if not self.value:
            return None
        if val_type == date:
            for fmt in self.date_formats:
                try:
                    return datetime.strptime(self.value, fmt).date()
                except:  # pylint:disable=bare-except
                    pass
            raise Exception(f'Cannot parse test date: "{self.value}"')

        for fmt in self.datetime_formats:
            try:
                return datetime.strptime(self.value, fmt)
            except:  # pylint:disable=bare-except
                pass
        raise Exception(f'Cannot parse test datetime: "{self.value}"')

    @staticmethod
    def parse(line: str):
        index_end = line.find(')')
        if index_end < 1:
            return None

        index_part = line[:index_end]
        check_all = False
        if index_part == '..':
            check_all = True
            index = -1
        else:
            index = int(line[:index_end])
        line = line[index_end + 1:]

        comp_match = TypedFieldCheck.reg_compare_split.search(line)
        if not comp_match:
            return None
        sign_start, sign_end = comp_match.span()
        if sign_start < 2:
            return None
        path = line[:sign_start]
        path_parts = path.split('.')
        val = line[sign_end:].replace('\\n', '\n').replace('#s#', ' ')
        comp_sign = comp_match.group()
        return TypedFieldCheck(index=index,
                               path=path_parts,
                               value=val,
                               comparison=comp_sign,
                               check_all=check_all)


class ParsingError:
    def __init__(self, **kwargs):
        self.error_type = kwargs.get('error_type')  # type: str
        self.exception = kwargs.get('exception')
        self.case_index = kwargs.get('case_index')
        self.check_index = kwargs.get('check_index')  # type: int
        if self.case_index is None:
            self.case_index = -1
        self.message = kwargs.get('message') or ''

    def __repr__(self):
        parts = [
            f'message={self.message}' if self.message else '',
            f'case={self.case_index}' if self.case_index >= 0 else '',
            f'annotation={self.check_index}' if self.check_index >= 0 else '',
            f'message={self.message}' if self.message else '',
            f'exception={self.exception}' if self.exception else ''
        ]
        return '\n'.join([p for p in parts if p])


class TypedAnnotationsTester:
    def __init__(self, **kwargs):
        self.parsing_method = None  # type: Callable
        self.file_path = None  # type: str
        self.entity_type = None  # type: Type
        self.encoding = kwargs.get('encoding') or 'utf8'
        self.test_cases = []  # type: List[TypedAntTestCase]
        self.test_case = TypedAntTestCase()
        self.errors = []  # type: List[ParsingError]
        self.tests_passed = 0
        self.tests_failed = 0

        self.now = datetime.now()

    def test_and_raise_errors(self,
                              parsing_method: Callable,
                              file_name: str,
                              entity_type: Type):
        print(f'Testing {entity_type}, file: "{file_name}"\n')
        self.test_parser(parsing_method, file_name, entity_type)
        if self.tests_failed:
            print(f'{self.tests_passed} tests passed, {self.tests_failed} tests failed')
        else:
            print(f'{self.tests_passed} tests passed')
        if not self.tests_failed and not len(self.errors):
            return

        error_message = ''
        err_by_ant = OrderedDict()
        for er in self.errors:
            if er.case_index in err_by_ant:
                err_by_ant[er.case_index].append(er)
            else:
                err_by_ant[er.case_index] = [er]

        for case_index in err_by_ant:
            if case_index >= 0:
                error_message += str(self.test_cases[case_index]) + '\n\n'
            else:
                error_message += 'Test case parsing errors:\n\n'
            for error in err_by_ant[case_index]:
                error_message += f'{error.check_index}) {error.message}'
                error_message += '\n-----------------------------------------\n'

        raise Exception(error_message)

    def test_parser(self,
                    parsing_method: Callable,
                    file_name: str,
                    entity_type: Type):

        self.file_path = file_name
        if not os.path.isfile(self.file_path):
            self.file_path = os.path.join(lexnlp_test_path, self.file_path)
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f'File "{file_name}" was not found')

        self.parsing_method = parsing_method
        self.entity_type = entity_type
        self.process_file()

    def process_file(self):
        self.read_cases()
        self.process_cases()

    def process_cases(self) -> Tuple[int, int]:
        for case_index in range(len(self.test_cases)):
            case = self.test_cases[case_index]
            try:
                ants = self.parsing_method(case.text)
            except Exception as e:  # pylint:disable=broad-except
                self.errors.append(ParsingError(
                    message=f'Exception while parsing {case_index} case.',
                    exception=e))
                continue
            errors_before = len(self.errors)

            if isinstance(ants, types.GeneratorType):
                ants = list(ants)

            self.check_case_annotations(ants, case, case_index)

            if len(self.errors) > errors_before:
                self.tests_failed += 1
            else:
                self.tests_passed += 1

        return self.tests_passed, self.tests_failed

    def check_case_annotations(self,
                               ants: List[TextAnnotation],
                               case: TypedAntTestCase,
                               case_index: int):
        count = len(ants)
        if count != case.total:
            self.errors.append(ParsingError(
                message=f'Read {count} annotations instead of {case.total}:\n{case}'))

        # individual checks (index >= 0)
        for check_index in range(count):
            ant = ants[check_index]
            checks = [c for c in case.field_checks if c.index == check_index]
            for check in checks:
                self.process_one_check(ant, check, case_index, check_index)

        # checks, defined for all annotations
        for i in range(count):
            for j in range(len(case.field_checks)):
                check = case.field_checks[j]
                if check.check_all:
                    self.process_one_check(ants[i], check, case_index, j)

    def process_one_check(self,
                          ant: TextAnnotation,
                          check: TypedFieldCheck,
                          case_index: int,
                          check_index: int) -> None:
        try:
            val = check.get_ant_field_value(ant)
        except Exception as e:  # pylint:disable=broad-except
            self.errors.append(ParsingError(
                message=f'Error getting annotation value {check.path_string}',
                case_index=case_index,
                exception=e,
                check_index=check_index))
            return

        equals, cmp_ok = check.compare_values(val)
        if equals:
            return
        if not cmp_ok:
            self.errors.append(ParsingError(message=check.last_error,
                                            case_index=case_index,
                                            check_index=check_index))
            return

        self.errors.append(ParsingError(
            message=f'Checking {check.path_string}: value "{val}" ' +
                    f'should be {check.comparison_string} "{check.value}"',
            case_index=case_index,
            check_index=check_index))

    def read_cases(self):
        """
        Sample file contains:
### comment line starts with "###"
--------
1.11.SCADA System means a supervisory control and data acquisition system such
as the S/3 Software or Licensee's OASyS(R) product.
--------
total=1
0)locale="en"
0)trademark="OASyS (R)"
        """
        with codecs.open(self.file_path, encoding=self.encoding, mode='r') as of:
            lines = of.readlines()

        for line in lines:
            line = line.strip('\n')
            if line.startswith('###'):
                continue  # comment

            if line.startswith('----'):
                if self.test_case.is_completed:
                    self.test_cases.append(self.test_case)
                    self.test_case = TypedAntTestCase()
                    continue
                self.test_case.text_filled = True
                continue

            if line.startswith('total='):
                self.test_case.total = int(line[len('total='):])
                continue

            if not line:
                if not self.test_case.text_filled:
                    self.test_case.text += '\n'
                continue

            if not self.test_case.text_filled:
                self.test_case.text += line
                self.test_case.text += '\n'
                continue

            line = self.substitute_spec_entries(line)

            fcheck = TypedFieldCheck.parse(line)
            if fcheck:
                self.test_case.field_checks.append(fcheck)

        if self.test_case.text_filled:
            self.test_cases.append(self.test_case)

    def substitute_spec_entries(self, line: str) -> str:
        line = line.replace('$YEAR$', str(self.now.date().year))
        line = line.replace('$MONTH$', str(self.now.date().month))
        line = line.replace('$DAY$', str(self.now.date().day))
        return line
