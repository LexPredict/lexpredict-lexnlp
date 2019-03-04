"""Geo Entity extraction for English.

This module implements extraction functionality for geo entities in English, including formal names, abbreviations,
and aliases.

"""
from typing import List, Tuple, Union, Dict, Generator, Any

from lexnlp.config.en import geoentities_config
from lexnlp.extract.en.dict_entities import find_dict_entities, conflicts_take_first_by_id, \
    prepare_alias_blacklist_dict, conflicts_top_by_priority

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

_ALIAS_BLACK_LIST_PREPARED = prepare_alias_blacklist_dict(geoentities_config.ALIAS_BLACK_LIST)


def get_geoentities(text: str,
                    geo_config_list: List[Tuple[int, str, List[Tuple[str, str, bool, int]]]],
                    priority: bool = False,
                    priority_by_id: bool = False,
                    text_languages: List[str] = None,
                    min_alias_len: int = geoentities_config.MIN_ALIAS_LEN,
                    prepared_alias_black_list: Union[None, Dict[str, Tuple[List[str], List[str]]]]
                    = _ALIAS_BLACK_LIST_PREPARED) -> Generator[Tuple[Tuple, Tuple], Any, Any]:
    """
    Searches for geo entities from the provided config list and yields pairs of (entity, alias).
    Entity is: (entity_id, name, [list of aliases])
    Alias is: (alias_text, lang, is_abbrev, alias_id)

    This method uses general searching routines for dictionary entities from dict_entities.py module.
    Methods of dict_entities module can be used for comfortable creating the config: entity_config(),
    entity_alias(), add_aliases_to_entity().
    :param text:
    :param geo_config_list: List of all possible known geo entities in the form of tuples
    (id, name, [(alias, lang, is_abbrev, alias_id), ...]).
    :param priority: If two entities found with the totally equal matching aliases -
    then use the one with the greatest priority field.
    :param priority_by_id: If two entities found with the totally equal matching aliases -
    then use the one with the lowest id.
    :param text_languages: Language(s) of the source text. If a language is specified then only aliases of this
    language will be searched for. For example: this allows ignoring "Island" - a German language
     alias of Iceland for English texts.
    :param min_alias_len: Minimal length of geo entity aliases to search for.
    :param prepared_alias_black_list: List of aliases to exclude from searching in the form:
     dict of lang -> (list of normalized non-abbreviation aliases, list of normalized abbreviation aliases).
     Use dict_entities.prepare_alias_blacklist_dict() for preparing this dict.
    :return: Generates tuples: (entity, alias)
    """
    conflict_resolving_func = None

    if priority_by_id:
        conflict_resolving_func = conflicts_take_first_by_id

    if priority:
        conflict_resolving_func = conflicts_top_by_priority

    yield from find_dict_entities(text, geo_config_list,
                                  conflict_resolving_func=conflict_resolving_func,
                                  text_languages=text_languages,
                                  min_alias_len=min_alias_len,
                                  prepared_alias_black_list=prepared_alias_black_list)
