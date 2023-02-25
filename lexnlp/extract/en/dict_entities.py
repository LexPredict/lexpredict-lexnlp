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

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import csv
import re
from typing import Union, List, Dict, Set, Tuple, Callable, Generator, Any, Optional

import pandas as pd

from lexnlp.extract.all_locales.languages import DEFAULT_LANGUAGE
from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder
from lexnlp.nlp.en.tokens import get_token_list, get_stem_list


reg_space = re.compile(r'\s+')


class DictionaryEntryAlias:
    def __init__(self,
                 alias: str = '',
                 language: str = '',
                 is_abbreviation: bool = False,
                 alias_id: Optional[int] = None,
                 normalized_alias: str = ''):
        self.alias = alias  # 'Mississippi'
        self.language = language  # 'fr'
        self.is_abbreviation = is_abbreviation  # False
        self.alias_id = alias_id  # None (or 1051 ...)
        self.normalized_alias = normalized_alias  # 'mississippi'

    def __repr__(self):
        if self.alias_id is not None:
            return f'{self.alias}, lang: {self.language}, id: {self.alias_id}'
        return f'{self.alias}, lang: {self.language}'

    @classmethod
    def entity_alias(cls, alias: str, language: str = None, is_abbreviation: bool = False, alias_id: int = None) \
            -> 'DictionaryEntryAlias':
        normalized_alias = normalize_text(alias, lowercase=not is_abbreviation)
        return DictionaryEntryAlias(alias, language, is_abbreviation, alias_id, normalized_alias)

    def has_closer_locale(self,
                          alias: 'DictionaryEntryAlias',
                          text_languages: Optional[List[str]]) -> bool:
        # does 'self' have its locale higher on the passed 'text_languages' list?
        if not text_languages:
            return False
        if not alias.language and self.language:
            return False  # empty language means default language
        if alias.language and not self.language:
            return True
        for lang in text_languages:
            if self.language == lang and alias.language != lang:
                return True
            if alias.language == lang:
                return False
        return False


