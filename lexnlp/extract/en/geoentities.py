"""
Geo Entity extraction for English.

This module implements extraction functionality for geo entities in English, including formal names, abbreviations,
and aliases.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Tuple, Dict, Generator, Any, Optional

from lexnlp.extract.all_locales.languages import LANG_EN
from lexnlp.extract.common.geoentity_detector import GeoEntityLocator
from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
from lexnlp.config.en import geoentities_config
from lexnlp.extract.en.dict_entities import prepare_alias_banlist_dict, DictionaryEntry, DictionaryEntryAlias


_ALIAS_BAN_LIST_PREPARED = prepare_alias_banlist_dict(geoentities_config.ALIAS_BLACK_LIST)


def get_geoentities(
    text: str,
    geo_config_list: List[DictionaryEntry],
    conflict_resolving_field: str = 'none',
    priority_direction: str = 'asc',
    text_languages: List[str] = None,
    min_alias_len: Optional[int] = None,
    prepared_alias_ban_list: Optional[Dict[str, Tuple[List[str], List[str]]]] = None,
    simplified_normalization: bool = False,
) -> Generator[Tuple[DictionaryEntry, DictionaryEntryAlias], Any, Any]:
    """
    """
    prepared_alias_ban_list = (
        prepared_alias_ban_list
        if prepared_alias_ban_list is not None
        else _ALIAS_BAN_LIST_PREPARED
    )

    min_alias_len = min_alias_len if min_alias_len else geoentities_config.MIN_ALIAS_LEN

    locator = GeoEntityLocator(
        LANG_EN.code,
        geo_config_list,
        prepared_alias_ban_list,
        conflict_resolving_field=conflict_resolving_field,
        priority_direction=priority_direction,
        text_languages=text_languages,
        min_alias_len=min_alias_len,
        simplified_normalization=simplified_normalization
    )

    yield from locator.get_geoentity_entries(text)


def get_geoentity_list(
    text: str,
    geo_config_list: List[DictionaryEntry],
    conflict_resolving_field: str = 'none',
    priority_direction: str = 'asc',
    text_languages: List[str] = None,
    min_alias_len: Optional[int] = None,
    prepared_alias_ban_list: Optional[Dict[str, Tuple[List[str], List[str]]]] = None,
    simplified_normalization: bool = False,
) -> List[Tuple[DictionaryEntry, DictionaryEntryAlias]]:
    """
    """
    return list(
        get_geoentities(
            text=text,
            geo_config_list=geo_config_list,
            conflict_resolving_field=conflict_resolving_field,
            priority_direction=priority_direction,
            text_languages=text_languages,
            min_alias_len=min_alias_len,
            prepared_alias_ban_list=prepared_alias_ban_list,
            simplified_normalization=simplified_normalization,
        )
    )


def get_geoentity_annotations(
    text: str,
    geo_config_list: List[DictionaryEntry],
    conflict_resolving_field: str = 'none',
    priority_direction: str = 'asc',
    text_languages: List[str] = None,
    min_alias_len: Optional[int] = None,
    prepared_alias_ban_list: Optional[Dict[str, Tuple[List[str], List[str]]]] = None,
    simplified_normalization: bool = False,
) -> Generator[GeoAnnotation, None, None]:

    prepared_alias_ban_list = (
        prepared_alias_ban_list
        if prepared_alias_ban_list is not None
        else _ALIAS_BAN_LIST_PREPARED
    )

    min_alias_len = min_alias_len if min_alias_len else geoentities_config.MIN_ALIAS_LEN

    locator = GeoEntityLocator(
        LANG_EN.code,
        geo_config_list,
        prepared_alias_ban_list,
        conflict_resolving_field=conflict_resolving_field,
        priority_direction=priority_direction,
        text_languages=text_languages,
        min_alias_len=min_alias_len,
        simplified_normalization=simplified_normalization,
    )

    yield from locator.get_geoentity_annotations(text)


def get_geoentity_annotation_list(
    text: str,
    geo_config_list: List[DictionaryEntry],
    conflict_resolving_field: str = 'none',
    priority_direction: str = 'asc',
    text_languages: List[str] = None,
    min_alias_len: Optional[int] = None,
    prepared_alias_ban_list: Optional[Dict[str, Tuple[List[str], List[str]]]] = None,
    simplified_normalization: bool = False,
) -> List[GeoAnnotation]:
    """
    """
    return list(
        get_geoentity_annotations(
            text=text,
            geo_config_list=geo_config_list,
            conflict_resolving_field=conflict_resolving_field,
            priority_direction=priority_direction,
            text_languages=text_languages,
            min_alias_len=min_alias_len,
            prepared_alias_ban_list=prepared_alias_ban_list,
            simplified_normalization=simplified_normalization,
        )
    )
