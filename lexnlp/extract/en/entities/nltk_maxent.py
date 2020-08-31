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
import os
from typing import Generator, Dict, Tuple, Optional, List
import nltk

from lexnlp.extract.common.entities.entity_banlist import BanListUsage, default_banlist_usage, EntityBanListItem
from lexnlp.extract.en.entities.nltk_tokenizer import NltkTokenizer
from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder
from lexnlp.extract.common.annotations.company_annotation import CompanyAnnotation
from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS
from lexnlp.extract.en.entities import nltk_re
from lexnlp.extract.en.utils import strip_unicode_punctuation, NPExtractor
from lexnlp.nlp.en.segments.sentences import get_sentence_list, get_sentence_span_list
from lexnlp.nlp.en.tokens import get_token_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
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
        # noinspection PyTypeChecker
        for ant in nltk_re.get_companies(person):  # type: CompanyAnnotation
            if ant.name == ant.company_type or ant.name == ant.description:
                continue
            return True

    for ant in companies:
        # Solving this scenario: This Amendment to Employment Agreement ("Amendment") is entered into
        # between Marsh Supermarkets, Inc. (the "Company"), and Don E. Marsh (the "Executive").
        # because that is pretty common , even though it screws up this scenario
        # "This is an agreement between John Smith and John Smith, LLC"
        if person in ant.name:
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
        companies = list(get_company_annotations(text))

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

    def __init__(self, grammar=None):
        grammar = grammar or r"""
            NBAR:
                {<DT>?<NNP.*|JJ|POS|\(|\)|,>*<NNP.*>}  # DeTerminer, Proper Noun, Adjective, brackets, terminated by Proper Noun
            IN:
                {<CC|IN>}   # Coordinating Conjunction, Preposition/Subordinating Conjunction
            NP:
                {(<NBAR><IN>)*<NBAR><VBD>*}  # Delaver Housing Incorporated (NNP-NNP-VBD)
        """
        super().__init__(grammar)

    def get_tokenizer(self):
        orig_tokenizer = nltk.tokenize.TreebankWordTokenizer
        punctuation = list(orig_tokenizer.PUNCTUATION)
        punctuation[4] = (re.compile(r'[;@#$%]', re.UNICODE), ' \\g<0> ')
        # for case like "McDonald\'s Incorporated: Burgers" when POS tokenizer treats
        # "Incorporated:" as VBN instead of NNP and NP extractor fails to recognize such grammar
        punctuation.append((re.compile(r':'), r';'))
        # for case when apostrophe is in company name like Moody`s
        starting_quotes = [(re.compile(r'`s '), r'-ES-')] + list(orig_tokenizer.STARTING_QUOTES) + [
            (re.compile(r'-ES-'), r'`s ')]

        tokenizer = NltkTokenizer(punctuation, starting_quotes)
        return tokenizer.tokenize

    @staticmethod
    def strip_np(np):
        return np.strip(string.punctuation + string.whitespace)

    def cleanup_leaves(self, leaves):
        leaves = super().cleanup_leaves(leaves)
        leaves = [i for i in leaves if i[0] != ('a', 'DT') and i[0] != ('A', 'DT') and
                  not (i[0][1] == 'JJ' and i[0][0].islower())]
        return leaves


np_extractor = CompanyNPExtractor()


def get_company_annotations(
    text: str,
    strict: bool = False,
    use_gnp: bool = False,
    count_unique: bool = False,
    name_upper: bool = False,
    banlist_usage: BanListUsage = default_banlist_usage
) -> Generator[CompanyAnnotation, None, None]:
    """
    Find company names in text, optionally using the stricter article/prefix expression.
    :param parse_name_abbr:
    :param text:
    :param strict:
    :param use_gnp: use get_noun_phrases or NPExtractor
    :param name_upper: return company name in upper case.
    :param count_unique: return only unique companies - case insensitive.
    :param banlist_usage: a banlist or hints on using the default BL
    :return:
    """
    # skip if all text is in uppercase
    if text == text.upper():
        return
    banlist = get_company_banlist(banlist_usage)
    valid_punctuation = VALID_PUNCTUATION + ["(", ")"]
    unique_companies: Dict[Tuple[str, str], CompanyAnnotation] = {}

    if not COMPANY_TYPES_RE.search(text):
        return
    # iterate through sentences
    for s_start, s_end, sentence in get_sentence_span_list(text):
        # skip if whole phrase is in uppercase
        if sentence == sentence.upper():
            continue
        if use_gnp:
            phrases = list(get_noun_phrases(sentence, strict=strict, valid_punctuation=valid_punctuation))
        else:
            phrases = list(np_extractor.get_np(sentence))
        phrase_spans = PhrasePositionFinder.find_phrase_in_source_text(sentence, phrases)

        for phrase, p_start, p_end in phrase_spans:
            if COMPANY_TYPES_RE.search(phrase):
                ant: CompanyAnnotation
                for ant in nltk_re.get_companies(phrase, use_sentence_splitter=False):
                    if ant.name == ant.company_type or ant.name == ant.description:
                        continue
                    # check against banlist
                    if banlist:
                        if EntityBanListItem.check_list(ant.name, banlist):
                            continue
                    ant.coords = (ant.coords[0] + s_start + p_start,
                                  ant.coords[1] + s_start + p_start)

                    if name_upper:
                        ant.name = ant.name.upper()

                    if count_unique:
                        unique_key = (ant.name.lower() if ant.name else None, ant.company_type_abbr)
                        existing_result = unique_companies.get(unique_key)

                        if existing_result:
                            existing_result.counter += 1
                        else:
                            unique_companies[unique_key] = ant
                    else:
                        yield ant

    if count_unique:
        for company in unique_companies.values():
            yield company

    # search for acronyms in text ("[A-Z]" or (A-Z))
    # try to merge annotations (in one sentence!) in acronyms


def get_companies(text: str,
                  strict: bool = False,
                  use_gnp: bool = False,
                  detail_type: bool = False,
                  count_unique: bool = False,
                  name_upper: bool = False,
                  parse_name_abbr: bool = False,
                  return_source: bool = False,
                  banlist_usage: BanListUsage = default_banlist_usage):
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
    :param banlist_usage: a banlist or hints on using the default BL
    :return:
    """
    # skip if all text is in uppercase
    # noinspection PyTypeChecker
    for ant in get_company_annotations(text,
                                       strict,
                                       use_gnp,
                                       count_unique,
                                       name_upper,
                                       banlist_usage):  # type:CompanyAnnotation
        result = (ant.name, ant.company_type)
        if detail_type:
            result += (ant.company_type_abbr, ant.company_type_label, ant.description)
        if parse_name_abbr:
            result += (ant.name_abbr,)
        if return_source and not count_unique:
            result = result + (ant.text,)
        if count_unique:
            result = result + (ant.counter,)
        yield result


default_company_banlist = None


def get_company_banlist(banlist_usage: BanListUsage) -> Optional[List[EntityBanListItem]]:
    # pylint: disable=global-statement
    global default_company_banlist

    if banlist_usage.banlist and not banlist_usage.append_to_default:
        return banlist_usage.banlist
    if not banlist_usage.append_to_default and not banlist_usage.use_default_banlist:
        return None
    if default_company_banlist is None:
        path = os.path.join(os.path.dirname(__file__),
                            '../data/en_company_banlist.csv')
        default_company_banlist = EntityBanListItem.read_from_csv(path)

    if banlist_usage.append_to_default and banlist_usage.banlist:
        return default_company_banlist + banlist_usage.banlist

    return default_company_banlist
