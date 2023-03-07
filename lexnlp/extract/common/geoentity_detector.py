# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Union, Dict, Tuple, Generator, Any

from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
from lexnlp.extract.en.dict_entities import DictionaryEntry, find_dict_entities, DictionaryEntryAlias, \
    conflicts_take_first_by_id, conflicts_top_by_priority


class GeoEntityLocator:
    """
    Searches for geo entities from the provided config list and yields pairs of (entity, alias).
                Entity is: (entity_id, name, [list of aliases])
                Alias is: (alias_text, lang, is_abbrev, alias_id)
    """
    def __init__(
            self,
            language: str,
            geo_config_list: List[DictionaryEntry],
            prepared_alias_ban_list: Union[None, Dict[str, Tuple[List[str], List[str]]]],
            conflict_resolving_field: str = 'none',
            priority_direction: str = 'asc',
            text_languages: List[str] = None,
            min_alias_len: int = 2,
            simplified_normalization: bool = False):
        """
        :param language: default language for annotations found
        :param geo_config_list: List of all possible known geo entities in the form of tuples
        (id, name, [(alias, lang, is_abbrev, alias_id), ...]).
        :param conflict_resolving_field: If two entities found with the totally equal matching aliases -
        then use the one with the greatest priority field ("priority") / the one with the lowest id ("id") /
         leave all entries found ("none", default).
        :param priority_direction: priority ('asc' or 'desc') order for the conflict resolving function
        :param text_languages: Language(s) of the source text. If a language is specified then only aliases of this
        language will be searched for. For example: this allows ignoring "Island" - a German language
         alias of Iceland for English texts.
        :param min_alias_len: Minimal length of geo entity aliases to search for.
        :param prepared_alias_ban_list: List of aliases to exclude from searching in the form:
         dict of lang -> (list of normalized non-abbreviation aliases, list of normalized abbreviation aliases).
         Use dict_entities.prepare_alias_banlist_dict() for preparing this dict.
        :param simplified_normalization: don't use NLTK for "normalizing" text
        """
        self.language = language
        self.geo_config_list = geo_config_list
        self.prepared_alias_ban_list = prepared_alias_ban_list
        self.conflict_resolving_func = conflicts_take_first_by_id if conflict_resolving_field == 'id' \
            else conflicts_top_by_priority if conflict_resolving_field == 'priority' else None
        self.priority_direction = priority_direction
        self.text_languages = text_languages
        self.min_alias_len = min_alias_len
        self.simplified_normalization = simplified_normalization

    def get_geoentity_entries(
            self,
            text: str) -> Generator[Tuple[DictionaryEntry, DictionaryEntryAlias], Any, Any]:
        """
        This method uses general searching routines for dictionary entities from dict_entities.py module.
        Methods of dict_entities module can be used for comfortable creating the config: entity_config(),
        entity_alias(), add_aliases_to_entity().
        """
        for ent in find_dict_entities(text,
                                      self.geo_config_list,
                                      conflict_resolving_func=self.conflict_resolving_func,
                                      priority_direction=self.priority_direction,
                                      default_language=self.language,
                                      text_languages=self.text_languages,
                                      min_alias_len=self.min_alias_len,
                                      prepared_alias_ban_list=self.prepared_alias_ban_list,
                                      simplified_normalization=self.simplified_normalization):
            yield ent.entity

    def get_geoentity_annotations(
            self,
            text: str) -> Generator[GeoAnnotation, None, None]:
        """
        This method uses general searching routines for dictionary entities from dict_entities.py module.
        Methods of dict_entities module can be used for comfortable creating the config: entity_config(),
        entity_alias(), add_aliases_to_entity().
        """
        dic_entries = find_dict_entities(text,
                                         self.geo_config_list,
                                         self.language,
                                         conflict_resolving_func=self.conflict_resolving_func,
                                         priority_direction=self.priority_direction,
                                         text_languages=self.text_languages,
                                         min_alias_len=self.min_alias_len,
                                         prepared_alias_ban_list=self.prepared_alias_ban_list,
                                         simplified_normalization=self.simplified_normalization)

        for ent in dic_entries:
            ant = GeoAnnotation(coords=ent.coords)
            if ent.entity[0]:
                toponym = ent.entity[0]  # type: DictionaryEntry
                ant.entity_id = toponym.id
                ant.entity_category = toponym.category
                ant.entity_priority = toponym.priority
                ant.name_en = toponym.entity_name
                # year = TextAnnotation.get_int_value(toponym.id)  # ?
                # if year:
                #     ant.year = year
                ant.name = toponym.name
                if toponym.extra_columns:
                    for extr_col in toponym.extra_columns:
                        setattr(ant, extr_col, toponym.extra_columns[extr_col])

            if ent.entity[1]:  # alias
                ant.alias = ent.entity[1].alias
                ant.locale = ent.entity[1].language
            if not ant.locale:
                ant.locale = self.language
            yield ant
