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

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from lexnlp.extract.en.dict_entities import DictionaryEntry
from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS, CompanyDescriptor
from lexnlp.extract.en.entities.company_detector import CompanyDetector
from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.common.entities.entity_banlist import BanListUsage, EntityBanListItem
from lexnlp.extract.en.entities.nltk_maxent import get_company_annotations


def load_entities_dict():
    base_path = os.path.join(lexnlp_test_path, 'lexnlp/extract/en/tests/test_geoentities')
    entities_fn = os.path.join(base_path, 'geoentities.csv')
    aliases_fn = os.path.join(base_path, 'geoaliases.csv')
    return DictionaryEntry.load_entities_from_files(entities_fn, aliases_fn)


_CONFIG = list(load_entities_dict())


class TestGetCompanies(TestCase):

    def test_get_unpreffixed_companies(self):
        texts = ["MI 48226 From: Company City of Detroit, Contact ROMONA JONES Address COLEMAN",
                 "Order Amount 51.000.00 USD, Sold To City of Detroit, COLEMAN A YOUNG MUNICIPAL CENTER 2",
                 "MI 48226 &nbsp. Supplier GAYANGA Inc. / CO AMERIFACTORS LACRESHA"]
        all_companies = []
        for text in texts:
            comps = list(get_company_annotations(
                text,
                banlist_usage=BanListUsage(use_default_banlist=False)))
            all_companies += comps
        self.assertEqual(1, len(all_companies))

    def test_copyright(self):
        text = "Copyright (c) 2019, Moody's Corporation, Moody's Investors Service, Inc., " + \
               "Moody's Analytics, Inc. and/or their licensors and affiliates (collectively, \"MOODY's\")."
        comps = list(get_company_annotations(text))
        self.assertEqual(2, len(comps))
        self.assertEqual("Moody\'s Corporation, Moody\'s Investors Service", comps[0].name)
        self.assertEqual('Moody\'s Analytics', comps[1].name)

    def test_with_wo_apostrophe(self):
        text = 'McDonalds Inc.: Burgers, Fries & More. Quality Ingredients.'
        comps = list(get_company_annotations(text))
        self.assertEqual(1, len(comps))

        text = 'McDonald\'s Inc.: Burgers, Fries & More. Quality Ingredients.'
        comps = list(get_company_annotations(text))
        self.assertEqual(1, len(comps))

    def test_with_apostrophe(self):
        text = 'RTC is a wholly-owned subsidiary of The Repository Trust and Clearing Corporation ("RTCC").'
        comps = list(get_company_annotations(text))
        self.assertEqual('The Repository Trust', comps[0].name)

        text = 'DTC is a wholly-owned subsidiary of The Depository Trust & Clearing Corporation ("DTCC").'
        comps = list(get_company_annotations(text))
        self.assertEqual('The Depository Trust & Clearing', comps[0].name)

    def test_with_forwardslash(self):
        # TODO: this should eventually extract both companies
        text = 'Supplier GAYANGA CO / CO AMERIFACTORS'
        comps = list(get_company_annotations(text))
        self.assertEqual('Supplier GAYANGA', comps[0].name)
        self.assertEqual('CO', comps[0].company_type)

    def test_num_preffixed(self):
        text = """01077.ROW Supplier GAYANGA CO / CO AMERIFACTORS"""
        comps = list(get_company_annotations(text))
        self.assertEqual(1, len(comps))
        self.assertEqual('Supp', comps[0].name[:4])

    def test_banlisted(self):
        text = 'Depository Bank is a wholly-owned subsidiary of The Repository Trust and Clearing Corporation ("RTCC").'
        comps = list(get_company_annotations(text))
        self.assertEqual(len(comps), 2)

        comps = list(get_company_annotations(
            text, banlist_usage=BanListUsage(use_default_banlist=False)))
        self.assertEqual(len(comps), 3)

    def test_mixed_banlisted(self):
        text = """Hereinafter, the Issuing Bank is a wholly-owned subsidiary of 
The Repository Trust and Clearing Corporation ("RTCC")."""
        comps = list(get_company_annotations(text))
        self.assertEqual(len(comps), 2)

    def test_custom_banlisted(self):
        text = 'Depository Bank is a partially-owned subsidiary of The Depository Trust and Cleaning Corporation ("DTCC").'
        custom_bl = [EntityBanListItem('Cleaning')]
        comps = list(get_company_annotations(
            text, banlist_usage=BanListUsage(banlist=custom_bl,
                                             append_to_default=True)))
        self.assertEqual(1, len(comps))

        comps = list(get_company_annotations(
            text, banlist_usage=BanListUsage(banlist=custom_bl,
                                             use_default_banlist=False,
                                             append_to_default=False)))
        self.assertEqual(len(comps), 2)

    def test_default_banlisted(self):
        text = 'Depository Bank is a partially-owned subsidiary of The Depository Thrust and Clearing Agency ("DTCA").'
        comps = list(get_company_annotations(text))
        self.assertEqual(1, len(comps))

    def test_with_colon(self):
        text = 'this is McDonald\'s Incorporated: Burgers, blah-blah'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ("McDonald's", 'Incorporated', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Inc'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Inc', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Marketing Inc'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Marketing', 'Inc', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Inc.'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Inc', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Incorporated.'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Incorporated', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Incorporated'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Incorporated', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Corp'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Corp', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Corp.'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Corp', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Corp: good old company.'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Corp', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Corp - good old company.'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Corp', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Incorporated: good old company'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Incorporated', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Incorporated - good old company'
        res = list(get_company_annotations(text))[0]
        self.assertEqual((res.name,
                          res.company_type_full,
                          res.company_type_abbr,
                          res.company_type_label,
                          res.name_abbr, res.description),
                         ('Sitwell Housing', 'Incorporated', 'CORP', 'Corporation', None, None))

        text = 'Sitwell Housing Busted'
        res = list(get_company_annotations(text))
        self.assertEqual(0, len(res))

    def test_reg_back(self):
        # here we check that the test doesn't hang
        text = '/NOR <FEFF004200720075006b002000640069007300730065002000' + \
               '69006e006e007300740069006c006c0069006e00670065006e006500.'

        res = list(get_company_annotations(text))
        self.assertEqual(0, len(res))

    def test_custom_company(self):
        comp_types = dict(COMPANY_TYPES)
        comp_types['OOO'] = CompanyDescriptor('ooo', 'LLC', 'Company')
        detector = CompanyDetector(comp_types, COMPANY_DESCRIPTIONS)

        text = 'Sitwell Housing OOO - good old company.'
        res = list(detector.get_company_annotations(text, strict=False))
        self.assertEqual(1, len(res))

    def test_wrong_pos(self):
        text = '''This Commercial Lease Agreement ("Lease") is made and effective June 1, 2010, by 
and between Rawdermet, inc. ("Landlord/Tenant") and Resocoat, inc ("Sub- 
Tenant"). This is a sublease to the current lease held by Rawdermet, Inc. with  
Sheeman Properties, LLC..'''
        comps = list(get_company_annotations(text))
        self.assertEqual(4, len(comps))
        self.assertEqual('Rawdermet', comps[0].name)
        self.assertEqual('Resocoat', comps[1].name)
        self.assertEqual((94, 108), comps[0].coords)
        self.assertEqual((134, 147), comps[1].coords)
        self.assertEqual('Corporation', comps[0].company_type_label)
        self.assertEqual('Corporation', comps[1].company_type_label)
