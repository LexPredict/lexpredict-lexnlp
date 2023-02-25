"""Section segmentation for English.

This module implements section segmentation in English using simple
machine learning classifiers.

Todo:
  * Standardize model (re-)generation
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import string
import unicodedata

from typing import Generator, List, Optional, Tuple, Any, Union

# Packages
import pandas
import regex as re
import joblib

# Project imports
from lexnlp.nlp.en.segments.utils import build_document_line_distribution
from lexnlp.utils.map import Map
from lexnlp.utils.decorators import safe_failure
from lexnlp.nlp.en.segments.heading_heuristics import HeadingHeuristics


# Setup module path


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


class SectionSegmenterModel:
    SECTION_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./section_segmenter.pickle"))
    FEATURE_NAMES = []


class DocumentSection:
    def __init__(self,
                 start: int = 0,
                 end: int = 0,
                 title: str = '',
                 title_start: int = 0,
                 title_end: int = 0,
                 level: int = 0,
                 abs_level: int = 0,
                 text: str = ''):
        self.start = start
        self.end = end
        self.title = title
        self.title_start = title_start
        self.title_end = title_end
        self.level = level
        self.abs_level = abs_level
        self.text = text

    def __str__(self):
        return f'{self.title} [{self.start}: {self.end}]'

    def __eq__(self, other):
        if not isinstance(other, DocumentSection):
            return NotImplemented

        return self.start == other.start and self.end == other.end \
            and self.title == other.title and self.title_start == other.title_start \
            and self.title_end == other.title_end and self.level == other.level \
            and self.abs_level == other.abs_level and self.text == other.text


def build_section_break_features(
        lines,
        line_id,
        line_window_pre,
        line_window_post,
        characters=string.printable,
        include_doc=None):
    """
    Build a feature vector for a given line ID with given parameters.
    """
    # Feature vector
    feature_vector = {}

    # Check start offset
    if line_id < line_window_pre:
        line_window_pre = line_id

    # Check final offset
    if (line_id + line_window_post) >= len(lines):
        line_window_post = len(lines) - line_window_post - 1

    # Iterate through window
    for i in range(-line_window_pre, line_window_post + 1):
        try:
            line = lines[line_id + i]
        except IndexError:
            continue

        # Count length
        feature_vector['line_len_{0}'.format(i)] = len(line)
        feature_vector['line_lenstrip_{0}'.format(i)] = len(line.strip())
        feature_vector['line_title_case_{0}'.format(i)] = line == line.title()
        feature_vector['line_upper_case_{0}'.format(i)] = line == line.upper()

        # Count characters
        feature_vector['line_n_alpha_{0}'.format(i)] = sum([1 for c in line if unicodedata.category(c).startswith('L')])
        feature_vector['line_n_number_{0}'.format(i)] = sum(
            [1 for c in line if unicodedata.category(c).startswith('N')])
        feature_vector['line_n_punct_{0}'.format(i)] = sum([1 for c in line if unicodedata.category(c).startswith('P')])
        feature_vector['line_n_whitespace_{0}'.format(i)] = sum(
            [1 for c in line if unicodedata.category(c).startswith('Z')])

    # Simple checks
    line = lines[line_id]
    line_stripped = line.strip()
    len_line_stripped = len(line_stripped)
    feature_vector['section'] = 1 if 'section' in line else 0
    feature_vector['SECTION'] = 1 if 'SECTION' in line else 0
    feature_vector['Section'] = 1 if 'Section' in line else 0
    feature_vector['article'] = 1 if 'article' in line else 0
    feature_vector['ARTICLE'] = 1 if 'ARTICLE' in line else 0
    feature_vector['Article'] = 1 if 'Article' in line else 0
    feature_vector['sw_section'] = 1 if line_stripped.lower().startswith('section') else 0
    feature_vector['sw_article'] = 1 if line_stripped.lower().startswith('article') else 0
    feature_vector['first_char_punct'] = (line_stripped[0] in string.punctuation) if len_line_stripped > 0 else False
    feature_vector['last_char_punct'] = (line_stripped[-1] in string.punctuation) if len_line_stripped > 0 else False
    feature_vector['first_char_number'] = (line_stripped[0] in string.digits) if len_line_stripped > 0 else False
    feature_vector['last_char_number'] = (line_stripped[-1] in string.digits) if len_line_stripped > 0 else False

    # Build character vector
    for character in characters:
        feature_vector["char_{0}".format(character)] = line.count(character)

    # Add doc if requested
    if include_doc:
        feature_vector.update(include_doc)

    return feature_vector


def get_section_feature_names(
        lines_count,
        line_window_pre,
        line_window_post,
        characters=string.printable,
        include_doc=None):
    # Feature vector titles
    feature_vector = {
        'section',
        'SECTION',
        'Section',
        'article',
        'ARTICLE',
        'Article',
        'sw_section',
        'sw_article',
        'first_char_punct',
        'last_char_punct',
        'first_char_number',
        'last_char_number'}

    # Check start offset
    if lines_count - 1 < line_window_pre:
        line_window_pre = lines_count - 1

    # Check final offset
    if line_window_post >= lines_count:
        line_window_post = lines_count - line_window_post - 1

    # Iterate through window
    for i in range(-line_window_pre, line_window_post + 1):
        # Count length
        feature_vector.add(f'line_len_{i}')
        feature_vector.add(f'line_lenstrip_{i}')
        feature_vector.add(f'line_title_case_{i}')
        feature_vector.add(f'line_upper_case_{i}')

        # Count characters
        feature_vector.add(f'line_n_alpha_{i}')
        feature_vector.add(f'line_n_number_{i}')
        feature_vector.add(f'line_n_punct_{i}')
        feature_vector.add(f'line_n_whitespace_{i}')

    # Build character vector
    for character in characters:
        feature_vector.add(f'char_{character}')

    # Add doc if requested
    if include_doc:
        feature_vector.update(set(include_doc.keys()))

    return feature_vector


# TODO: we let errors arise silently
@safe_failure
def get_sections(text, window_pre=3, window_post=3, score_threshold=0.5) -> Generator:
    """
    Get sections from text.
    NLP-based detection of sections.
    :param text:
    :param window_pre:
    :param window_post:
    :param score_threshold:
    :return:
    """

    # Get document character distribution
    doc_distribution = build_document_line_distribution(text)
    lines = text.splitlines()
    test_feature_data = []
    for line_id in range(len(lines)):
        test_feature_data.append(
            build_section_break_features(lines, line_id, window_pre, window_post, include_doc=doc_distribution))

    # Predict page breaks
    columns = list(get_section_feature_names(len(lines), window_pre, window_post, include_doc=doc_distribution))
    columns.sort()
    test_feature_df = pandas.DataFrame(test_feature_data, columns=columns).fillna(-1)
    test_predicted_lines = SectionSegmenterModel.SECTION_SEGMENTER_MODEL.predict_proba(test_feature_df)
    predicted_df = pandas.DataFrame(test_predicted_lines, columns=["prob_false", "prob_true"])
    section_breaks = predicted_df.loc[predicted_df["prob_true"] >= score_threshold, :].index.tolist()

    if len(section_breaks) > 0:
        # Get first break
        pos0 = 0
        pos1 = section_breaks[0]
        section = "\n".join(lines[pos0:pos1])
        if len(section.strip()) > 0:
            yield section

        # Iterate through section breaks
        for i in range(len(section_breaks) - 1):
            # Get breaks
            pos0 = section_breaks[i]
            pos1 = section_breaks[i + 1]
            # Get text
            section = "\n".join(lines[pos0:pos1])
            if len(section.strip()) > 0:
                yield section

        # Yield final section
        section = "\n".join(lines[section_breaks[-1]:])
        if len(section.strip()) > 0:
            yield section


SECTION_TITLE_PTN = r"""
\s*
(
    (?i:(?:appendix|part|section|article|(?:sub)?title|EXHIBIT|SCHEDULE)\s+)?
    (?-i:\d+(?:\.\d+)?
         |
         \p{Lu}(?:-\d+(?:\.\d+)?)?
         |
         [XVILCM]+
         |
         \((?:\d{1,3}|\p{L}+)\)
    )
)
(?:\.|\s|$)
"""
SECTION_TITLE_RE1 = re.compile(r'(?<=[,\.:>;\d\n\s]\n)' + SECTION_TITLE_PTN, re.M | re.X)
SECTION_TITLE_RE2 = re.compile(r'\A' + SECTION_TITLE_PTN, re.M | re.X)


@safe_failure
def get_sections_re(text) -> Generator:
    """
    Get sections from text.
    Regex-based detection of text sections.
    :param text: str - source full text
    :return: generator of str
    """
    prev_start = None
    for match in SECTION_TITLE_RE1.finditer(text):
        start = match.start()
        if prev_start:
            yield text[prev_start:start]
        elif start != 0:
            yield text[0:start]
        prev_start = start
    if prev_start:
        yield text[prev_start:]


@safe_failure
def get_section_spans(text: str,
                      use_ml=True,
                      return_text=True,
                      skip_empty_headers=False,
                      sections_hierarchy: Optional[List[Any]] = None) -> \
        Generator[DocumentSection, None, None]:
    """
    Get sections from text.
    Use NLP-based detection OR regex-bases detection of sections - see use_ml param.
    :param text: str - source full text
    :param use_ml: bool - use sklearn classifier otherwise use regex-based detection
    :param return_text: bool - return section text
    :param skip_empty_headers: bool - return results containing headers only
    :param sections_hierarchy: list of regexes
    :return: Generator of dictionaries
    """

    _start_index_counter = 0
    level_parser = SectionLevelParser(sections_hierarchy=sections_hierarchy)
    sections_detector = get_sections if use_ml else get_sections_re

    for section in sections_detector(text):
        start_index = _start_index_counter + text[_start_index_counter:].index(section)
        end_index = start_index + len(section)
        _start_index_counter = end_index
        try:
            title = SECTION_TITLE_RE2.findall(section)[0]
            title_start = start_index + section.index(title)
            title_end = title_start + len(title)
        except IndexError:
            # wrong number of features (short text or smth similar)
            title = title_start = title_end = None
        if skip_empty_headers and not title:
            continue

        # try to get level
        level, abs_level = level_parser.detect(title)

        res = DocumentSection(
            start=start_index,
            end=end_index,
            title=title,
            title_start=title_start,
            title_end=title_end,
            level=level,
            abs_level=abs_level,
        )
        if return_text:
            res.text = section
        yield res


class SectionLevelParser:

    DEFAULT_SECTION_HIERARCHY = [
        r'(?i:(appendix|exhibit|schedule|part|title)\s+\S+)',
        r'(?i:subtitle\s+\S+)',
        r'(?i:section\s+\S+)',
        r'(?i:subsection\s+\S+)',
        r'(?i:article\s+\S+)',
        r'\p{Lu}+(?:-\d+(?:\.\d+)?)?',
        r'[\d\.]+',
        r'\p{L}+(?:-\d+(?:\.\d+)?)?',
        r'\([\p{L}\d]+\)'
    ]

    def __init__(self, sections_hierarchy: Optional[List[str]] = None):
        if not sections_hierarchy:
            sections_hierarchy = self.DEFAULT_SECTION_HIERARCHY
        self.default_sections_hierarchy = [Map(regex=re.compile(i),
                                               abs_level=n,
                                               rel_level=None)
                                           for n, i in enumerate(sections_hierarchy, start=1)]
        self.level = 1        # represents previous->current relative level (new custom hierarchy)
        self.abs_level = 1    # represents previous->current absolute level from sections_hierarchy
        self.prev_level_re = None
        self.title = ''

    @property
    def current_sections_hierarchy(self):
        return [i for i in self.default_sections_hierarchy if i.rel_level]

    def detect(self, title: str) -> Tuple[int, int]:
        self.title = title
        if not title:
            return 0, 0
        if self.prev_level_re and self.prev_level_re.match(title):
            return self.level, self.abs_level
        if self.current_sections_hierarchy:
            levels = self.get_from_detected()
            if levels is not None:
                return levels
        self.get_from_default()
        return self.level, self.abs_level

    def get_from_detected(self) -> Optional[Tuple[int, int]]:
        for level_data in self.current_sections_hierarchy:
            if level_data.regex.match(self.title):
                self.level = level_data.rel_level
                self.abs_level = level_data.abs_level
                self.prev_level_re = level_data.regex
                return self.level, self.abs_level
        return None

    def get_from_default(self):
        for level_data in self.default_sections_hierarchy:
            if level_data.regex.match(self.title):
                if level_data.abs_level > self.abs_level:
                    self.level += 1
                elif level_data.abs_level < self.abs_level:
                    self.level -= 1
                level_data.rel_level = self.level
                self.abs_level = level_data.abs_level
                self.prev_level_re = level_data.regex
                break


def get_document_sections_with_titles(
        full_text: str,
        sentence_list: List[Union[Tuple[int, int], Tuple[int, int, str]]],
        use_ml=False) -> List[DocumentSection]:
    """
    The method takes large text and a list of sentence bounds ([start, end]).
    The method searches for sections and fills 'title' value for each section.
    A section is a dictionary like
    {'start': 460, 'end': 1283, 'title': 'A', 'title_start': 517, 'title_end': 518, 'level': 2, 'abs_level': 1}
    :param full_text:
    :param sentence_list:
    :param use_ml:
    :return:
    """
    sections = list(get_section_spans(
        full_text, use_ml=use_ml, return_text=False, skip_empty_headers=True))
    find_section_titles(sections, sentence_list, full_text)
    return sections


def find_section_titles(sections: List[DocumentSection],
                        sentences: List[Union[Tuple[int, int], Tuple[int, int, str]]],
                        full_text: str) -> None:
    """
    Methods tries to pick section titles as first sentences of
    referenced paragraphs (sections). The method fills section['title'] values.
    :param full_text: text to analyze
    :param sections: # [DocumentSection(start: 460, end: 1283, title: 'A',...), ... ]
    :param sentences: [[start, end], [start, end] ...] - sentence bounds
    """
    if not sections:
        return
    sections.sort(key=lambda s: s.start)
    sentences.sort(key=lambda t: t[0])
    sent_index = 0
    for section in sections:
        possible_title = ''
        title_start = 0
        for i in range(sent_index, len(sentences)):
            sent_index = i
            if section.start > sentences[i][1]:
                continue
            if section.start < sentences[i][0] and \
                    section.end < sentences[i][0]:
                break
            possible_title = full_text[sentences[i][0]: sentences[i][1]]
            title_start = sentences[i][0]
            break
        if not possible_title:
            continue

        title_full = possible_title
        possible_title = possible_title.strip()
        sect_title = section.title.strip()
        # choose title that looks better
        if not HeadingHeuristics.is_new_title_better(sect_title, possible_title):
            continue
        section.title = possible_title
        section.title_start = title_full.index(section.title) + title_start
        section.title_end = section.title_start + len(section.title)
