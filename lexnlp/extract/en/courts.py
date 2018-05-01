"""Court extraction for English.

This module implements extraction functionality for courts in English, including formal names, abbreviations,
and aliases.

Todo:
  * Add utilities for loading court data
"""
from typing import List, Tuple, Generator, Any

from lexnlp.extract.en.dict_entities import find_dict_entities, conflicts_take_first_by_id

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_courts(text: str,
               court_config_list: List[Tuple[int, str, int, List[Tuple[str, str, bool, int]]]],
               priority: bool = False,
               text_languages: List[str] = None) -> Generator[Tuple[Tuple, Tuple], Any, Any]:
    """
    Searches for courts from the provided config list and yields tuples of (court_config, court_alias).
    Court config is: (court_id, court_name, [list of aliases])
    Alias is: (alias_text, language, is_abbrev, alias_id)

    This method uses general searching routines for dictionary entities from dict_entities.py module.
    Methods of dict_entities module can be used for comfortable creating the config: entity_config(),
    entity_alias(), add_aliases_to_entity().
    :param text:
    :param court_config_list: List list of all possible known courts in the form of tuples:
     (id, name, [(alias, lang, is_abbrev], ...).
    :param return_source:
    :param priority: If two courts found with the totally equal matching aliases - then use the one with the lowest id.
    :param text_languages: Language(s) of the source text. If a language is specified then only aliases of this
    language will be searched for. For example: this allows ignoring "Island" - a German language
     alias of Iceland for English texts.
    :return: Generates tuples: (court entity, court alias)
    """
    yield from find_dict_entities(text, court_config_list,
                                  conflict_resolving_func=conflicts_take_first_by_id if priority else None,
                                  text_languages=text_languages)
