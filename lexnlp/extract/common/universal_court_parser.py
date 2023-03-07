# pylint: disable=unused-import

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
import pandas
from typing import Callable, Generator, List, Optional, Tuple

from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.utils.lines_processing.line_processor import LineProcessor, LineSplitParams, LineOrPhrase
from lexnlp.utils.lines_processing.phrase_finder import PhraseFinder, PhraseMatch


class ParserInitParams:
    """
    UniversalCourtsParser initialization parameters
    """
    def __init__(self):
        self.court_pattern_checker: Optional[re.Pattern] = None
        self.column_names = {
            'type': 'Court Type',
            'name': 'Court Name',
            'jurisdiction': 'Jurisdiction',
            'alias': 'Alias'
        }
        self.dataframe_paths: List[str] = []
        self.split_ptrs: Optional[LineSplitParams] = None
        self.key_word_preproc_func: Optional[Callable[[str], str]] = None


class MatchFound:
    def __init__(self, subset, entry_start: int, entry_end: int, text: str):
        self.subset = subset
        self.is_exact: bool = len(subset) == 1
        self.court_name = None
        self.jurisdiction = None
        self.court_type = None
        self.entry_start = entry_start
        self.entry_end = entry_end
        self.text = text

    def __repr__(self) -> str:
        length = 'nil' if self.subset is None else str(len(self.subset))
        court_name = 'court name: ' + self.court_name if self.court_name is not None else ''
        court_type = 'court type: ' + self.court_type if self.court_type is not None else ''
        court_jur = 'jurisdiction: ' + self.jurisdiction if self.jurisdiction is not None else ''
        return f'Exact: {self.is_exact} [{length}] {court_name} {court_type} {court_jur}'

    def make_sort_key(self) -> int:
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
        Each phrase can contain zero or one court annotations. See LineProcessor class.
        For a courts parser phrase bounds usually include punctuation (.,;!?) and conjunctions
        (and, or) or (und, oder)

        The example function for key_word_preproc_func is:
        def preproc_func(text):
             return re.sub('e$', '[e]?', text)
        """

        self.phrase_match_pattern = None if ptrs.court_pattern_checker is None else ptrs.court_pattern_checker
        self.court_type_column = ptrs.column_names['type']
        self.court_name_column = ptrs.column_names['name']
        self.court_alias_column = ptrs.column_names['alias']
        self.jurisdiction_column = ptrs.column_names['jurisdiction']
        self.proc: LineProcessor = LineProcessor(line_split_params=ptrs.split_ptrs)
        self.courts: pandas.DataFrame = self.load_courts(ptrs.dataframe_paths)
        self.locale: Optional[str] = None

        # unique columns
        self.finder_court_alias = (
            None
            if len(self.court_alias_column) == 0
            else PhraseFinder(
                UniversalCourtsParser.get_unique_col_values(self.courts[self.court_alias_column]),
                ptrs.key_word_preproc_func,
            )
        )
        self.finder_court_name = PhraseFinder(
            phrase_set=UniversalCourtsParser.get_unique_col_values(self.courts[self.court_name_column]),
            extra_format_function=ptrs.key_word_preproc_func,
        )

        # non-unique columns
        self.finder_court_type = PhraseFinder(
            UniversalCourtsParser.get_unique_col_values(self.courts[self.court_type_column]),
            ptrs.key_word_preproc_func,
        )
        self.finder_jur = PhraseFinder(
            UniversalCourtsParser.get_unique_col_values(self.courts[self.jurisdiction_column]),
            ptrs.key_word_preproc_func,
        )

    def parse(self, text: str, locale: str = None) -> Generator[CourtAnnotation, None, None]:
        """
        Args:
            text (str):
                An input string from which to extract CourtAnnotations.

            locale (str):
                A locale string ("en", "de", "es") to use in CourtAnnotation formation.

        Yields:
            CourtAnnotation

        Here is an example of the method's call:
        ret = parser.parse("Bei dir läuft, deine Verfassungsgerichtshof des Freistaates Sachsen rauchen Joints vor der Kamera")

        ret[0]['attrs'] = {'start': 14, 'end': 97}
        ret[0]['tags'] = {'Extracted Entity Type': 'court',
            'Extracted Entity Court Name': 'Verfassungsgerichtshof des Freistaates Sachsen',
            'Extracted Entity Court Type': 'Verfassungsgericht',
            'Extracted Entity Court Jurisdiction': 'Sachsen'}
        """
        self.locale: Optional[str] = locale
        yield from self.find_courts_by_alias_in_whole_text(text)

        # if the whole text doesn't contain the key word (-gericht), skip all the following
        if self.phrase_match_pattern is not None:
            if self.phrase_match_pattern.search(text, re.IGNORECASE) is None:
                return

        for phrase in self.proc.split_text_on_line_with_endings(text):
            # if the phrase doesn't contain the key word (e.g., "Gericht" for German), skip the phrase
            if self.phrase_match_pattern is not None:
                if self.phrase_match_pattern.search(phrase.text, re.IGNORECASE) is None:
                    continue
            annotation = self.find_court_by_any_key(phrase)
            if annotation:
                yield annotation

    def load_courts(self, dataframe_paths: List[str]) -> pandas.DataFrame:
        frames = []
        dtypes = {
            self.court_type_column: str,
            self.court_name_column: str,
            self.jurisdiction_column: str,
        }
        if self.court_alias_column:
            dtypes[self.court_alias_column] = str
        for path in dataframe_paths:
            frame = pandas.read_csv(path, encoding="utf-8", converters=dtypes)
            frames.append(frame)
        if frames:
            return pandas.concat(frames)
        return pandas.DataFrame()

    def find_courts_by_alias_in_whole_text(self, text: str) -> Generator[CourtAnnotation, None, None]:
        if self.finder_court_alias:
            for m in self.finder_court_alias.find_word(text):
                alias = m[0]
                rows = self.courts.loc[self.courts[self.court_alias_column] == alias]
                match_found = MatchFound(rows, m[1], m[2], text[m[1]:m[2]])
                yield self.create_annotation(match_found)

    def find_court_by_any_key(self, phrase: LineOrPhrase) -> Optional[CourtAnnotation]:
        # find by court names
        matches = []
        matches += self.find_court_by_name(phrase)
        matches += self.find_court_by_type_and_jurisdiction(phrase)
        matches = [m for m in matches if m is not None]
        if matches:
            # find the best match
            matches.sort(key=lambda m: m.make_sort_key())
            annotation = self.create_annotation(matches[0])
            return annotation

    def find_court_by_name(self, phrase: LineOrPhrase) -> List[MatchFound]:
        match = self.find_court_by_key_column(phrase, self.finder_court_name, self.court_name_column)
        if match is None:
            return []

        match[0].court_name = match[1][0][0]
        return [match[0]]

    def find_court_by_key_column(
        self,
        phrase: LineOrPhrase,
        phrase_finder: PhraseFinder,
        column: str,
    ) -> Optional[Tuple[MatchFound, List[PhraseMatch]]]:
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
        return match, found_substrings

    def find_court_by_type_and_jurisdiction(self, phrase: LineOrPhrase) -> List[MatchFound]:
        court_types = self.finder_court_type.find_word(phrase.text, True)
        if len(court_types) == 0:
            return []

        court_jurs = self.finder_jur.find_word(phrase.text, True)
        if len(court_types) != 1 or len(court_jurs) > 1:
            # special case: 2 or more courts within the same phrase
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

    def create_annotation(self, match: MatchFound) -> CourtAnnotation:
        len_match = len(match.subset)

        name = (
            match.subset[self.court_name_column].values[0]
            if match.is_exact
            else match.court_name
            if match.court_name is not None
            else match.subset[self.court_name_column].values[0]
            if len_match > 0
            else ""
        )

        court_type = (
            match.subset[self.court_type_column].values[0]
            if match.is_exact
            else match.court_type
            if match.court_type is not None
            else match.subset[self.court_type_column].values[0]
            if len_match > 0
            else ""
        )

        jurisdiction = (
            match.subset[self.jurisdiction_column].values[0]
            if match.is_exact
            else match.jurisdiction
            if match.jurisdiction is not None
            else match.subset[self.jurisdiction_column].values[0]
            if len_match > 0
            else ""
        )

        annotation = CourtAnnotation(
            name=name,
            coords=(match.entry_start, match.entry_end),
            locale=self.locale,
            text=match.text,
            jurisdiction=jurisdiction,
            court_type=court_type
        )

        return annotation

    @staticmethod
    def get_unique_col_values(col_values):
        return [c for c in col_values.unique() if c]
