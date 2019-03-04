"""Universal extraction of entities for which we have full dictionaries of possible names and aliases from English text.

   Example: Courts - we have the full dictionary of known courts with their names and aliases and are able to
   search the text for each possible court.
            Geo entities - we have the full set of known geo entities and can search any text for their occurrences.


   Search methods of this module require lists of possible entities with their ids, names and sets of aliases
   in different languages.
   To allow using these methods in Celery and especially for allowing building these configuration lists once and using
   them in multiple Celery tasks it is required to allow their easy and fast serialization.
   By default Celery uses JSON serialization starting from v. 4 and does not allow serializing objects of custom
   classes out of the box. So we will have to use either dicts or tuples to avoid requiring special configuration for
   Celery. Tuples are faster.

   To avoid typos in development and utilize typization hints in IDE there are few methods in this module for operating
   tuples which represent entities and aliases. They accept named parameters lists and return tuples.
"""
import re
from typing import Union, List, Dict, Set, Tuple, Callable, Generator

from lexnlp.nlp.en.tokens import get_token_list, get_stem_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def entity_config(entity_id: int,
                  name: str,
                  priority: int = 0,
                  aliases: List[Union[str, Tuple]] = (),
                  name_is_alias: bool = True) -> Tuple[int, str, int, List[Tuple]]:
    """
    Create entity configuration for a possible entity with its id, name and aliases to search.
    :param entity_id: Unique identifier of the entity.
    :param name: Human-readable name to displaying in UI. Searches are made not for name but for the possible aliases -
    each one having its assigned language. And name may or may not be added to the list of search aliases.
    :param priority: Optional int priority value for the entity. Can be used for sorting. Entities with higher prio
    should be selected first.
    :param aliases: List of aliases to search for. Each alias can be either string or
    (alias, language, is_abbreviation, alias_id)
    tuple. For string - a tuple with default values is created. entity_alias() function can be used to create the alias
    tuple ensuring its components type safety in IDE.
    :param name_is_alias: If True - then add entity name to the list of aliases with undefined language.
    :return: A tuple representing the entity in format (entity_id, name, [(alias, lang, is_abbrev, alias_id), ...])
    """
    res = (entity_id, name, priority, list())

    if name_is_alias:
        add_alias_to_entity(res, name)

    if aliases:
        for alias in aliases:
            if isinstance(alias, str):
                add_alias_to_entity(res, alias)
            else:
                res[3].append(alias)
    return res


def entity_alias(alias: str, language: str = None, is_abbreviation: bool = False, alias_id: int = None) \
        -> Tuple[str, str, bool, int]:
    """
    Create entity alias tuple. This method is just for ensuring type safety of alias components in IDE.
    :param alias_id: Alias id. None if there is no id.
    :param alias: Alias text - 'Mississippi', 'MS', 'CAN', ...
    :param language: Language - en, de, fr, ...
    :param is_abbreviation: Is this alias representing an abbreviation or not. Abbreviations have different rules
    of searching.
    :return: A tuple representing the alias in format: (alias_text, lang, is_abbreviation, alias_id)
    """
    return alias, language, is_abbreviation, alias_id


def get_entity_name(entity: Tuple[int, str, int, List[Tuple]]) -> str:
    """
    Get name of the entity.
    This method is just for more comfortable development - to avoid accessing properties of
    entities by their indexes.
    :param entity:
    :return:
    """
    return entity[1]


def get_entity_id(entity: Tuple[int, str, int, List[Tuple]]) -> int:
    """
    Get id of the entity.
    This method is just for more comfortable development - to avoid accessing properties of
    entities by their indexes.
    :param entity:
    :return:
    """
    return entity[0]


def get_entity_aliases(entity: Tuple[int, str, int, List[Tuple]]) -> List[Tuple]:
    """
    Get aliases of the entity.
    This method is just for more comfortable development - to avoid accessing properties of
    entities by their indexes.
    :param entity:
    :return:
    """
    return entity[3]


def get_entity_priority(entity: Tuple[int, str, int, List[Tuple]]) -> int:
    """
    Get priority of the entity.
    This method is just for more comfortable development - to avoid accessing properties of
    entities by their indexes.
    :param entity:
    :return:
    """
    return entity[2]


def get_alias_text(alias: Tuple[str, str, bool, int]) -> str:
    """
    Get alias text from alias tuple.
    This method is just for more comfortable development - to avoid accessing properties of
    aliases by their indexes.
    :param alias:
    :return:
    """
    return alias[0]


