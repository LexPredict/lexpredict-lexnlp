__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import List, Tuple, Generator

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common import year_parser
from lexnlp.extract.common.annotations.court_citation_annotation import CourtCitationAnnotation
from lexnlp.extract.de.dates import get_dates
from lexnlp.utils.lines_processing.phrase_finder import PhraseFinder


class PossibleToken:
    def __init__(self, token_type: str, value: str, coords: Tuple[int, int], prob: int):
        self.token_type = token_type
        self.value = value
        self.coords = coords
        self.prob = prob

    def __repr__(self):
        return '%s [%s] at (%d, %d), prob: %d' % \
               (self.value, self.token_type, self.coords[0], self.coords[1], self.prob)


class CourtCitationsParser:
    """
    https://docs.google.com/spreadsheets/d/1_-Hnr46s8JmTYIFSkcI01gbwqwjnVDoAV1dUv3Bz5fM/edit#gid=0

    could be one of the following:

    (lalala; DATE; vom) or (lalala; DATE; Beschluss)

    or § lalala Court Name (abbreviation)

    or
    """
    reg_cite_chunk = re.compile(r"\([^0-9\)]+[0-9\.]{2,}[^\)]+\)", re.UNICODE)
    reg_trigger_words = re.compile('Beschluss|vom', re.UNICODE | re.IGNORECASE)
    reg_token_end = re.compile(r"[;,]")

    registries = {
        'BStBl': 'Bundessteuerblatt (sonstige gebräuchliche Verwendung)',
        'BFH': 'Deutschland, Rechtswesen: Bundesfinanzhof',
        'BFHE': 'Sammlung der Entscheidungen des BFH',
        'GmS-OGB': 'Beschluss des Gemeinsamen Senats der obersten Gerichtshöfe des Bundes',
        'BVerwGE': 'Entscheidungen des Bundesverwaltungsgerichts',
        'GrS': 'Beschluss des Großen Senats des BFH',
        'BFH-Urteile': 'Bundesfinanzhof Urteile',
        'BFH-Beschlüsse': 'Bundesfinanzhof Beschlüsse',
        'DstR': 'Deutsches Steuerrecht - DStR',
        'KStG': 'Körperschaftsteuergesetz'
    }

    registry_finder = None
    reg_split_by_registry = None

    # region STATICINIT
    if not registry_finder:
        registry_finder = PhraseFinder(list(registries.keys()))
    if not reg_split_by_registry:
        reg_split_by_registry = re.compile("|".join(list(registries.keys())))
    # endregion

    def __init__(self):
        self.items: List[CourtCitationAnnotation] = []
        self.language: str = 'de'

    def parse(self, text: str, language: str = 'de') -> List[CourtCitationAnnotation]:
        # TODO: can we turn this into a generator?
        self.language: str = language
        self.items: List[CourtCitationAnnotation] = []
        self.find_citations_in_embraced_text(text)
        return self.items

    def find_citations_in_embraced_text(self, text: str) -> None:
        fragment_start = 0
        for embraced_text in CourtCitationsParser.reg_cite_chunk.finditer(text):
            start = embraced_text.start()

            # process text before braces
            fragment = text[fragment_start:start]
            self.split_chunk_and_find_citations(fragment, fragment_start)
            fragment_start = embraced_text.end() + 1

            # process text in braces
            self.process_chunks_in_embraced_text(embraced_text, start)

        fragment = text[fragment_start:-1]
        self.split_chunk_and_find_citations(fragment, fragment_start)

    def process_chunks_in_embraced_text(self, embraced_text: str, start) -> None:
        parts = embraced_text.group().split(';')
        for part in parts:
            self.get_detail_from_chunk(part, start)
            start += len(part) + 1

    def split_chunk_and_find_citations(self, text: str, start: int) -> None:
        chunks = self.split_text_by_keywords(text)
        for chunk in chunks:
            self.get_detail_from_chunk(chunk[0], chunk[1] + start)

    def get_detail_from_chunk(self, chunk_text: str, chunk_start: int) -> None:
        chunk_body = chunk_text.strip(r'() \t')
        dates = self.get_dates_from_text(chunk_body)
        registries = self.get_registries_from_text(chunk_body)
        triggers = CourtCitationsParser.reg_trigger_words.search(chunk_body)

        if not triggers and len(registries) == 0 and len(dates) == 0:
            return

        start = chunk_start + chunk_text.find(chunk_body)
        end = start + len(chunk_body)
        ant = CourtCitationAnnotation(name=chunk_body,
                                      coords=(start, end),
                                      text=chunk_body,
                                      locale=self.language)
        if len(registries) > 0:
            ant.name = CourtCitationsParser.registries[registries[0].value]
            ant.short_name = self.get_reference_from_registry(registries[0], chunk_body)
        self.items.append(ant)

    def get_reference_from_registry(self, registry: PossibleToken,
                                    chunk_body: str) -> str:
        start = registry.coords[0]
        end = -1
        end_match = CourtCitationsParser.reg_token_end.search(chunk_body[start:])
        if end_match:
            end = end_match.start()
        return chunk_body[start: end + 1].strip(' \t.,;()')

    def get_registries_from_text(self, text: str) -> List[PossibleToken]:
        reg_names = [(m, 100) for m in CourtCitationsParser.registry_finder.find_word(text, ignore_case=False)]
        # if the case is not the same, the probability is 50%
        reg_names += [(m, 50) for m in CourtCitationsParser.registry_finder.find_word(text, ignore_case=True)]
        reg_names.sort(key=lambda n: n[0][1] - n[1] * 1000)

        toks = []
        for match_prob in reg_names:
            tok = PossibleToken('registry', match_prob[0][0],
                                (match_prob[0][1], match_prob[0][2]),
                                match_prob[1])
            toks.append(tok)
        return toks

    def get_dates_from_text(self, text: str) -> List[PossibleToken]:
        try:
            date_ents = list(get_dates(text))
        except TypeError:
            date_ents = []
        date_ents.sort(key=lambda d: d['location_start'])

        tokens = []
        for d in date_ents:
            tok = PossibleToken('date', d['value'], (d['location_start'], d['location_end']), 100)
            tokens.append(tok)
        if len(tokens) > 0:
            return tokens

        # try only getting years
        for year in year_parser.year_parser.get_years_with_coords_from_string(text):
            tokens.append(PossibleToken('date', str(year[0]), (year[1], year[2]), 50))
        return tokens

    @staticmethod
    def split_text_by_keywords(text: str) -> List[Tuple[str, int]]:
        # noinspection PyTypeChecker
        matches: Tuple[re.Match] = tuple(CourtCitationsParser.reg_split_by_registry.finditer(text))
        chunks = []
        for i, match in enumerate(matches):
            ending = -1
            if i < len(matches) - 1:
                ending = matches[i + 1].start() - 1
            phrase_break = CourtCitationsParser.reg_token_end.search(text[match.end():ending])
            if phrase_break:
                ending = min(ending, phrase_break.start())
            chunks.append((text[match.start():ending], match.start()))
        return chunks


parser = CourtCitationsParser()


def get_court_citation_annotations(
    text: str,
    language: str = 'de',
) -> Generator[CourtCitationAnnotation, None, None]:
    yield from parser.parse(text, language)


def get_court_citation_annotation_list(
    text: str,
    language: str = 'de',
) -> List[CourtCitationAnnotation]:
    return parser.parse(text, language)


def get_court_citations(text: str, language: str = 'de') -> Generator[dict, None, None]:
    cts = parser.parse(text, language)
    for ct in cts:
        yield ct.to_dictionary()


def get_court_citation_list(text: str, language: str = 'de') -> List[CourtCitationAnnotation]:
    return parser.parse(text, language)
