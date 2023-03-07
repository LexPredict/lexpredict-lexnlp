"""Citation extraction for German.

This module implements citation extraction functionality in German.

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

import regex as re
from typing import Dict, Generator, List

from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.extract.common.annotations.citation_annotation import CitationAnnotation
from lexnlp.extract.en.dates import get_dates


class DeCitationParser:
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

    @classmethod
    def get_citation_annotations(cls, text: str) -> \
            Generator[CitationAnnotation, None, None]:
        """
        Get citations containing "BGBl"
        :param text: str
        :return: yields dict
        """

        for ptn in [cls.CITATION_PTN_RE, cls.SECOND_CITATION_PTN_RE, cls.CITATION_RANGE_PTN_RE]:
            for match in ptn.finditer(text):
                capture = match.capturesdict()
                date = ''.join(capture.get('date', ''))
                if date:
                    try:
                        date = str(list(get_dates(date, 'de'))[0]['value'])
                    except:
                        pass

                ant = CitationAnnotation(coords=match.span(),
                                         text=capture['text'][0],
                                         paragraph=''.join(capture.get('paragraph', '')),
                                         subparagraph=''.join(capture.get('subparagraph', '')),
                                         letter=''.join(capture.get('letter', '')),
                                         date=date,
                                         part=capture['part'][0],
                                         locale='de')
                ant.article = TextAnnotation.get_int_value(
                    ''.join(capture.get('article', '')))
                ant.number = TextAnnotation.get_int_value(
                    ''.join(capture.get('number', '')))
                ant.sentence = TextAnnotation.get_int_value(
                    ''.join(capture.get('sentence', '')))

                page_range = ', '.join(capture['page'])
                page = TextAnnotation.get_int_value(page_range)
                if page:
                    ant.page = page
                else:
                    ant.page_range = page_range

                volume_str = ''.join(capture.get('number', ''))
                volume = TextAnnotation.get_int_value(volume_str)
                if volume:
                    ant.volume = volume
                else:
                    ant.volume_str = volume_str

                year_str = ', '.join(capture.get('year', ''))
                year = TextAnnotation.get_int_value(year_str)
                if year:
                    ant.year = year
                else:
                    ant.year_str = year_str

                yield ant


def get_citation_annotations(text: str) -> \
        Generator[CitationAnnotation, None, None]:
    yield from DeCitationParser.get_citation_annotations(text)


def get_citation_annotation_list(text: str) -> List[CitationAnnotation]:
    return list(get_citation_annotations(text))


def get_citations(text: str) -> Generator[Dict, None, None]:
    """
    Get citations containing "BGBl"
    :param text: str
    :return: yields dict
    """
    for ant in get_citation_annotations(text):
        yield dict(
            location_start=ant.coords[0],
            location_end=ant.coords[1],
            text=ant.text,
            article=str(ant.article) if ant.article else '',
            number=str(ant.volume) if ant.volume else ant.volume_str,
            sentence=str(ant.sentence) if ant.sentence else '',
            date=ant.date,
            page=str(ant.page) if ant.page else ant.page_range,
            year=str(ant.year) if ant.year else ant.year_str,
            letter=ant.letter,
            paragraph=ant.paragraph,
            subparagraph=ant.subparagraph,
            part=ant.part
        )


def get_citation_list(text) -> List[Dict]:
    return list(get_citations(text))
