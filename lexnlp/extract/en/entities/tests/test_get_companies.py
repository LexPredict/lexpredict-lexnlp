from unittest import TestCase

from lexnlp.extract.en.entities.nltk_maxent import get_company_annotations

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestGetCompanies(TestCase):
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
        text = 'DTC is a wholly-owned subsidiary of The Depository Trust and Clearing Corporation ("DTCC").'
        comps = list(get_company_annotations(text))
        self.assertEqual('The Depository Trust', comps[0].name)

        text = 'DTC is a wholly-owned subsidiary of The Depository Trust & Clearing Corporation ("DTCC").'
        comps = list(get_company_annotations(text))
        self.assertEqual('The Depository Trust & Clearing', comps[0].name)

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
        text = """
        /NOR <FEFF004200720075006b00200064006900730073006500200069006e006e007300740069006c006c0069006e00670065006e006500.
        """
        res = list(get_company_annotations(text))
        self.assertEqual(0, len(res))
