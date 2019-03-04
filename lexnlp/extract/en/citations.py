"""Citation extraction for English.

This module implements citation extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""
# pylint: disable=bare-except

# Imports
from typing import Generator

import regex as re
from reporters_db import EDITIONS, REPORTERS

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

CITATION_PTN = r"""
(?:[\s,:\(]|^)
(
(\d+)\s+
({reporters})\s+
(\d+)
(?:,\s+(\d+(?:\-\d+)?))?
(?:\s+\((.+?)?(\d{{4}})\))?
)
(?:\W|$)
""".format(reporters='|'.join([re.escape(i) for i in EDITIONS]))
CITATION_PTN_RE = re.compile(CITATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_citations(text, return_source=False, as_dict=False) -> Generator:
    """
    Get citations.
    :param text:
    :param return_source:
    :param as_dict:
    :return: tuple or dict
    (volume, reporter, reporter_full_name, page, page2, court, year[, source text])
    """

    for source_text, volume, reporter, page, page2, court, year\
            in CITATION_PTN_RE.findall(text):
        try:
            reporter_data = REPORTERS[EDITIONS[reporter]]
            reporter_full_name = ''
            if len(reporter_data) == 1:
                reporter_full_name = reporter_data[0]['name']
            elif year:
                for period_data in reporter_data:
                    if reporter in period_data['editions']:
                        start = period_data['editions'][reporter]['start'].year
                        end = period_data['editions'][reporter]['end']
                        if (end and start <= int(year) <= end.year) or start <= int(year):
                            reporter_full_name = period_data['name']
            item = (int(volume),
                    reporter,
                    reporter_full_name,
                    int(page),
                    page2 or None,
                    court.strip(', ') or None,
                    int(year) if year.isdigit() else None)
            if return_source:
                item += (source_text.strip(),)
            if as_dict:
                keys = ['volume', 'reporter', 'reporter_full_name',
                        'page', 'page2', 'court', 'year', 'citation_str']
                item = {keys[n]: val for n, val in enumerate(item)}
            yield item
        except KeyError:
            pass