class DictionaryEntry:
    def __init__(self,
                 # pylint: disable=redefined-builtin
                 id: int = 0,
                 name: str = '',
                 priority: int = 0,
                 name_is_alias: bool = True,
                 aliases: Optional[List[DictionaryEntryAlias]] = None,
                 entity_name: str = '',
                 category: str = '',
                 extra_columns: Optional[Dict[str, str]] = None):
        self.id = id
        self.name = name
        self.priority = priority
        self.aliases = aliases or []
        if name_is_alias:
            self.aliases.append(DictionaryEntryAlias(name))
        self.entity_name = entity_name  # "universal" or En name
        self.category = category  # 'countries' or 'US states' or ...
        # columns that directly go to annotation object's fields:
        # 'iso_3166_2': 'de', ...
        self.extra_columns = extra_columns

    def __repr__(self):
        return f'"{self.name}": #{self.id}'

    def __str__(self):
        return f'"{self.name}": #{self.id}'

    @classmethod
    def load_entities_from_files(cls, entities_fn: str, aliases_fn: str) -> List['DictionaryEntry']:
        entities = {}

        with open(entities_fn, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entities[row['id']] = DictionaryEntry(
                    id=int(row['id']), name=row['name'], priority=int(row['priority']) if row['priority'] else 0,
                    name_is_alias=True)

        with open(aliases_fn, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entity: DictionaryEntry = entities.get(row['entity_id'])
                if entity:
                    aliases = row['alias']
                    for alias in aliases.split(';'):
                        dictionary_entry_alias = DictionaryEntryAlias(
                            alias=alias.strip(),
                            language=row['locale'],
                            is_abbreviation=row['type'].startswith('iso') or row['type'] == 'abbreviation',
                        )
                        entity.aliases.append(dictionary_entry_alias)
        return list(entities.values())

    @classmethod
    def load_entities_from_single_df(
            cls,
            config: pd.DataFrame,
            language: str,
            alias_columns: Optional[List[DictionaryEntryAlias]] = None,  # columns (values) to search for in text
            entity_id_column: str = 'Entity ID',
            entity_category_column: str = 'Entity Category',
            # source_column: str = '',
            name_column: str = 'Entity Name',
            local_name_column: str = '',  # 'German Name' etc
            priority_column: str = 'Entity Priority',
            # { 'column_name': 'annotation attribute name', ... }
            extra_columns: Optional[Dict[str, str]] = None) -> List['DictionaryEntry']:

        records: List['DictionaryEntry'] = []
        local_name_column = local_name_column or name_column
        extra_columns = extra_columns if extra_columns is not None else \
            {'ISO-3166-2': 'iso_3166_2', 'ISO-3166-3': 'iso_3166_3'}
        for _, row in config.iterrows():
            r = DictionaryEntry(
                id=int(row[entity_id_column]),
                name=row[local_name_column],
                priority=int(row[priority_column]) if priority_column and row[priority_column] else 0,
                entity_name=row[name_column] if name_column else row[local_name_column],
                category=row.get(entity_category_column) or '')
            if not alias_columns:
                alias_columns = [DictionaryEntryAlias(name_column, DEFAULT_LANGUAGE.code, False),
                                 DictionaryEntryAlias(local_name_column, language, False),
                                 DictionaryEntryAlias('Alias', language, False),
                                 DictionaryEntryAlias('ISO-3166-2', language, True),
                                 DictionaryEntryAlias('ISO-3166-3', language, True)]
            r.aliases = []
            for a in alias_columns:
                aliases = row.get(a.alias)
                if not aliases or not isinstance(aliases, str):
                    continue
                for alias in aliases.split(';'):
                    r.aliases.append(DictionaryEntryAlias(alias, a.language, a.is_abbreviation))

            if extra_columns:
                r.extra_columns = {}
                for ec in extra_columns:
                    r.extra_columns[extra_columns[ec]] = row[ec]

            records.append(r)
        return records


class AliasBanRecord:
    def __init__(self,
                 alias: str = '',
                 lang: Optional[str] = '',
                 is_abbrev: bool = False):
        self.alias = alias
        self.lang = lang
        self.is_abbrev = is_abbrev

    def __repr__(self):
        abr_str = ' abbr.' if self.is_abbrev else ''
        return f'{self.alias}, {self.lang}{abr_str}'


class AliasBanList:
    def __init__(self,
                 aliases: Optional[List[str]] = None,
                 abbreviations: Optional[List[str]] = None):
        self.aliases = aliases or []
        self.abbreviations = abbreviations or []


class SearchResultPosition:
    """
    Represents a position in the normalized source text at which one or more entities have been detected.
    One or more entities having equal aliases can be detected on a position in the text.
    """
    __slots__ = ('entities_dict', 'alias_text', 'start', 'end', 'source_text')

    def __init__(self,
                 entity: DictionaryEntry,
                 alias: DictionaryEntryAlias,
                 start: int,
                 end: int,
                 source_text: str = ''):
        self.entities_dict = {entity.id: (entity, alias)}
        self.alias_text = alias.alias
        self.start = start
        self.end = end
        self.source_text = source_text

    def __repr__(self):
        ent_str = f'{self.entities_dict}'
        ending = f'alias="{self.alias_text}", @[{self.start}, {self.end}]'
        return f'{ent_str}; {ending}'

    def add_entity(self,
                   entity: DictionaryEntry,
                   alias: DictionaryEntryAlias,
                   alias_language_order: Optional[List[str]]) -> 'SearchResultPosition':
        if entity:
            existing = self.entities_dict.get(entity.id)
            if not existing or not existing[1].has_closer_locale(alias, alias_language_order):
                self.entities_dict[entity.id] = (entity, alias)
        return self

    def get_entities_aliases(self) -> List[Tuple[DictionaryEntry, DictionaryEntryAlias]]:
        return list(self.entities_dict.values())

    def overlaps(self, other: 'SearchResultPosition') -> bool:
        return max(self.start, other.start) <= min(self.start + len(self.alias_text) - 1,
                                                   other.start + len(other.alias_text) - 1)


def normalize_text(text: str,
                   spaces_on_start_end: bool = True,
                   spaces_after_dots: bool = True,
                   lowercase: bool = True,
                   use_stemmer: bool = False,
                   simple_tokenization: bool = False) -> str:
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
    :param simple_tokenization: don't use nltk, just split text by space characters
    :param use_stemmer: Use stemmer instead of tokenizer. When using stemmer all words will be converted to singular
    number (or to some the most plain form) before matching. When using tokenizer - the words are compared as is.
    Using tokenizer should be enough for searches for entities which exist in a single number in the real world -
    geo entities, courts, .... Stemmer is required for searching for some common objects - table, pen, developer, ...
    :return: "normazlied" string
    """
    if use_stemmer:
        tokens = get_stem_list(text, lowercase=lowercase)
    elif simple_tokenization:
        tokens = reg_space.split(text)
        if lowercase:
            tokens = [t.lower() for t in tokens]
    else:
        tokens = get_token_list(text, lowercase=lowercase)
    res = ' '.join(tokens)
    if spaces_on_start_end:
        res = ' ' + res + ' '
    if spaces_after_dots:
        res = res.replace('.', ' . ').replace('  ', ' ')
    return res


def normalize_text_with_map(
        text: str,
        spaces_on_start_end: bool = True,
        spaces_after_dots: bool = True,
        lowercase: bool = True,
        use_stemmer: bool = False,
        simple_tokenization: bool = False) -> Tuple[str, List[int]]:
    """
    Almost like normalize_text, but also returns source-to-resulted char index map:
    map[i] = I, where i is the character coordinate within the source text,
                I is the same character's coordinate within the resulted text
    """
    src_dest_map = []  # type: List[int]
    if use_stemmer:
        tokens = get_stem_list(text, lowercase=lowercase)
    elif simple_tokenization:
        tokens = reg_space.split(text)
        if lowercase:
            tokens = [t.lower() for t in tokens]
    else:
        tokens = get_token_list(text, lowercase=lowercase)
    # [ (token, start, end), ... ]
    entity_positions = PhrasePositionFinder.find_phrase_in_source_text(
        text, list(tokens))

    resulted = ''
    src_index, first_token = 0, True
    for tok, s, _e in entity_positions:
        if first_token or spaces_on_start_end:
            resulted += ' '
        first_token = False
        while src_index < s:
            src_dest_map.append(len(resulted) - 1)
            src_index += 1

        for c_index, c in enumerate(tok):
            if spaces_after_dots and c == '.' and c_index > 0:
                resulted += ' '
            resulted += c
            src_dest_map.append(len(resulted) - 1)
            if spaces_after_dots and c == '.' and c_index < len(tok) - 1:
                resulted += ' '

            src_index += 1

    if spaces_on_start_end:
        resulted += ' '
    return resulted, src_dest_map


def reverse_src_to_dest_map(
        conv_map: List[int], normalized_text_len=0) -> List[int]:
    """       1         2         3         4         5
    012345678901234567890123456789012345678901234567890
    One one Bankr. E.D.N.C. two two two.
     One one Bankr . E . D . N . C . two two two . 
    
     0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,15,16,17,19  <- map
    [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,12,13,13  <- reversed
    """
    # pylint: disable=redefined-builtin
    reversed = []  # type: List[int]
    src_index = 0
    for index, dst_index in enumerate(conv_map):
        while src_index <= dst_index:
            reversed.append(index)
            src_index += 1
    if normalized_text_len and reversed and len(reversed) < normalized_text_len:
        reversed += [reversed[-1]] * (normalized_text_len - len(reversed))

    return reversed


def alias_is_banlisted(alias_ban_list: Optional[Dict[str, AliasBanList]],
                       norm_alias: str,
                       alias_lang: str,
                       is_abbrev: bool) -> bool:
    if not alias_ban_list:
        return False
    for lang in (alias_lang, None):
        lang_aliases = alias_ban_list.get(lang)  # type: Optional[AliasBanList]
        if lang_aliases:
            alias_lst = lang_aliases.abbreviations if is_abbrev else lang_aliases.aliases
            if norm_alias in alias_lst:
                return True
    return False


def _find_entity_positions(normalized_text: str,
                           normalized_text_lowercase: str,
                           entity: DictionaryEntry,
                           text_languages: Union[List[str], Tuple[str], Set[str]],
                           alias_language_order: Optional[List[str]],
                           context: Dict[int, SearchResultPosition] = None,
                           use_stemmer: bool = False,
                           abbrev_uppercase_check_range: int = 20,
                           min_alias_len: int = None,
                           alias_ban_list: Union[None, Dict[str, AliasBanList]] = None,
                           simplified_normalization: bool = False):
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
    :param alias_language_order: pick the alias with the default language among the others
    :param entity:
    :param context: Map of alias/name positions in the source text to SearchResultPosition entries.
    This context can be shared between multiple executions of this functions to reach the results of the overall search
    of multiple DictEntities with the longest matching DictEntity on each position.
    Can be None - for the case of single DictEntity search.
    :param alias_ban_list: Prepared ban list of aliases to exclude from search.
    Should be: dict of language -> tuple (list of normalized non-abbreviations, list of normalized abbreviations)
    "None" is a key for "any" language.
    :param abbrev_uppercase_check_range: To avoid false-positives in detecting abbreviations similar to AND, OR, IN
    we need to ensure that it is not english words appeared in a piece of text written in uppercase.
    For this for each abbrev we ignore it if text[position - range : position + range] == uppercase(text[...]).
    :return:
    """

    def abbrev_in_uppercase_block(text: str, position: int, check_range: int):
        block = text[max(0, position - check_range): min(len(text), position + check_range)]
        block_upper = block.upper()
        return block == block_upper

    if context is None:
        context = {}

    if not entity.aliases:
        return

    for ea in entity.aliases:
        alias_text = ea.alias
        alias_lang = ea.language
        alias_is_abbreviation = ea.is_abbreviation

        # get or create normalized alias
        normalized_alias = ea.normalized_alias if ea.normalized_alias \
            else normalize_text(alias_text,
                                lowercase=not alias_is_abbreviation,
                                use_stemmer=use_stemmer,
                                simple_tokenization=simplified_normalization)

        if not alias_text or (
                        text_languages and alias_lang and alias_lang not in text_languages):
            continue
        if min_alias_len and len(alias_text) < min_alias_len:
            continue

        normalized_text_for_alias = normalized_text if alias_is_abbreviation else normalized_text_lowercase

        if alias_is_banlisted(alias_ban_list, normalized_alias, alias_lang, alias_is_abbreviation):
            continue

        start = None
        while True:
            start = normalized_text_for_alias.find(
                normalized_alias, start + len(normalized_alias) - 1 if start is not None else 0)
            if start < 0:
                break

            if alias_is_abbreviation and \
                    abbrev_in_uppercase_block(normalized_text_for_alias, start, abbrev_uppercase_check_range):
                continue
            end = start + len(normalized_alias) - 1

            already_found = context.get(start)  # type: SearchResultPosition
            if already_found and len(already_found.alias_text) >= len(alias_text):
                already_found.add_entity(entity, ea, alias_language_order)
            else:
                context[start] = SearchResultPosition(
                    entity, ea, start, end, normalized_text[start: end])


class DictionaryEntity:
    def __init__(self, entity: Any, coords: Tuple[int, int]):
        self.entity = entity
        self.coords = coords

    def __repr__(self):
        ent_str = 'None'
        if self.entity:
            ent_str = str(self.entity[0])
            if len(self.entity) > 1:
                ent_str += f', {self.entity[1]}'
        coord_str = ', -'
        if self.coords:
            coord_str = f', @[{self.coords[0]}, {self.coords[1]}]'
        return ent_str + coord_str


def find_dict_entities(text: str,
                       all_possible_entities: List[DictionaryEntry],
                       default_language: str,
                       text_languages: Union[List[str], Tuple[str], Set[str]] = None,
                       conflict_resolving_func: Callable[[List[Tuple[DictionaryEntry, DictionaryEntryAlias]], str],
                                                         List[Tuple[DictionaryEntry, DictionaryEntryAlias]]] = None,
                       priority_direction: str = 'asc',
                       use_stemmer: bool = False,
                       remove_time_am_pm: bool = True,
                       min_alias_len: int = None,
                       prepared_alias_ban_list: Optional[Dict[str, AliasBanList]] = None,
                       simplified_normalization: bool = False)\
        -> Generator[DictionaryEntity, None, None]:
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
    :param default_language: the language that's preferred among several aliases
    :param min_alias_len: Minimal length of alias/name to search for. Can be used to ignore too short aliases like "M."
    while searching.
    :param prepared_alias_ban_list: List of aliases to remove from searching. Can be used to ignore concrete aliases.
    Prepared ban list of aliases to exclude from search.
    Should be: dict of language -> tuple (list of normalized non-abbreviations, list of normalized abbreviations)
    :param text_languages: If set - then only aliases of these languages will be searched for.
    :param conflict_resolving_func: A function for resolving conflicts when there are multiple entities detected
    at the same position in the source text and their detected aliases are of the same length.
    The function takes a list of conflicting entities and should return a list of one or more entities which
    should be returned.
    :param priority_direction: 'asc' or 'desc'
    :param use_stemmer: Use stemmer instead of tokenizer. Stemmer converts words to their simple form (singular number,
    e.t.c.). Stemmer works better for searching for "tables", "developers", ... Tokenizer fits for "United States",
    "Mississippi", ...
    :param remove_time_am_pm: Remove from final results AM/PM abbreviations which look like end part of time
    strings - 11:45 am, 10:00 pm.
    :param simplified_normalization: Don't use NLTK for text "normalization"
    :return:
    """

    if not text:
        return

    # text (usually bloated with spaces) plus map:
    # map[i] = I, where i is the character coordinate within the source text,
    # I is the same character's coordinate within the resulted text
    normalized_text, norm_map = normalize_text_with_map(text,
                                                        lowercase=False,
                                                        use_stemmer=use_stemmer,
                                                        simple_tokenization=False)
    normalized_text_lowercase = normalized_text.lower()

    search_context = {}
    # Search for each DictEntity occurrence adding them into the shared search context.
    # while searching for entities from the dictionary by their attributes / aliases
    # we may
    alias_lang_order = [default_language] + (text_languages or [])
    for dict_entity in all_possible_entities:
        _find_entity_positions(normalized_text,
                               normalized_text_lowercase,
                               dict_entity,
                               text_languages,
                               alias_lang_order,
                               search_context,
                               use_stemmer=use_stemmer,
                               min_alias_len=min_alias_len,
                               alias_ban_list=prepared_alias_ban_list,
                               simplified_normalization=simplified_normalization)

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
    prev_pos = None  # type: Optional[SearchResultPosition]

    def resolve_conflicts(pos: SearchResultPosition) \
            -> List[DictionaryEntity]:
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
            return [DictionaryEntity(entities_at_pos[0], (pos.start, pos.end))]
        cfree_ents = conflict_resolving_func(entities_at_pos, priority_direction) \
            if conflict_resolving_func else entities_at_pos
        return [DictionaryEntity(ent, (pos.start, pos.end))
                for ent in cfree_ents]

    # [ (start, data), ... ]
    search_results = sorted(search_context.items())  # type: List[Tuple[int, SearchResultPosition]]
    if not search_results:
        return
    # refine search results coordinates using norm_map
    rev_map = reverse_src_to_dest_map(norm_map, len(normalized_text))
    for i, search_result in enumerate(search_results):
        search_result = search_result[1]
        text_fragment = search_result.source_text
        norm_start = search_result.start + 1 if text_fragment.startswith(' ') else search_result.start
        norm_end = search_result.end - 1 if text_fragment.endswith(' ') else search_result.end

        search_result.start = rev_map[norm_start]
        search_result.end = rev_map[norm_end]
        search_results[i] = (search_result.start, search_result)

    for _index, next_pos in search_results:
        if prev_pos and not next_pos.overlaps(prev_pos):
            for entity in resolve_conflicts(prev_pos):
                yield entity
            prev_pos = next_pos
        else:
            prev_pos = prev_pos if prev_pos and \
                                   len(prev_pos.alias_text) >= len(next_pos.alias_text) else next_pos

    if prev_pos:
        resolved_ents = resolve_conflicts(prev_pos)
        for entity in resolved_ents:
            yield entity


def conflicts_take_first_by_id(
        conflicting_entities_aliases: List[Tuple[DictionaryEntry, DictionaryEntryAlias]],
        priority_direction: str = 'asc') \
        -> List[Tuple[DictionaryEntry, DictionaryEntryAlias]]:
    """
    Default conflict resolving function for dropping all entities detected at the same position excepting the one
    having the smallest id. To be used in find_dict_entities() method.
    """
    target_func = min if priority_direction == 'asc' else max
    return [target_func(conflicting_entities_aliases, key=lambda entity_alias_pair: entity_alias_pair[0].id)]


def conflicts_top_by_priority(
        conflicting_entities_aliases: List[Tuple[DictionaryEntry, DictionaryEntryAlias]],
        priority_direction: str = 'asc') \
        -> List[Tuple[DictionaryEntry, DictionaryEntryAlias]]:
    """
    Default conflict resolving function for dropping all entities detected at the same position excepting the one
    having the smallest id. To be used in find_dict_entities() method.
    """
    target_func = max if priority_direction == 'asc' else min
    return [target_func(
        conflicting_entities_aliases,
        key=lambda entity_alias_pair: entity_alias_pair[0].priority)]


def prepare_alias_banlist_dict(alias_banlist: List[AliasBanRecord],
                               use_stemmer: bool = False) \
        -> Optional[Dict[str, AliasBanList]]:
    """
    Prepare alias ban list for providing it to find_dict_entities() function.
    :param alias_banlist: Non-normalized form of the banlist: [(alias, lang, is_abbrev), ...]
    :param use_stemmer: Use stemmer for alias normalization. Otherwise - tokenizer only.
    :return:
    """
    if not alias_banlist:
        return None

    # language - aliases (both full and abbreviated)
    res = {}  # type: Dict[str, AliasBanList]
    for record in alias_banlist:
        lang_tuple = res.get(record.lang)
        if lang_tuple is None:
            lang_tuple = AliasBanList()
            res[record.lang] = lang_tuple
        if record.is_abbrev:
            lang_tuple.abbreviations.append(normalize_text(record.alias,
                                                           lowercase=False, use_stemmer=use_stemmer))
        else:
            lang_tuple.aliases.append(normalize_text(record.alias,
                                                     lowercase=True, use_stemmer=use_stemmer))
    return res
