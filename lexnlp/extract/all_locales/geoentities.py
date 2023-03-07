# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator, List, Optional, Tuple, Dict

from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
from lexnlp.extract.en.dict_entities import DictionaryEntry
from lexnlp.extract.all_locales.languages import LANG_EN, LANG_DE, DEFAULT_LANGUAGE, Locale
from lexnlp.extract.en.geoentities import get_geoentity_annotations as get_geoentity_annotations_en
from lexnlp.extract.de.geoentities import get_geoentity_annotations as get_geoentity_annotations_de


ROUTINE_BY_LOCALE = {
    LANG_EN.code: get_geoentity_annotations_en,
    LANG_DE.code: get_geoentity_annotations_de
}


def get_geoentity_annotations(
        locale: str,
        text: str,
        geo_config_list: List[DictionaryEntry],
        conflict_resolving_field: str = 'none',
        priority_direction: str = 'asc',
        text_languages: List[str] = None,
        min_alias_len: Optional[int] = None,
        prepared_alias_ban_list: Optional[
            Dict[str, Tuple[List[str], List[str]]]] = None,
        simplified_normalization: bool = False) -> Generator[GeoAnnotation, None, None]:
    routine = ROUTINE_BY_LOCALE.get(Locale(locale).language, ROUTINE_BY_LOCALE[DEFAULT_LANGUAGE.code])
    yield from routine(text, geo_config_list, conflict_resolving_field,
                       priority_direction, text_languages, min_alias_len,
                       prepared_alias_ban_list, simplified_normalization)
