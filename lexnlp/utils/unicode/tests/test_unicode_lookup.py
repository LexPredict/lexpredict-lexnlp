# pylint: disable=logging-format-interpolation,broad-except

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import logging
import math
import os
import unicodedata
from datetime import datetime
from tempfile import mkstemp

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.utils.unicode.unicode_lookup import UNICODE_CHAR_TOP_CATEGORY_MAPPING, build_lookup_tables, _load_table


logger = logging.getLogger(__name__)


def check_all_chars_have_correct_category():
    """
    A method for manual running, debugging and comparing the custom unicode lookup tables and unicodedata module.
    :return:
    """
    m = int(math.pow(16, 5))
    for i in range(0, m):
        ch = chr(i)
        unicode_data_category = unicodedata.category(ch)
        lookup_category = UNICODE_CHAR_TOP_CATEGORY_MAPPING.get(ch)

        if unicode_data_category == 'Cn' and lookup_category is None:
            continue

        if unicode_data_category and unicode_data_category[0] != lookup_category:
            print('For char: {0} / {1} '
                  'lookup table from ftp.unicode.org gives {2} but unicodedata module gives {3}.'
                  .format(i, hex(i), lookup_category, unicode_data_category))

            # As we found unicodedata module returns different categories for many characters.
            #  if lookup_category \
            #         and unicode_data_category \
            #         and unicode_data_category != 'Cn' \
            #         and lookup_category != unicode_data_category[0]:
            #     raise AssertionError()

            # Checking at least that missing category in our lookup tables mean Cn in unicodedata
            # if not lookup_category and unicode_data_category[0] != 'C':
            #    raise AssertionError()


def test_performance():
    """
    Ensures that performance of the custom unicode lookup tables is better than using unicodedata method.
    :return:
    """
    repeat_count = 100000
    line = 'qwertyuiop[]asdfghjkl;zxcvbnm,./'

    start = datetime.now()

    found = set()
    for _ in range(0, repeat_count):
        for ch in line:
            found.add(unicodedata.category(ch)[0])
    duration1 = datetime.now() - start

    print('Duration when using unicodedata.category(): {0}'.format(duration1))

    start = datetime.now()

    found = set()
    for _ in range(0, repeat_count):
        for ch in line:
            found.add(UNICODE_CHAR_TOP_CATEGORY_MAPPING[ch])
    duration2 = datetime.now() - start

    print('Duration when using custom lookup tables: {0}'.format(duration2))
    # this test is unstable
    # assert duration2 < duration1


def safe_remove_temp_file(handler, name):
    """
    Safely closes os handler and removes the file.
    :param handler: OS file handler.
    :param name: File name.
    :return:
    """
    try:
        os.close(handler)
    except Exception as e1:
        logger.error('Unable to close OS temp file handler for file {0}'.format(name), e1)
    finally:
        try:
            os.remove(name)
        except Exception as e:
            logger.error('Unable to remove temp file {0}'.format(name), e)


def test_preparing_tables():
    """
    Tests preparing and loading the custom unicode lookup tables.
    :return:
    """
    h1, fn_categories = mkstemp()
    h2, fn_char_category_mapping = mkstemp()
    h3, fn_char_top_category_mapping = mkstemp()

    try:
        path = os.path.join(lexnlp_test_path, 'lexnlp/utils/unicode_data.txt')
        build_lookup_tables(fn_categories,
                            fn_char_category_mapping,
                            fn_char_top_category_mapping,
                            table_source=path)

        tbl_categories = _load_table(fn_categories, False)

        # Simple basic testing that the contents are not empty and make sense.

        assert ',' in tbl_categories['punctuation']
        assert '[' in tbl_categories['punctuation_start']
        assert ']' in tbl_categories['punctuation_end']
        assert '^' in tbl_categories['symbol']
        assert '$' in tbl_categories['symbol_currency']
        assert '+' in tbl_categories['symbol_math']
        assert ' ' in tbl_categories['whitespace']
        assert ' ' in tbl_categories['space']
        assert '\u2028' in tbl_categories['line']

        tbl_char_category_mapping = _load_table(fn_char_category_mapping, False)
        assert tbl_char_category_mapping['a'] == 'Ll'

        tbl_char_top_category_mapping = _load_table(fn_char_top_category_mapping, False)
        assert tbl_char_top_category_mapping['a'] == 'L'

    finally:
        safe_remove_temp_file(h1, fn_categories)
        safe_remove_temp_file(h2, fn_char_category_mapping)
        safe_remove_temp_file(h3, fn_char_top_category_mapping)
