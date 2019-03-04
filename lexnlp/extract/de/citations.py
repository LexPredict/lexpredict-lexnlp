"""Citation extraction for German.

This module implements citation extraction functionality in German.

Todo:
  * Improved unit tests and case coverage
"""
# pylint: disable=bare-except

import regex as re

from lexnlp.extract.en.dates import get_dates


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


CITATION_PTN = r"""
(?P<text>
(?:
(?:
(?:
(?:Artikel\s(?P<article>\d+))|
(?:\sSatz\s(?P<sentence>\d+))|
(?:\s(?:Nummer|Nr\.)\s(?P<number>(?:\d+|\s*und |\s*bis\s)+))|
(?:\sAbsatz(?:es)?\s(?P<paragraph>(?:\d+|\s*und\s)+))|
(?:\sUnterabsatz(?:es)?\s(?P<subparagraph>(?:\d+|\s*und\s)+))|
(?:\sBuchstabe\s(?P<letter>(?:\w|\s*und\s)+))
)*
(?:\sdes\sGesetzes|\sder\sVerordnung)
)?\s*
(?:vom|v\.)\s(?P<date>\d{1,2}\.\s\S+\s\d{4}),?\s
)?
\(?BGBl\.?\s(?:(?P<year>\d{4})\s)?(?P<part>I{1,3})\sS\.\s(?:(?P<page>\d+)(?:\s\((?P<year>\d{4})\))?(?:,\s)?)+\)?)
"""


SECOND_CITATION_PTN = r"""
(?P<text>BGBl[IS\.,\s\d]+;\s(?P<year>\d{4})\s(?P<part>I{1,3})\sS\.\s(?:(?P<page>\d+)(?:,\s)?)+)
"""

CITATION_RANGE_PTN = r"""
(?P<text>BGBl\.?\s(?P<part>I{1,3})\s(?P<year>\d{4}),\s(?P<page>\d+\s*[—-]\s*\d+))
"""

re_flags = re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE
CITATION_PTN_RE = re.compile(CITATION_PTN, re_flags)
SECOND_CITATION_PTN_RE = re.compile(SECOND_CITATION_PTN, re_flags)
CITATION_RANGE_PTN_RE = re.compile(CITATION_RANGE_PTN, re_flags)


def get_citations(text):
    """
    Get citations containing "BGBl"
    :param text: str
    :return: yields dict
    """

    for ptn in [CITATION_PTN_RE, SECOND_CITATION_PTN_RE, CITATION_RANGE_PTN_RE]:
        for match in ptn.finditer(text):
            capture = match.capturesdict()
            date = ''.join(capture.get('date', ''))
            if date:
                try:
                    date = str(list(get_dates(date, 'de'))[0]['value'])
                except:
                    pass
            yield dict(
                location_start=match.start(),
                location_end=match.end(),
                text=capture['text'][0],
                article=''.join(capture.get('article', '')),
                number=''.join(capture.get('number', '')),
                subparagraph=''.join(capture.get('subparagraph', '')),
                sentence=''.join(capture.get('sentence', '')),
                paragraph=''.join(capture.get('paragraph', '')),
                letter=''.join(capture.get('letter', '')),
                date=date,
                part=capture['part'][0],
                page=', '.join(capture['page']),
                year=', '.join(capture.get('year', ''))
            )


def get_citation_list(text):
    return list(get_citations(text))
