"""Entity extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic entity extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.

Todo:
  * Better define interface for sentences vs. raw text
  * Standardize generator vs list
"""
# pylint: disable=W0612

# Imports
import re
import string

from typing import Generator

import nltk

from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS
from lexnlp.extract.en.entities import nltk_re
from lexnlp.extract.en.utils import strip_unicode_punctuation, NPExtractor
from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.nlp.en.tokens import get_token_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

VALID_PUNCTUATION = [",", ".", "&"]

COMPANY_TYPES = sorted(list(COMPANY_TYPES.keys()) + COMPANY_DESCRIPTIONS, key=len)
COMPANY_TYPES_RE = re.compile(r' %s(?:\W|$)' % '|'.join([re.escape(i.strip('.'))
                                                         for i in COMPANY_TYPES]), re.IGNORECASE)

PERSONS_STOP_WORDS = re.compile(
    r'avenue|amendment|agreement|addendum|article|assignment|exhibit', re.IGNORECASE)


def contains_companies(person:str, companies) -> bool:
    if COMPANY_TYPES_RE.search(person):
        for result in nltk_re.get_companies(person,
                                            detail_type=True,
                                            parse_name_abbr=True):
            co_name, co_type, co_type_abbr, co_type_label, co_desc, co_abbr = result

            if co_name == co_type or co_name == co_desc:
                continue
            return True

    for co_name, co_type in companies:
        # Solving this scenario: This Amendment to Employment Agreement ("Amendment") is entered into
        # between Marsh Supermarkets, Inc. (the "Company"), and Don E. Marsh (the "Executive").
        # because that is pretty common , even though it screws up this scenario
        # "This is an agreement between John Smith and John Smith, LLC"
        if person in co_name:
            return True
    return False


def get_persons(text, strict=False, return_source=False, window=2) -> Generator:
    """
    Get names from text.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentence_list(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_token_list(sentence))
        companies = get_companies(text)

        # Iterate through chunks
        persons = []
        last_person_pos = None

        for i, chunk in enumerate(nltk.ne_chunk(sentence_pos)):
            if type(chunk) == nltk.tree.Tree:
                # Check label
                if chunk.label() == 'PERSON':
                    if not strict and last_person_pos is not None and (i - last_person_pos) < window:
                        persons[-1] += " " + " ".join([c[0] for c in chunk])
                    else:
                        persons.append(" ".join([c[0] for c in chunk]))
                    last_person_pos = i
            elif not strict and last_person_pos is not None and (i - last_person_pos) < window:
                if chunk[1] in ["NNP", "NNPS"]:
                    persons[-1] += " " + chunk[0]
                    last_person_pos = i
                elif chunk[1] in ["CC"] or chunk[0] in VALID_PUNCTUATION:
                    if chunk[0].lower() in ["or"]:
                        continue
                    persons[-1] += (" " if chunk[0].lower() in ["&", "and"] else "") + chunk[0]
                    last_person_pos = i
                else:
                    last_person_pos = None

        # Cleanup and yield
        for person in persons:
            # Cleanup
            person = person.strip()
            if len(person) <= 2:
                continue

            if PERSONS_STOP_WORDS.search(person):
                continue

            person = strip_unicode_punctuation(person).strip(string.punctuation).strip(string.whitespace)

            if contains_companies(person, companies):
                continue

            if person.lower().endswith(" and"):
                person = person[0:-4]
            elif person.endswith(" &"):
                person = person[0:-2]


            if return_source:
                yield person, sentence
            else:
                yield person


def get_geopolitical(text, strict=False, return_source=False, window=2) -> Generator:
    """
    Get GPEs from text.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    # Iterate through sentences
    for sentence in get_sentence_list(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_token_list(sentence))

        # Iterate through chunks
        gpes = []
        last_gpe_pos = None
        for i, chunk in enumerate(nltk.ne_chunk(sentence_pos)):
            if type(chunk) == nltk.tree.Tree:
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


