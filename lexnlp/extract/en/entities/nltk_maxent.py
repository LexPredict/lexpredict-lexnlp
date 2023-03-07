"""Entity extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic entity extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.

Todo:
  * Better define interface for sentences vs. raw text
  * Standardize generator vs list
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=W0612

import string
from typing import Generator, Optional, Tuple
import nltk

from lexnlp.extract.en.entities.nltk_re import RE_PARTY_AS
from lexnlp.extract.common.annotations.company_annotation import CompanyAnnotation
from lexnlp.extract.common.entities.entity_banlist import BanListUsage
from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS
from lexnlp.extract.en.utils import strip_unicode_punctuation
from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.nlp.en.tokens import get_token_list
from lexnlp.extract.en.entities.company_detector import CompanyDetector, VALID_PUNCTUATION


default_company_detector = CompanyDetector(COMPANY_TYPES, COMPANY_DESCRIPTIONS)


def get_company_annotations(
        text: str,
        strict: bool = False,
        use_gnp: bool = False,
        count_unique: bool = False,
        name_upper: bool = False,
        banlist_usage: Optional[BanListUsage] = None) -> Generator[CompanyAnnotation, None, None]:
    yield from default_company_detector.get_company_annotations(
        text, strict, use_gnp, count_unique, name_upper, banlist_usage)


def get_geopolitical(text, strict=False, return_source=False, window=2) -> Generator:
    """
    Get GPEs from text
    """
    # Iterate through sentences
    for sentence in get_sentence_list(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_token_list(sentence))

        # Iterate through chunks
        gpes = []
        last_gpe_pos = None
        for i, chunk in enumerate(nltk.ne_chunk(sentence_pos)):
            if isinstance(chunk, nltk.tree.Tree):
                # Check label
                if chunk.label() == 'GPE':
                    if not strict and last_gpe_pos is not None and (i - last_gpe_pos) < window:
                        gpes[-1] += " " + " ".join([c[0] for c in chunk])
                    else:
                        gpes.append(" ".join([c[0] for c in chunk]))
                    last_gpe_pos = i
            elif not strict and last_gpe_pos is not None and (i - last_gpe_pos) < window:
                if chunk[1] in ["NNP", "NNPS"]:
                    gpes[-1] += " " + chunk[0]
                    last_gpe_pos = i
                elif chunk[1] in ["CC"] or chunk[0] in VALID_PUNCTUATION:
                    if chunk[0].lower() in ["or"]:
                        continue
                    gpes[-1] += (" " if chunk[0].lower() in ["&", "and"] else "") + chunk[0]
                    last_gpe_pos = i
                else:
                    last_gpe_pos = None

        # Clean up names and yield
        for gpe in gpes:
            # Cleanup
            gpe = gpe.strip()
            if len(gpe) <= 2:
                continue

            if gpe.lower().endswith(" and"):
                gpe = gpe[0:-4]
            elif gpe.endswith(" &"):
                gpe = gpe[0:-2]

            gpe = strip_unicode_punctuation(gpe).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield gpe, sentence
            else:
                yield gpe


def get_companies(text: str,
                  strict: bool = False,
                  use_gnp: bool = False,
                  detail_type: bool = False,
                  count_unique: bool = False,
                  name_upper: bool = False,
                  parse_name_abbr: bool = False,
                  return_source: bool = False,
                  banlist_usage: Optional[BanListUsage] = None):
    return default_company_detector.get_companies(
        text, strict, use_gnp, detail_type, count_unique, name_upper,
        parse_name_abbr, return_source, banlist_usage)


def get_persons(text: str, strict=False, return_source=False, window=2) -> Generator:
    return default_company_detector.get_persons(text, strict, return_source, window)


# pylint: disable=unused-argument
def get_parties_as(text: str, detail_type=False) -> \
        Generator[Tuple[str, str, str, str], None, None]:
    """
    :param text: source text to search for companies
    :param detail_type: obsolete
    :return: parties: [(name, company type, company description, party type), ...]
    """
    # Iterate through matches
    for match in RE_PARTY_AS.finditer(text):
        # Setup fields
        captures = match.capturesdict()
        party_string = "".join(captures["party_string"])
        party_type = "".join(captures["party_type"])

        # Skip dates
        if party_type.lower().startswith("of "):
            continue

        # noinspection PyTypeChecker
        for ant in get_companies(party_string):  # type: CompanyAnnotation
            yield ant.name, ant.company_type, ant.description, party_type
