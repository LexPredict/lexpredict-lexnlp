# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Dict, List, Generator, Tuple, Optional
import os
import copy
import regex as re
import nltk
import string

from lexnlp.config.en.company_types import CompanyDescriptor
from lexnlp.extract.common.annotations.company_annotation import CompanyAnnotation
from lexnlp.extract.en.entities.company_np_extractor import CompanyNPExtractor
from lexnlp.extract.en.utils import strip_unicode_punctuation, replace_upper_words_with_titled
from lexnlp.extract.en.entities import nltk_re
from lexnlp.extract.common.entities.entity_banlist import BanListUsage, default_banlist_usage, EntityBanListItem
from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list, get_sentence_list
from lexnlp.nlp.en.tokens import get_token_list
from lexnlp.utils.pos_adjustments import TokenPosTagAdjustment


VALID_PUNCTUATION = [",", ".", "&"]

PERSONS_STOP_WORDS = re.compile(
    r'avenue|amendment|agreement|addendum|article|assignment|exhibit', re.IGNORECASE)

MONTH_NAMES = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
               'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
MONTH_NAMES_STR = '|'.join([fr'\-{m}\-' for m in MONTH_NAMES])
PARTY_PREFIX_STR = fr'^\d\d([0-9\.\s\,]*({MONTH_NAMES_STR}|\-)*[0-9\.\s\,]*)+'
COMPANY_NAME_PREFIX_RE = re.compile(PARTY_PREFIX_STR, re.IGNORECASE)
COMPANY_NAME_TRIM_RE = re.compile(r'^\s*(?:and|&|of)\s+|\s+(?:and|&|of)\s*$', re.IGNORECASE)