def get_alias_id(alias: Tuple[str, str, bool, int]) -> int:
    """
    Get alias text from alias tuple.
    This method is just for more comfortable development - to avoid accessing properties of
    aliases by their indexes.
    :param alias:
    :return:
    """
    return alias[3]


def add_alias_to_entity(entity: Tuple[int, str, int, List[Tuple]],
                        alias: str, language: str = None, is_abbreviation: bool = False, alias_id: int = None):
    """
    Add alias to entity. Entities are in the form of tuples:
    (entity_id, name, [(alias_text, lang, is_abbrev, alias_id), ...]).
    This method is just for more comfortable development - to ensure type safety and avoid accessing properties of
    entities by their indexes.
    :param entity:
    :param alias:
    :param language:
    :param is_abbreviation:
    :param alias_id: Alias id or None if identifying is not supported.
    :return:
    """
    entity[3].append(entity_alias(alias, language, is_abbreviation, alias_id))


def add_aliases_to_entity(entity: Tuple[int, str, int, List[Tuple[str, str, bool]]],
                          aliases_csv: str,
                          language: str = None,
                          is_abbreviation: bool = None,
                          alias_id: int = None,
                          csv_separator: str = ';'):
    """
    Add alias to entity. Entities are in the form of tuples:
    (entity_id, name, [(alias_text, lang, is_abbrev, alias_id), ...]).
    This method can be used if there is a comma separated list of aliases stored somewhere and they all have the same
    language and is_abbreviation value.
    This method is just for more comfortable development - to ensure type safety and avoid accessing properties of
    entities by their indexes.
    :param entity:
    :param aliases_csv:
    :param language:
    :param is_abbreviation:
    :param alias_id:
    :param csv_separator:
    :return:
    """
    if aliases_csv:
        for alias in aliases_csv.split(csv_separator):
            add_alias_to_entity(entity, alias, language, is_abbreviation, alias_id)


class SearchResultPosition:
    """
    Represents a position in the normalized source text at which one or more entities have been detected.
    One or more entities having equal aliases can be detected on a position in the text.
    """
    __slots__ = ('entities_dict', 'alias_text', 'start')

    def __init__(self, entity: Tuple[int, str, int, List[Tuple]], alias: Tuple[str, str, bool, int], start: int):
        self.entities_dict = {entity[0]: (entity, alias)}
        self.alias_text = alias[0]
        self.start = start

    def add_entity(self, entity: Tuple[int, str, int, List[Tuple]], alias: Tuple[str, str, bool, int]):
        if entity:
            self.entities_dict[entity[0]] = (entity, alias)
        return self

    def get_entities_aliases(self):
        return list(self.entities_dict.values())

    def overlaps(self, other: 'SearchResultPosition'):
        return max(self.start, other.start) <= min(self.start + len(self.alias_text) - 1,
                                                   other.start + len(other.alias_text) - 1)


def normalize_text(text: str,
                   spaces_on_start_end: bool = True,
                   spaces_after_dots: bool = True,
                   lowercase: bool = True,
                   use_stemmer: bool = False) -> str:
    """
    Normalizes text for substring search operations - extracts tokens, joins them back with spaces,
    adds missing spaces after dots for abbreviations, e.t.c.
    Overall aim of this method is to weaken substring matching conditions by normalizing both the text
    and the substring being searched by the same way removing obsolete differences between them
    (case, punctuation, ...).
    :param text:
    :param spaces_on_start_end:
    :param spaces_after_dots:
    :param lowercase:
    :param use_stemmer: Use stemmer instead of tokenizer. When using stemmer all words will be converted to singular
    number (or to some the most plain form) before matching. When using tokenizer - the words are compared as is.
    Using tokenizer should be enough for searches for entities which exist in a single number in the real world -
    geo entities, courts, .... Stemmer is required for searching for some common objects - table, pen, developer, ...
    :return:
    """
    tokens = get_stem_list(text, lowercase=lowercase) if use_stemmer else get_token_list(text, lowercase=lowercase)
    res = ' '.join(tokens)
    if spaces_on_start_end:
        res = ' ' + res + ' '
    if spaces_after_dots:
        res = res.replace('.', ' . ').replace('  ', ' ')
    return res


