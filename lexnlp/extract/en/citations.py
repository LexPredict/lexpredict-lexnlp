"""Citation extraction for English.

This module implements citation extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=bare-except

from typing import Dict, Generator, List, Tuple, Union

import regex as re
from reporters_db import EDITIONS, REPORTERS

from lexnlp.extract.common.annotations.citation_annotation import CitationAnnotation


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


def get_citations(
    text: str,
    return_source: bool = False,
    as_dict: bool = False,
) -> Generator[Union[Dict, Tuple], None, None]:
    """
    Get a list of citations.

    Args:
        text (str):
            An input string.

        return_source (bool=False):
            Whether to return the source.

        as_dict (bool=False):
            Whether to return a dictionary. If False (default), returns tuples.

    Returns:
        A list of tuples or dictionaries representing citations.
    """
    for ant in get_citation_annotations(text):
        if as_dict:
            yield ant.to_dictionary_legacy()
        else:
            item = (ant.volume,
                    ant.reporter,
                    ant.reporter_full_name,
                    ant.page,
                    ant.page_range,
                    ant.court,
                    ant.year)
            if return_source:
                item += (ant.source,)
            yield item


def get_citation_list(
    text: str,
    return_source: bool = False,
    as_dict: bool = False,
) -> List[Union[Dict, Tuple]]:
    """
    Get a list of citations.

    Args:
        text (str):
            An input string.

        return_source (bool=False):
            Whether to return the source.

        as_dict (bool=False):
            Whether to return a dictionary. If False (default), returns tuples.

    Returns:
        A list of tuples or dictionaries representing citations.
    """
    return list(
        get_citations(
            text=text,
            return_source=return_source,
            as_dict=as_dict,
        )
    )


def get_citation_annotations(text: str) -> Generator[CitationAnnotation, None, None]:
    """
    Get citation annotations.

    Args:
        text (str):

    Yields:
        CitationAnnotations
    """
    for match in CITATION_PTN_RE.finditer(text):
        source_text, volume, reporter, \
            page, page2, court, year = match.groups()
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

            ant = CitationAnnotation(coords=match.span(),
                                     volume=int(volume) if volume else None,
                                     year=int(year) if year and year.isdigit() else None,
                                     reporter=reporter,
                                     reporter_full_name=reporter_full_name,
                                     page=int(page) if page else None,
                                     page_range=page2,
                                     source=source_text.strip(),
                                     court=court.strip(', ') if court else None,
                                     locale='en')

            yield ant
        except KeyError:
            pass


def get_citation_annotation_list(text: str) -> List[CitationAnnotation]:
    """
    Get citation annotations.

    Args:
        text (str):

    Returns:
        A list of CitationAnnotations.
    """
    return list(get_citation_annotations(text))
