# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator

from lexnlp.extract.all_locales.languages import (
    DEFAULT_LANGUAGE,
    LANG_DE,
    LANG_EN,
    get_language_routine,
)
from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.en.definitions import get_definition_annotations as get_definition_annotations_en
from lexnlp.extract.de.definitions import get_definition_annotations as get_definition_annotations_de


ROUTINE_BY_LOCALE = {
    LANG_EN.code: get_definition_annotations_en,
    LANG_DE.code: get_definition_annotations_de
}


def get_definition_annotations(
        locale: str,
        text: str,
        **kwargs) \
        -> Generator[DefinitionAnnotation, None, None]:
    routine = get_language_routine(
        locale,
        ROUTINE_BY_LOCALE,
        DEFAULT_LANGUAGE,
    )
    yield from routine(text, **kwargs)
