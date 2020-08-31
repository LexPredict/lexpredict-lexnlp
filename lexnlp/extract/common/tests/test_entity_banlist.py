"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""

# -*- coding: utf-8 -*-

import os

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.common.entities.entity_banlist import EntityBanListItem

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
