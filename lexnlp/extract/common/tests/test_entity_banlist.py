# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.common.entities.entity_banlist import EntityBanListItem


def test_simple_pattern():
    ptrn = EntityBanListItem('Company')
    assert ptrn.check('company')
    assert ptrn.check('Company')
    assert ptrn.check(' company')
    assert not ptrn.check('simple company')

    ptrn = EntityBanListItem('Company', trim_phrase=False)
    assert not ptrn.check(' company')

    ptrn = EntityBanListItem('Company', ignore_case=False)
    assert not ptrn.check('company')


def test_regex_pattern():
    ptrn = EntityBanListItem(r'(?:the\s+)?company', is_regex=True)
    assert ptrn.check('company')
    assert ptrn.check('The Company')
    assert ptrn.check('The Company ')
    assert not ptrn.check('The-Company')


def test_read_csv():
    path = os.path.join(f'{lexnlp_test_path}/lexnlp/extract/common/entities',
                        'en_banlist_full.csv')
    items = EntityBanListItem.read_from_csv(path)
    assert len(items) > 1


def test_read_one_col_csv():
    path = os.path.join(f'{lexnlp_test_path}/lexnlp/extract/common/entities',
                        'en_banlist_one_col.csv')
    items = EntityBanListItem.read_from_csv(path)
    assert len(items) > 1
    assert items[0].ignore_case
    assert not items[0].is_regex