def alias_is_blacklisted(alias_black_list: Union[None, Dict[str, Tuple[List[str], List[str]]]],
                         norm_alias: str,
                         alias_lang:str,
                         is_abbrev: bool) -> bool:
    if not alias_black_list:
        return False
    for lang in (alias_lang, None):
        lang_aliases = alias_black_list.get(lang)
        if lang_aliases and len(lang_aliases) >= 2:
            if norm_alias in lang_aliases[1 if is_abbrev else 0]:
                return True
    return False


def _find_entity_positions(normalized_text: str,
                           normalized_text_lowercase: str,
                           entity: Tuple[int, str, int, List[Tuple]],
                           text_languages: Union[List[str], Tuple[str], Set[str]],
                           context: Dict[int, SearchResultPosition] = None,
                           use_stemmer: bool = False,
                           abbrev_uppercase_check_range: int = 20,
                           min_alias_len: int = None,
                           alias_black_list: Union[None, Dict[str, Tuple[List[str], List[str]]]] = None):
    """
    Searches for all occurrences of name/alias of the specified entity in the specified text and fills the
    provided context dict with them.
    Operates on the provided search context - a map of alias/name positions to the SearchResultPosition entries.
    If there is a previously found name/alias at the same position in the text - the longest name/alias is
    stored in the context and the shorter one is dropped.
    So after the series of execution of this method on the shared context it will be filled with the best matching
    search results for each starting position in the text. Next these results should be ordered by start index and
    checked for intersections - to drop entries having shorter names/aliases.
    Alias languages are taken into account in this method - if a language of the source text is specified then
    only aliases of this language are being searched for.

    :param normalized_text Non-lowercase version of the normalized source text - to search for abbreviations.
    :param normalized_text_lowercase: Lowercase version of the normalized source text - to search for non-abbrevs.
    :param text_languages: If set - then only aliases of these languages will be searched for.
    :param entity:
    :param context: Map of alias/name positions in the source text to SearchResultPosition entries.
    This context can be shared between multiple executions of this functions to reach the results of the overall search
    of multiple DictEntities with the longest matching DictEntity on each position.
    Can be None - for the case of single DictEntity search.
    :param alias_black_list: Prepared black list of aliases to exclude from search.
    Should be: dict of language -> tuple (list of normalized non-abbreviations, list of normalized abbreviations)
    "None" is a key for "any" language.
    :param abbrev_uppercase_check_range: To avoid false-positives in detecting abbreviations similar to AND, OR, IN
    we need to ensure that it is not english words appeared in a piece of text written in uppercase.
    For this for each abbrev we ignore it if text[position - range : position + range] == uppercase(text[...]).
    :return:
    """

    def abbrev_in_uppercase_block(text: str, position: int, check_range:int):
        block = text[max(0, position - check_range): min(len(text), position + check_range)]
        block_upper = block.upper()
        return block == block_upper

    if context is None:
        context = dict()

    entity_aliases = get_entity_aliases(entity)
    if entity_aliases:
        for ea in entity_aliases:

            alias_text = ea[0]
            alias_lang = ea[1]
            alias_is_abbreviation = ea[2]

            if not alias_text or (
                            text_languages and alias_lang and alias_lang not in text_languages):
                continue
            if min_alias_len and len(alias_text) < min_alias_len:
                continue

            if alias_is_abbreviation:
                normalized_alias = normalize_text(alias_text, lowercase=False, use_stemmer=use_stemmer)
                normalized_text_for_alias = normalized_text
            else:
                normalized_alias = normalize_text(alias_text, lowercase=True, use_stemmer=use_stemmer)
                normalized_text_for_alias = normalized_text_lowercase

            if alias_is_blacklisted(alias_black_list, normalized_alias, alias_lang, alias_is_abbreviation):
                continue

            start = None
            while True:
                start = normalized_text_for_alias.find(normalized_alias,
                                                       start + len(normalized_alias) - 1 if start is not None else 0)
                if start < 0:
                    break

                if alias_is_abbreviation and \
                        abbrev_in_uppercase_block(normalized_text_for_alias, start, abbrev_uppercase_check_range):
                    continue

                already_found = context.get(start)
                if already_found and len(already_found.alias_text) >= len(alias_text):
                    already_found.add_entity(entity, ea)
                else:
                    context[start] = SearchResultPosition(entity, ea, start)


