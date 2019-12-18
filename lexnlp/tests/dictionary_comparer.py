from typing import List

from lexnlp.tests.values_comparer import values_look_equal

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DictionaryComparer:
    def __init__(self,
                 check_order: bool = True,
                 allow_extra_key: bool = False,
                 number_precision_percent: float = 0.001):
        self.check_order = check_order
        self.allow_extra_key = allow_extra_key
        self.number_precision_percent = number_precision_percent

    def compare_list_of_dicts(
            self,
            expected: List[dict],
            actual: List[dict]) -> List[str]:
        errors = []
        if len(expected) != len(actual):
            errors.append(f'Parsed items counts missmatch: ' +
                          f'expected {len(expected)}, got {len(actual)} items')
        if not actual or not expected:
            return errors

        for i in range(len(expected)):
            exp = expected[i]

            if self.check_order:
                if i >= len(actual):
                    break
                act = actual[i]
                itm_errors = self.check_dicts_equal(exp, act)
                errors += [f'{i}): {e}' for e in itm_errors]
            else:
                # is there any actual item that matches expected one?
                best_effort = None
                best_index = 0
                for j in range(len(actual)):
                    act = actual[j]
                    itm_errors = self.check_dicts_equal(exp, act)
                    if best_effort is None or len(best_effort) > len(itm_errors):
                        best_effort = itm_errors
                        best_index = j
                if not best_effort:
                    continue
                errors += [f'{i} - {best_index}): {e}' for e in best_effort]

        return errors

    def check_dicts_equal(self,
                          expected: dict, actual: dict) -> List[str]:
        errors = []

        for key in expected:
            if key not in actual:
                errors.append(f'key "{key}"\'s missed in actual data')
        if not self.allow_extra_key:
            for key in actual:
                if key not in expected:
                    errors.append(f'got extra key ("{key}") in actual data')

        for key in expected:
            if key not in actual:
                continue
            exp_val = expected[key]
            act_val = actual[key]
            if exp_val == act_val:
                continue
            if values_look_equal(exp_val, act_val):
                continue
            errors.append(f'actual[\'{key}\'] = ' +
                          f'"{act_val}" that differs from expected ("{exp_val}")')
        return errors
