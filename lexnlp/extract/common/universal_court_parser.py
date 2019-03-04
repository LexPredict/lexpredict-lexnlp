# pylint: disable=unused-import

import re
import pandas as pd
from typing import List, Tuple

from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.utils.lines_processing.line_processor import LineProcessor, LineSplitParams, LineOrPhrase
from lexnlp.utils.lines_processing.phrase_finder import PhraseFinder, PhraseMatch


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ParserInitParams:
    """
    UniversalCourtsParser initialization parameters
    """
    def __init__(self):
        self.court_pattern_checker = None  # type: re
        self.column_names = {
            'type': 'Court Type',
            'name': 'Court Name',
            'jurisdiction': 'Jurisdiction',
            'alias': 'Alias'
        }
        self.dataframe_paths = []  # type: List[str]
        self.split_ptrs = None   # type: LineSplitParams
        self.key_word_preproc_func = None  # def (text:str) -> str


class MatchFound:
    def __init__(self, subset, entry_start: int, entry_end: int, text: str):
        self.subset = subset
        self.is_exact = len(subset) == 1
        self.court_name = None
        self.jurisdiction = None
        self.court_type = None
        self.entry_start = entry_start
        self.entry_end = entry_end
        self.text = text

    def __repr__(self):
        length = 'nil' if self.subset is None else str(len(self.subset))
        court_name = 'court name: ' + self.court_name if self.court_name is not None else ''
        court_type = 'court type: ' + self.court_type if self.court_type is not None else ''
        court_jur = 'jurisdiction: ' + self.jurisdiction \
            if self.jurisdiction is not None else ''
        return ' '.join(['Exact: ', self.is_exact, '[' + length + ']',
                         court_name, court_type, court_jur])

    def make_sort_key(self):
        return 0 if self.is_exact else 10 if len(self.subset) == 0 else len(self.subset)


