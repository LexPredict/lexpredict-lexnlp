"""Company types and abbreviations.

This module defines constants and configuration for company types, including their full descriptions, common short
names, and abbreviations.

Todo:
  * Include automated generation from raw source.
  * Expand full description list
"""

import csv
import os


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


_COMPANY_TYPES = [
    'A.G.', 'AG', 'B.V.', 'C.A.', 'C.V.', 'Corp.', 'Corporation',
    'G.P.', 'Inc.', 'Incorporated', 'K.K.', 'L.L.C.', 'L.L.L.P.', 'L.L.P.', 'L.P.',
    'LLC.', 'LLP.', 'Lda.', 'Ltd.', 'Ltda.', 'N.A.', 'National Association',
    'N.V.', 'Pte. Ltd.',
    'S de R.L. de C.V.', 'S. DE R.L. DE C.V.', 'S. De R.L. De C.V.',
    'S. De R.L. de C.V.', 'S. de R. L. de C.V.', 'S. de R.L. de C.V.',
    'S.A.', 'S.A. DE C.V.', 'S.A. De C.V.', 'S.A. de C.V.', 'S.A.R.L.',
    'S.A.S.', 'S.A.U.', 'S.A.de C.V.', 'S.C.', 'S.C.A.',
    'S.L.', 'S.L.U.', 'S.R.L.', 'S.R.L. de C.V.', 'S.R.O.', 'S.a.r.l.',
    'S.de R.L. de C.V.', 'S.r.l.', 'Sdn. Bhd.', 's.r.o.', 'CO'
]


default_company_types_file_path = os.path.join(os.path.dirname(__file__), 'company_types.csv')


def get_company_types(file_path=None):
    ret = dict()
    file_path = file_path or default_company_types_file_path
    with open(file_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            alias_dot = row['Alias'].strip(' ').lower()
            alias = alias_dot.strip('.')
            abbr = row['Abbreviation'].strip()
            label = row['Label'].strip()
            ret[alias] = dict(
                abbr=abbr,
                label=label)
            if alias_dot != alias:
                ret[alias_dot] = dict(
                    abbr=abbr,
                    label=label)
    return ret


COMPANY_TYPES = get_company_types()

COMPANY_DESCRIPTIONS = ['Trust Bank', 'Trust Company', 'Trust',
                        'Bank', 'Company', 'Partnership']