def find_dict_entities(text: str,
                       all_possible_entities: List[Tuple[int, str, int, List[Tuple]]],
                       text_languages: Union[List[str], Tuple[str], Set[str]] = None,
                       conflict_resolving_func: Callable[[List[Tuple[int, str, List[Tuple]]]],
                                                         Tuple[List[Tuple[int, str, List[Tuple]]], Tuple]] = None,
                       use_stemmer: bool = False,
                       remove_time_am_pm: bool = True,
                       min_alias_len: int = None,
                       prepared_alias_black_list: Union[None, Dict[str, Tuple[List[str], List[str]]]] = None)\
        -> Generator:
    """
    Find all entities defined in the 'all_possible_entities' list appeared in the source text.
    This method takes care of leaving only the longest matching search result for the case of multiple
    entities having aliases - one being a substring of another.
    This method takes care of the language of the text and aliases - if language is specified both for the text
    and for the alias - then this alias is used only if they are the same.
    This method may detect multiple possibly matching entities at a position in the text - because there can be
    entites having the same aliases in the same language. To resolve such conflicts a special resolving function can be
    specified.
    This method takes care of time AM/PM components which possibly can appear in the aliases of some entities -
    it tries to detect minutes/seconds/milliseconds before AM/PM and ignore them in such cases.

    Algorithm of this method:
    1. Normalize the source text (we need lowercase and non-lowercase versions for abbrev searches).
    2. Create a shared search context - a map of position -> (alias text + list of matching entities)
    3. For each possible entity do search using the shared context:
        3.1. For each alias of the entity:
            3.1.1. Iteratively search for all occurrences of the alias taking into account its language, abbrev status.
                    For each found occurrence of the alias - check if there is already found another alias and entity
                    at this position and leave only the one having the longest alias ("Something" vs "Something Bigger")
                    If there is already a found different entity on this position having totally equal alias with
                    the same language - then store them both for this position in the text.
    4. Now we have a map filled with: position -> (alias text + list of entities having this alias).
    After sorting the items of this dict by position we will be able to get rid of overlaping of longer and shorter
    aliases being one a substirng of another ("Bankr. E.D.N.Y." vs "E.D.N.Y.").
    5. For each next position check if it overlaps with the next one [position; position + len(alias)].
    If overlaps - then leave the longest alias and drop the shorter.


    Main complexity of this algorithm is caused by the requirement to detect the longest match for each piece of text
    while the longer match can start at the earlier position then the shorter match and there can be multiple aliases
    of different entities matching the same piece of text.

    Another algorithm for this function can be based on the idea that or-kind regexp returns the longest matching group.
    We could form regexps containing the possible aliases and apply them to the source text:
    r'alias1|alias2|longer alias2|...'

    TODO Compare to other algorithms for time and memory complexity

    :param text:
    :param all_possible_entities: list of dict or list of DictEntity - all possible entities to search for
    :param min_alias_len: Minimal length of alias/name to search for. Can be used to ignore too short aliases like "M."
    while searching.
    :param prepared_alias_black_list: List of aliases to remove from searching. Can be used to ignore concrete aliases.
    Prepared black list of aliases to exclude from search.
    Should be: dict of language -> tuple (list of normalized non-abbreviations, list of normalized abbreviations)
    :param text_languages: If set - then only aliases of these languages will be searched for.
    :param conflict_resolving_func: A function for resolving conflicts when there are multiple entities detected
    at the same position in the source text and their detected aliases are of the same length.
    The function takes a list of conflicting entities and should return a list of one or more entities which
    should be returned.
    :param use_stemmer: Use stemmer instead of tokenizer. Stemmer converts words to their simple form (singular number,
    e.t.c.). Stemmer works better for searching for "tables", "developers", ... Tokenizer fits for "United States",
    "Mississippi", ...
    :param remove_time_am_pm: Remove from final results AM/PM abbreviations which look like end part of time
    strings - 11:45 am, 10:00 pm.
    :return:
    """

    if not text:
        return

    normalized_text = normalize_text(text, lowercase=False, use_stemmer=use_stemmer)
    normalized_text_lowercase = normalized_text.lower()

    search_context = dict()
    # Search for each DictEntity occurrence adding them into the shared search context.
    for dict_entity in all_possible_entities:
        _find_entity_positions(normalized_text, normalized_text_lowercase, dict_entity, text_languages, search_context,
                               use_stemmer=use_stemmer, min_alias_len=min_alias_len,
                               alias_black_list=prepared_alias_black_list)

    # At this moment we have a map of positions in the text
    # to SearchResultPosition entries (position + appeared name/alias + DictEntity).
    # Now we need to filter out the overlapping names/aliases - leaving only the longest one for each conflict.

    # Iterating over the (text pos -> SearchResultPosition) entries sorted by text pos.
    # For each next entry - checking if it intersects with the previous one by the means
    # of [text pos; text pos + len(found name/alias)].
    # An intersection means that we have a conflict of two courts having shorter and longer names/aliases.
    # So we leave only the longest one for each conflicting place.
    # Need to note that for the SearchResultPosition left on each step - we only need to test it for overlapping
    # with the next and further entries because they are already sorted by position in the text.
    # And this way it is done via a single loop.
    prev_pos = None

    def resolve_conflicts(pos: SearchResultPosition) \
            -> List[Tuple[Tuple[int, str, int, List[Tuple]], Tuple[str, str, bool, int]]]:
        """
        Takes SearchResultPosition (multiple found entities+aliases at the same position in the text)
        and return a single entity+its alias which should be returned for this position or their smaller list.
        Entity is (entity_id, name, list of aliases). Alias is: (alias_text, language, is_abbrev, alias_id)
        :param pos:
        :return:
        """
        entities_at_pos = pos.get_entities_aliases()

        if remove_time_am_pm and pos.alias_text.lower() in ('am', 'pm'):
            # We should check if this is not something like 11:45 am or 11:45.123 pm
            maybe_time1 = normalized_text_lowercase[max(0, pos.start - 3):pos.start + 1]
            maybe_time2 = normalized_text_lowercase[max(0, pos.start - 4):pos.start + 1]
            if re.match(r':\d\d\s', maybe_time1) \
                    or re.match(r'\.\d\d\d\s', maybe_time2):
                return []

        if len(entities_at_pos) == 1:
            return entities_at_pos
        else:
            return conflict_resolving_func(entities_at_pos) if conflict_resolving_func else entities_at_pos

    for (_index, next_pos) in sorted(search_context.items()):
        if prev_pos and not next_pos.overlaps(prev_pos):
            for entity, alias in resolve_conflicts(prev_pos):
                yield entity, alias
            prev_pos = next_pos
        else:
            prev_pos = prev_pos if prev_pos and len(prev_pos.alias_text) >= len(next_pos.alias_text) else next_pos

    if prev_pos:
        for entity, alias in resolve_conflicts(prev_pos):
            yield entity, alias