class UniversalCourtsParser:
    """
    The class describes a "constructor" for building locale (and region) specific
    parsers, that find reference to courts within the text.

    Use the parse() method to find all reference to courts from the
    text provided.
    Each reference is a dictionary with two keys:
    - "attrs" key leads to the "coordinates" (starting and ending characters) of the
      occurrence within the provided text
    - "tags" key leads to another dictionary, which contains:
      - court official name
      - court's jurisdiction ...

    In order to parse the text you are supposed to create your locale (or region) specific instance of
    UniversalCourtsParser. See the constructor below:
    """

    def __init__(self, ptrs: ParserInitParams):
        """
        :param ptrs.court_pattern_checker: a regex or None, the parser skips the phrase if pattern doesn't match the phrase
        :param ptrs.column_names['type']: "Court Type", e.g. 'Federal District Court'
        :param ptrs.column_names['name']: "Court Name", e.g. 'Southern Georgia District Court'
        :param ptrs.column_names['jurisdiction']: "Jurisdiction", e.g. 'Federal'
        :param ptrs.column_names['alias']: "Alias", e.g. 'C.D. Cal'
        :param ptrs.dataframe_paths: like ['data/us_courts.csv', ...]
        :param ptrs.split_ptrs: phrase splitting processor parameters, see LineProcessor class
        :param ptrs.key_word_preproc_func: a function used to pre-process column values used in text search

        dataframe_paths is a collection of *.CSV files that contain the data like:

        | Jurisdiction || Court Type         || Court Name               || ... |
        | Federal      || Verfassungsgericht || Bundesverfassungsgericht || ... |

        The column 'Court Name' (you may provide another column name instead of Court Name
        in param: court_name_column) should contain unique values that precisely identify each
        of the court given.

        The columns 'Court Type' (param: court_type_column) and 'Jurisdiction'
        (param: jurisdiction_column) in couple may or may not precisely identify the court given.

        At least this parser can identify the court's type and return the annotation that
        neither specifies the court's name nor jurisdiction

        The court_pattern_checker parameter speeds up the parsing process:
        - the whole text or the line would be skipped if this line doesn't match the court_pattern_checker
        E.g., you can pass re.compile('court', re.IGNORECASE) for searching courts' annotations
        for the En locale

        The split_ptrs specify how the parser splits the text into phrases.
        Each phrase can contain zero ore one court annotations. See LineProcessor class.
        For a courts parser phrase bounds usually include punctuation (.,;!?) and conjunctions
        (and, or) or (und, oder)

        The example function for key_word_preproc_func is:
        def preproc_func(text):
             return re.sub('e$', '[e]?', text)
        """

        self.phrase_match_pattern = None if ptrs.court_pattern_checker is None \
            else ptrs.court_pattern_checker
        self.court_type_column = ptrs.column_names['type']
        self.court_name_column = ptrs.column_names['name']
        self.court_alias_column = ptrs.column_names['alias']
        self.jurisdiction_column = ptrs.column_names['jurisdiction']
        self.proc = LineProcessor()
        self.phrase_split_ptrs = ptrs.split_ptrs
        self.annotations = []  # type: List[CourtAnnotation]
        self.courts = None
        self.load_courts(ptrs.dataframe_paths)
        self.locale = None

        # unique columns
        self.finder_court_name = PhraseFinder(UniversalCourtsParser.get_unique_col_values(
            self.courts[self.court_name_column]), ptrs.key_word_preproc_func)
        self.finder_court_alias = None if len(self.court_alias_column) == 0 else \
            PhraseFinder(UniversalCourtsParser.get_unique_col_values(
                self.courts[self.court_alias_column]), ptrs.key_word_preproc_func)

        # non-unique columns
        self.finder_court_type = PhraseFinder(UniversalCourtsParser.get_unique_col_values(
            self.courts[self.court_type_column]), ptrs.key_word_preproc_func)
        self.finder_jur = PhraseFinder(UniversalCourtsParser.get_unique_col_values(
            self.courts[self.jurisdiction_column]), ptrs.key_word_preproc_func)

    def parse(self, text: str, locale: str = None) -> List[CourtAnnotation]:
        """
        :param text: the text being processed
        :param locale: 'En', 'Es', ...
        :return: annotations - List[dict]

        Here is an example of the method's call:
        ret = processor.parse("Bei dir läuft, deine Verfassungsgerichtshof des Freistaates Sachsen rauchen Joints vor der Kamera")

        ret[0]['attrs'] = {'start': 14, 'end': 97}
        ret[0]['tags'] = {'Extracted Entity Type': 'court',
            'Extracted Entity Court Name': 'Verfassungsgerichtshof des Freistaates Sachsen',
            'Extracted Entity Court Type': 'Verfassungsgericht',
            'Extracted Entity Court Jurisdiction': 'Sachsen'}
        """
        self.annotations = []
        self.locale = locale
        self.find_courts_by_alias_in_whole_text(text)

        # if the whole text doesn't contain the key word (gericht) - skip all the following
        if self.phrase_match_pattern is not None:
            if self.phrase_match_pattern.search(text, re.IGNORECASE) is None:
                return self.annotations

        for phrase in self.proc.split_text_on_line_with_endings(text, self.phrase_split_ptrs):
            # if the phrase doesn't contain the key word (e.g., gericht for deutsche) - skip the phrase
            if self.phrase_match_pattern is not None:
                if self.phrase_match_pattern.search(phrase.text, re.IGNORECASE) is None:
                    continue
            self.find_court_by_any_key(phrase)

        return self.annotations

    def load_courts(self, dataframe_paths: List[str]):
        frames = []
        dtypes = {self.court_type_column: str,
                  self.court_name_column: str,
                  self.jurisdiction_column: str}
        if self.court_alias_column:
            dtypes[self.court_alias_column] = str

        for path in dataframe_paths:
            frame = pd.read_csv(path, encoding="utf-8", error_bad_lines=False,
                                converters=dtypes)
            frames.append(frame)
        self.courts = pd.concat(frames)

    def find_courts_by_alias_in_whole_text(self, text: str) -> None:
        if self.finder_court_alias is None:
            return
        for m in self.finder_court_alias.find_word(text):
            alias = m[0]
            rows = self.courts.loc[self.courts[self.court_alias_column] == alias]
            match_found = MatchFound(rows, m[1], m[2], text[m[1]:m[2]])
            self.add_annotation(match_found)

    def find_court_by_any_key(self, phrase: LineOrPhrase):
        # find by court names
        matches = []
        matches += self.find_court_by_name(phrase)
        matches += self.find_court_by_type_and_jurisdiction(phrase)
        matches = [m for m in matches if m is not None]
        if len(matches) == 0:
            return
        # find the best match
        matches.sort(key=lambda m: m.make_sort_key())
        self.add_annotation(matches[0])

    def find_court_by_name(self, phrase: LineOrPhrase) -> List[MatchFound]:
        match = self.find_court_by_key_column(phrase, self.finder_court_name,
                                                self.court_name_column)
        if match is None:
            return []

        match[0].court_name = match[1][0][0]
        return [match[0]]

    def find_court_by_key_column(self, phrase: LineOrPhrase,
                                 phrase_finder: PhraseFinder,
                                 column: str) -> Tuple[MatchFound, List[PhraseMatch]]:
        found_substrings = phrase_finder.find_word(phrase.text, True)
        if len(found_substrings) == 0:
            return None
        subset = self.courts.loc[self.courts[column] == found_substrings[0][0]]
        if len(subset) == 0:
            return None

        start = found_substrings[0][1]
        end = found_substrings[0][2]
        match = MatchFound(subset,
                           phrase.start + start,
                           phrase.start + end,
                           phrase.text[start:end])
        return (match, found_substrings)

    def find_court_by_type_and_jurisdiction(self, phrase: LineOrPhrase) -> List[MatchFound]:
        court_types = self.finder_court_type.find_word(phrase.text, True)
        if len(court_types) == 0:
            return []

        court_jurs = self.finder_jur.find_word(phrase.text, True)
        if len(court_types) != 1 or len(court_jurs) > 1:
            # special case: 2 ore more courts within the same phrase
            # (without commas or conjuctions)
            matches = []
            for ct in court_types:
                m = MatchFound([],
                               phrase.start + ct[1],
                               phrase.start + ct[2],
                               phrase.text[ct[1]:ct[2]])
                m.court_type = ct[0]
                m.court_name = ct[0]
                matches.append(m)
            return matches

        if len(court_jurs) == 0:
            subset = self.courts.loc[self.courts[self.court_type_column] == court_types[0][0]]
        else:
            subset = self.courts.loc[(self.courts[self.court_type_column] == court_types[0][0]) &
                                     (self.courts[self.jurisdiction_column] == court_jurs[0][0])]

        match = MatchFound(subset,
                           phrase.start,
                           phrase.start + court_types[0][2],
                           phrase.text[0:court_types[0][2]])
        if len(subset) != 1:
            match.court_name = court_types[0][0]
            match.court_type = court_types[0][0]
        return [match]

    def add_annotation(self, match: MatchFound):
        mlen = len(match.subset)

        name = match.subset[self.court_name_column].values[0] \
            if match.is_exact else \
            match.court_name if match.court_name is not None else \
            match.subset[self.court_name_column].values[0] if mlen > 0 else ''

        court_type = match.subset[self.court_type_column].values[0] \
            if match.is_exact else \
            match.court_type if match.court_type is not None else \
            match.subset[self.court_type_column].values[0] if mlen > 0 else ''

        jurisdiction = match.subset[self.jurisdiction_column].values[0] \
            if match.is_exact else \
            match.jurisdiction if match.jurisdiction is not None else \
                match.subset[self.jurisdiction_column].values[0] if mlen > 0 else ''

        ant = CourtAnnotation(name=name, coords=(match.entry_start, match.entry_end),
                              locale=self.locale, text=match.text)
        ant.jurisdiction = jurisdiction
        ant.court_type = court_type
        self.annotations.append(ant)

    @staticmethod
    def get_unique_col_values(col_values):
        return [c for c in col_values.unique() if c]
