# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator, List

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.en.dict_entities import DictionaryEntry, find_dict_entities, conflicts_take_first_by_id
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation


def get_court_annotations(
        locale: str,
        text: str,
        court_config_list: List[DictionaryEntry],
        priority: bool = False,
        text_locales: List[str] = (),
        simplified_normalization: bool = False) -> Generator[CourtAnnotation, None, None]:
    locale_obj = Locale(locale)
    dic_entries = find_dict_entities(
        text,
        court_config_list,
        default_language=locale_obj.language,
        conflict_resolving_func=conflicts_take_first_by_id if priority else None,
        text_languages=[Locale(item).language for item in text_locales],
        simplified_normalization=simplified_normalization)
    for ent in dic_entries:
        ant = CourtAnnotation(coords=ent.coords)
        if ent.entity[0]:
            toponym: DictionaryEntry = ent.entity[0]
            ant.entity_id = toponym.id
            ant.entity_category = toponym.category
            ant.entity_priority = toponym.priority
            ant.name_en = toponym.entity_name
            ant.name = toponym.name
            if toponym.extra_columns:
                for extr_col in toponym.extra_columns:
                    setattr(ant, extr_col, toponym.extra_columns[extr_col])
        if ent.entity[1]:  # alias
            ant.alias = ent.entity[1].alias
            ant.locale = ent.entity[1].language
        if not ant.locale:
            ant.locale = locale_obj.language
        yield ant
