"""Company types and abbreviations.

This module defines constants and configuration for company types, including their full descriptions, common short
names, and abbreviations.

Todo:
  * Include automated generation from raw source.
  * Expand full description list
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

COMPANY_TYPES = ['Inc.', 'L.L.C.', 'Ltd.', 'L.P.', 'S.A.', 'Corp.', 'Corporation', 'Incorporated',
                 'S.A. de C.V.', 'S. de R.L. de C.V.', 'S.L.', 'AG', 'A.G.', 'N.A.',
                 'B.V.', 'LLC.', 'LLP.', 'Lda.', 'Ltda.', 'S.R.L.', 's.r.o.',
                 'S.A.S.', 'S.A. DE C.V.', 'C.A.', 'Corp.', 'S.L.U.', 'S.A. De C.V.',
                 'S. DE R.L. DE C.V.', 'L.L.P.', 'K.K.', 'C.V.', 'N.A.', 'S.r.l.',
                 'S.A.R.L.', 'S. de R. L. de C.V.', 'S. De R.L. De C.V.', 'S.R.L. de C.V.', 'G.P.',
                 'S.A.de C.V.', 'L.P.', 'N.V.', 'S de R.L. de C.V.', 'S.C.A.',
                 'Sdn. Bhd.', 'S.R.O.', 'L.L.L.P.', 'S.de R.L. de C.V.', 'Pte. Ltd.',
                 'S.A.U.', 'S.C.', 'S.a.r.l.', 'S. De R.L. de C.V.']
COMPANY_DESCRIPTIONS = ['Bank', 'Trust', 'Company', "Partnership"]