def conflicts_take_first_by_id(conflicting_entities_aliases: List[Tuple[Tuple[int, str, int, List[Tuple]], Tuple]]) \
        -> List[Tuple[Tuple[int, str, int, List[Tuple]], Tuple[str, str, bool, int]]]:
    """
    Default conflict resolving function for dropping all entities detected at the same position excepting the one
    having the smallest id. To be used in find_dict_entities() method.
    :param conflicting_entities_aliases: list of (entity, alias) pairs
    :return:
    """
    return [min(conflicting_entities_aliases, key=lambda entity_alias_pair: get_entity_id(entity_alias_pair[0])), ]


def conflicts_top_by_priority(conflicting_entities_aliases: List[Tuple[Tuple[int, str, int, List[Tuple]], Tuple]]) \
        -> List[Tuple[Tuple[int, str, int, List[Tuple]], Tuple[str, str, bool, int]]]:
    """
    Default conflict resolving function for dropping all entities detected at the same position excepting the one
    having the smallest id. To be used in find_dict_entities() method.
    :param conflicting_entities_aliases: list of (entity, alias) pairs
    :return:
    """
    return [max(conflicting_entities_aliases,
                key=lambda entity_alias_pair: get_entity_priority(entity_alias_pair[0])), ]


def prepare_alias_blacklist_dict(alias_blacklist: List[Tuple[str, str, bool]], use_stemmer: bool=False) \
        -> Union[None, Dict[str, Tuple[List[str], List[str]]]]:
    """
    Prepare alias black list for providing it to find_dict_entities() function.
    :param alias_blacklist: Non-normalized form of the blacklist: [(alias, lang, is_abbreb), ...]
    :param use_stemmer: Use stemmer for alias normalization. Otherwise - tokenizer only.
    :return:
    """
    if not alias_blacklist:
        return None
    res = dict()
    for alias, lang, is_abbrev in alias_blacklist:
        lang_tuple = res.get(lang)
        if lang_tuple is None:
            lang_tuple = ([], [])
            res[lang] = lang_tuple
        if is_abbrev:
            lang_tuple[1].append(normalize_text(alias, lowercase=False, use_stemmer=use_stemmer))
        else:
            lang_tuple[0].append(normalize_text(alias, lowercase=True, use_stemmer=use_stemmer))
    return res
