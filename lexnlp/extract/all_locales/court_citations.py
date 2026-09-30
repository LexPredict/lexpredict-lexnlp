# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator

from lexnlp.extract.all_locales.languages import LANG_DE, Locale, get_language_routine
from lexnlp.extract.common.annotations.court_citation_annotation import CourtCitationAnnotation
from lexnlp.extract.de.court_citations import get_court_citation_annotations as get_court_citation_annotations_de


ROUTINE_BY_LOCALE = {
    LANG_DE.code: get_court_citation_annotations_de
}


def get_court_citation_annotations(locale: str, text: str, language: str = None) -> \
        Generator[CourtCitationAnnotation, None, None]:
    locale_language = Locale(locale).language
    routine = get_language_routine(locale, ROUTINE_BY_LOCALE, LANG_DE)
    annotation_language = language or (
        locale_language
        if locale_language in ROUTINE_BY_LOCALE
        else LANG_DE.code
    )
    yield from routine(text, annotation_language)