class CompanyDetector:
    BACKTRACK_CATASTROPHY_COMPANY_PATTERN = r'[0-9A-Za-z]{80,}'

    BACKTRACK_CATASTROPHY_COMPANY_RE = re.compile(BACKTRACK_CATASTROPHY_COMPANY_PATTERN)

    def __init__(
        self,
        company_types: Dict[str, CompanyDescriptor],
        company_descriptions: List[str]
    ) -> None:
        """
        """
        self.company_types = {}
        self.np_extractor = CompanyNPExtractor()
        self.init_company_types(company_types)
        self.np_extractor.token_pos_tag_adjustments = \
            self.create_token_pos_tag_adjustments()
        self.company_descriptions = company_descriptions
        self.default_company_banlist: Optional[List[EntityBanListItem]] = None
        self.default_company_banlist = None
        self.company_name_pattern = None
        self.company_pattern = None
        self.company_article_pattern = None
        self.re_company = None
        self.re_article_company = None
        self.default_company_desc_re = None
        self.company_types_re = self.compile_company_type_reg(list(company_types.keys()))
        self.compile_company_pattern()

    def init_company_types(self, company_types: Dict[str, CompanyDescriptor]):
        self.company_types = {}
        alias_transformers = [
            lambda a: a.strip(' ').lower(),
            lambda a: a.strip(' ').strip('.').lower()
        ]
        for trans in alias_transformers:
            for _alias, cmp in company_types.items():
                lc_alias = trans(cmp.alias)
                if lc_alias not in self.company_types:
                    self.company_types[lc_alias] = CompanyDescriptor(
                        lc_alias, cmp.abbreviation, cmp.label)

    def create_token_pos_tag_adjustments(self) -> List[TokenPosTagAdjustment]:
        """
        Some company abbreviations are not recognized as NNP parts of speech by
        NLTK in `get_np()`. This function inserts adjustments based on
        the detector's company_types.
        """
        def _create_adjustment(key) -> TokenPosTagAdjustment:
            return TokenPosTagAdjustment(
                from_token=lambda token: token == key,
                from_pos=lambda pos: pos == 'NN',
                to_pos=lambda pos: 'NNP'
            )
        token_pos_tag_adjustments: List[TokenPosTagAdjustment] = [
            _create_adjustment(key)
            for key in [
                *self.company_types,
                *(f'{k}.' for k in self.company_types if not k.endswith('.'))
            ]
        ]
        return token_pos_tag_adjustments

    @classmethod
    def compile_company_type_reg(cls, company_types: List[str]):
        company_types = sorted(company_types + nltk_re.COMPANY_DESCRIPTIONS, key=len)
        company_types_re = re.compile(r' %s(?:\W|$)' % '|'.join(
            [re.escape(i.strip('.')) for i in company_types]), re.IGNORECASE)
        return company_types_re

    def compile_company_pattern(self):
        self.company_name_pattern = r'''
            (?:
                (?:(?-i:[A-Z0-9][A-Z0-9a-z\'\`\-&]+)
                   |of
                   |(?<!(?:{company_type_pattern}|{company_description_pattern})\s+)and(?=\s+(?-i:[A-Z0-9][A-Z0-9a-z\'\`\-&]+))
                )[,\.& ]*
            ){{1,5}}
            (?:\([a-z0-9][a-z0-9 \,\.\-\&]+?\))?
        '''.format(
            company_type_pattern=nltk_re.get_company_type_pipe(self.company_types),
            company_description_pattern=nltk_re.get_company_description_pipe(self.company_descriptions))

        # Create patterns from parameters
        self.company_pattern = self.create_company_pattern()
        self.company_article_pattern = self.create_company_pattern(article_pattern=nltk_re.ARTICLE_PATTERN)
        self.re_company = re.compile(
            self.company_pattern, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)
        self.re_article_company = re.compile(
            self.company_article_pattern, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)
        self.default_company_desc_re = re.compile(
            r'(?:^|\W)(?:{})(?:$|\W)'.format('|'.join(self.company_descriptions)), re.I)

    def create_company_pattern(self, article_pattern: str = ''):
        """
        Create a company pattern for regular expression.
        """
        company_type_pattern = nltk_re.get_company_type_pipe(self.company_types)
        company_description_pattern = nltk_re.get_company_description_pipe(self.company_descriptions)
        return nltk_re.COMPANY_PATTERN_TEMPLATE \
            .format(company_name_pattern=self.company_name_pattern,
                    article_pattern=article_pattern,
                    company_type_pattern=company_type_pattern,
                    company_description_pattern=company_description_pattern)

    def get_company_annotations(
        self,
        text: str,
        strict: bool = False,
        use_gnp: bool = False,
        count_unique: bool = False,
        name_upper: bool = False,
        banlist_usage: Optional[BanListUsage] = None
    ) -> Generator[CompanyAnnotation, None, None]:
        """
        Find company names in text, optionally using the stricter article/prefix expression.
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
        # replace new lines with spaces
        text = text.replace('\n', ' ')
        banlist = self.get_company_banlist(banlist_usage)
        valid_punctuation = VALID_PUNCTUATION + ["(", ")"]
        unique_companies: Dict[Tuple[str, str], CompanyAnnotation] = {}

        if not self.company_types_re.search(text):
            return
        # iterate through sentences
        for s_start, _s_end, sentence in get_sentence_span_list(text):
            # skip if whole phrase is in uppercase
            if sentence == sentence.upper():
                continue
            if use_gnp:
                phrases = list(get_noun_phrases(sentence, strict=strict, valid_punctuation=valid_punctuation))
            else:
                phrases = list(self.np_extractor.get_np(sentence))
            phrase_spans = PhrasePositionFinder.find_phrase_in_source_text(sentence, phrases)

            for phrase, p_start, _p_end in phrase_spans:
                if self.company_types_re.search(phrase):
                    ant: CompanyAnnotation
                    for ant in self.get_companies_re(phrase, use_sentence_splitter=False):
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

    def get_companies(self,
                      text: str,
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
        for ant in self.get_company_annotations(
                text,
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

    def get_company_banlist(self, banlist_usage: Optional[BanListUsage]) -> Optional[List[EntityBanListItem]]:
        banlist_usage = banlist_usage or default_banlist_usage
        if banlist_usage.banlist and not banlist_usage.append_to_default:
            return banlist_usage.banlist
        if not banlist_usage.append_to_default and not banlist_usage.use_default_banlist:
            return None
        if self.default_company_banlist is None:
            path = os.path.join(os.path.dirname(__file__),
                                '../data/en_company_banlist.csv')
            self.default_company_banlist = EntityBanListItem.read_from_csv(path)

        if banlist_usage.append_to_default and banlist_usage.banlist:
            return self.default_company_banlist + banlist_usage.banlist

        return self.default_company_banlist

    def get_persons(self, text: str, strict=False, return_source=False, window=2) -> Generator:
        """
        Get names from text.
        """
        companies = list(self.get_company_annotations(text))
        # Iterate through sentences
        for sentence in get_sentence_list(text):
            # Tag sentence
            original_sentence = copy.copy(sentence)
            sentence = replace_upper_words_with_titled(sentence)
            sentence_pos = nltk.pos_tag(get_token_list(sentence))

            # Iterate through chunks
            persons = []
            last_person_pos = None

            for i, chunk in enumerate(nltk.ne_chunk(sentence_pos)):
                if isinstance(chunk, nltk.tree.Tree):
                    # Check label
                    if chunk.label() == 'PERSON':
                        if not strict and last_person_pos is not None and (i - last_person_pos) < window:
                            persons[-1] += " " + " ".join([c[0] for c in chunk])
                        else:
                            persons.append(" ".join([c[0] for c in chunk]))
                        last_person_pos = i
                elif not strict and last_person_pos is not None and (i - last_person_pos) < window:
                    if chunk[1] in ['NNP', 'NNPS']:
                        persons[-1] += " " + chunk[0]
                        last_person_pos = i
                    elif chunk[1] in ["CC"] or chunk[0] in VALID_PUNCTUATION:
                        if chunk[0].lower() in ["or"]:
                            continue
                        persons[-1] += (" " if chunk[0].lower() in ["&", "and"] else "") + chunk[0]
                        last_person_pos = i
                    else:
                        last_person_pos = None

            # convert persons to persons from original sentence and remove UPPER persons as 1 word
            persons = [person.upper() 
                       if person.upper() in original_sentence \
                          and person.upper() not in persons
                       else person 
                       for person in persons 
                       if not (person.upper() in original_sentence and len(re.findall(r'\w+', person)) < 2)]
            
            # Cleanup and yield
            for person in persons:
                # Cleanup
                person = person.strip()
                if len(person) <= 2:
                    continue

                if PERSONS_STOP_WORDS.search(person):
                    continue

                person = strip_unicode_punctuation(person).strip(string.punctuation).strip(string.whitespace)

                if self.contains_companies(person, companies):
                    continue

                if person.lower().endswith(" and"):
                    person = person[0:-4]
                elif person.endswith(" &"):
                    person = person[0:-2]

                if return_source:
                    yield person, sentence
                else:
                    yield person

    def get_companies_re(self,
                         text: str,
                         use_article: bool = False,
                         use_sentence_splitter: bool = True) -> Generator[CompanyAnnotation, None, None]:
        """
        Find company names in text, optionally using the stricter article/prefix expression.
        """
        # Select regex
        re_c = self.re_article_company if use_article else self.re_company

        # Iterate through sentences
        sent_list = get_sentence_span_list(text) if use_sentence_splitter else [(0, len(text), text)]
        for start, _, sentence in sent_list:
            if self.check_backtrack_catastrophy(sentence):
                continue

            for match in re_c.finditer(sentence):
                captures = match.capturesdict()
                company_type = captures['company_type_of'] or \
                    captures['company_type'] or \
                    captures['company_type_single']
                company_type = "".join(company_type).strip(
                    string.punctuation.replace(".", "") + string.whitespace)
                company_type = company_type or None

                company_name = "".join(captures['full_name'])
                if company_type:
                    company_name = re.sub(r'%s$' % company_type, '', company_name)
                company_name = nltk_re.FALSE_POS_SUB_RE.sub('', company_name)
                company_name = company_name.strip(
                    string.punctuation.replace('&', '').replace(')', '') + string.whitespace)
                company_name = COMPANY_NAME_TRIM_RE.sub('', company_name)
                # remove company name "prefix": numbers, dates etc
                company_name = COMPANY_NAME_PREFIX_RE.sub('', company_name)
                if not company_name:
                    continue

                # catch a Delaware company
                if company_name.lower().startswith('a ') or captures.get('article') == ['a']:
                    continue

                company_description = captures.get('company_description', '')
                if not company_description:
                    company_description_match = self.default_company_desc_re.findall(company_name)
                    if company_description_match:
                        company_description = company_description_match[0]

                company_description = "".join(company_description).strip(
                    string.punctuation + string.whitespace)

                # catch ABC & Company LLC case
                if company_description.lower() == 'company' and \
                        ('& company' in company_name.lower() or 'and company' in company_name.lower()):
                    company_description = None
                company_description = company_description or None

                # catch "The Company"
                if company_description:
                    _company_name = re.sub(r'[\s,]%s$' % company_description, '', company_name)
                    if not _company_name or \
                            nltk_re.ARTICLE_RE.fullmatch(_company_name) or \
                            re.match(r'.+?\s(?:of|in)$', _company_name.lower()):
                        continue
                if company_name in self.company_descriptions:
                    continue

                abbr_name = "".join(captures["abbr_name"]) or None

                ret = CompanyAnnotation(
                    (match.start() + start, match.end() + start),
                    name=company_name, company_type_full=company_type)
                ret.company_type_abbr = self.company_types[company_type.lower()].abbreviation if company_type else None
                ret.company_type_label = self.company_types[company_type.lower()].label if company_type else None
                ret.description = company_description
                ret.name_abbr = abbr_name
                ret.text = sentence
                # no args:         = [company_name, company_type, company_description]
                # detail_type:     + [company_type_abbr, company_type_label]
                # parse_name_abbr: + [abbr_name]
                # return_source:   + [source]
                yield ret

    def contains_companies(self, person: str, companies) -> bool:
        if self.company_types_re.search(person):
            # noinspection PyTypeChecker
            for ant in self.get_companies_re(person):  # type: CompanyAnnotation
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

    @classmethod
    def check_backtrack_catastrophy(cls, text: str) -> bool:
        return cls.BACKTRACK_CATASTROPHY_COMPANY_RE.search(text)


def get_noun_phrases(text, strict=False, return_source=False, window=3, valid_punctuation=None) -> Generator:
    """
    Get NNP phrases from text
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
            if chunk[1] in ['NNP', 'NNPS']:
                if do_join:
                    sep = "" if "(" in valid_punctuation and nnps[-1][-1] == "(" else " "
                    nnps[-1] += sep + chunk[0]
                else:
                    nnps.append(chunk[0])
                last_nnp_pos = i
            elif do_join:
                if chunk[1] in ['CC'] or chunk[0] in valid_punctuation:
                    if chunk[0].lower() in ["or"]:
                        continue
                    nnps[-1] += (' ' if chunk[0].lower() in ['&', 'and', '('] else '') + chunk[0]
                    last_nnp_pos = i
                else:
                    last_nnp_pos = None

        # Clean up names and yield
        for nnp in nnps:
            # Cleanup
            nnp = nnp.strip()
            if len(nnp) <= 2:
                continue

            if nnp.lower().endswith(' and'):
                nnp = nnp[0:-4].strip()
            elif nnp.endswith(' &'):
                nnp = nnp[0:-2].strip()

            nnp = strip_unicode_punctuation(nnp).strip(string.punctuation).strip(string.whitespace)
            if return_source:
                yield nnp, sentence
            else:
                yield nnp
