from enum import Enum

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AnnotationType(Enum):
    act = 1
    amount = 2
    citation = 3
    condition = 4
    constraint = 5
    copyright = 6
    court = 7
    court_citation = 8
    cusip = 9
    date = 10
    definition = 11
    distance = 12
    duration = 13
    geoentity = 14
    money = 15
    percent = 16
    pii = 17
    phone = 18
    ssn = 19
    ratio = 20
    regulation = 21
    trademark = 22
    url = 23
    laws = 24