def get_noun_phrases(text, strict=False, return_source=False, window=3, valid_punctuation=None) -> Generator:
    """
    Get NNP phrases from text.
    :param window:
    :param return_source:
    :param strict:
    :param text:
    :return:
    """
    valid_punctuation = valid_punctuation or VALID_PUNCTUATION
    # Iterate through sentences
    for sentence in get_sentence_list(text):
        # Tag sentence
        sentence_pos = nltk.pos_tag(get_token_list(sentence))

        # Iterate through chunks
        nnps = []
        last_nnp_pos = None
        for i, chunk in enumerate(sentence_pos):
            do_join = not strict and last_nnp_pos is not None and (i - last_nnp_pos) < window
            # Check label
            if chunk[1] in ["NNP", "NNPS"]:
                if do_join:
                    sep = "" if "(" in valid_punctuation and nnps[-1][-1] == "(" else " "
                    nnps[-1] += sep + chunk[0]
                else:
                    nnps.append(chunk[0])
                last_nnp_pos = i
            elif do_join:
                if chunk[1] in ["CC"] or chunk[0] in valid_punctuation:
                    if chunk[0].lower() in ["or"]:
                        continue
                    nnps[-1] += (" " if chunk[0].lower() in ["&", "and", "("] else "") + chunk[0]
                    last_nnp_pos = i
                else:
                    last_nnp_pos = None

        # Clean up names and yield
        for nnp in nnps:
            # Cleanup
            nnp = nnp.strip()
            if len(nnp) <= 2:
                continue

            if nnp.lower().endswith(" and"):
                nnp = nnp[0:-4].strip()
            elif nnp.endswith(" &"):
                nnp = nnp[0:-2].strip()

            nnp = strip_unicode_punctuation(nnp).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield nnp, sentence
            else:
                yield nnp



class CompanyNPExtractor(NPExtractor):

    @staticmethod
    def strip_np(np):
        return np.strip(string.punctuation + string.whitespace)

    def cleanup_leaves(self, leaves):
        leaves = super().cleanup_leaves(leaves)
        leaves = [i for i in leaves if i[0] != ('a', 'DT') and i[0] != ('A', 'DT') and
                  not (i[0][1] == 'JJ' and i[0][0].islower())]
        return leaves


np_extractor = CompanyNPExtractor()


def get_companies(text: str,
                  strict: bool = False,
                  use_gnp: bool = False,
                  detail_type: bool = False,
                  count_unique: bool = False,
                  name_upper: bool = False,
                  parse_name_abbr: bool = False,
                  return_source: bool = False):
    """
    Find company names in text, optionally using the stricter article/prefix expression.
    :param text:
    :param strict:
    :param use_gnp: use get_noun_phrases or NPExtractor
    :param detail_type: return detailed type (type, unified type, label) vs type only
    :param name_upper: return company name in upper case.
    :param count_unique: return only unique companies - case insensitive.
    :param parse_name_abbr: return company abbreviated name if exists.
    :param return_source:
    :return:
    """
    # skip if all text is in uppercase
    if text == text.upper():
        return
    valid_punctuation = VALID_PUNCTUATION + ["(", ")"]

    unique_companies = dict()

    if COMPANY_TYPES_RE.search(text):
        # Iterate through sentences
        for sentence in get_sentence_list(text):
            # skip if whole phrase is in uppercase
            if sentence == sentence.upper():
                continue
            if use_gnp:
                phrases = get_noun_phrases(sentence, strict=strict,
                                           valid_punctuation=valid_punctuation)
            else:
                phrases = np_extractor.get_np(sentence)
            for phrase in phrases:
                if COMPANY_TYPES_RE.search(phrase):
                    for result in nltk_re.get_companies(phrase,
                                                        detail_type=True,
                                                        parse_name_abbr=True):
                        co_name, co_type, co_type_abbr, co_type_label, co_desc, co_abbr = result

                        if co_name == co_type or co_name == co_desc:
                            continue
                        if name_upper:
                            co_name = co_name.upper()

                        result = (co_name, co_type)

                        if detail_type:
                            result += (co_type_abbr, co_type_label, co_desc)
                        if parse_name_abbr:
                            result += (co_abbr,)
                        if return_source and not count_unique:
                            result = result + (sentence,)

                        if count_unique:
                            unique_key = (result[0].lower() if result[0] else None, co_type_abbr)
                            existing_result = unique_companies.get(unique_key)

                            if existing_result:
                                unique_companies[unique_key] = existing_result[:-1] + (existing_result[-1] + 1,)
                            else:
                                unique_companies[unique_key] = result + (1,)
                        else:
                            yield result

        if count_unique:
            for company in unique_companies.values():
                yield company