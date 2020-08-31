"""Entity extraction for English using NLTK and basic regular expressions with
main data.

This module implements basic entity extraction functionality in English, but does NOT
rely on the pre-trained NLTK maximum entropy classifier.  Instead, it uses the NLTK English
grammar in combination with regular expressions and tested main data re: company types and
abbreviations (e.g., LLC).

Todo:
  * Better define interface for sentences vs. raw text
  * Standardize generator vs list
"""

# Imports
import string

from typing import Generator, Tuple

import regex as re

from lexnlp.extract.common.annotations.company_annotation import CompanyAnnotation
from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_company_type_pipe(company_type_list=None):
    company_type_list = company_type_list or COMPANY_TYPES
    if isinstance(company_type_list, dict):
        company_type_list = list(company_type_list.keys())

    # Setup company type list
    company_type_list.sort(key=len, reverse=True)
    company_type_pipe = "|".join([re.escape(c.lower())
                                  for c in company_type_list])
    return company_type_pipe


def get_company_description_pipe(company_description_list=None):
    company_description_list = company_description_list or COMPANY_DESCRIPTIONS
    company_description_list.sort(key=len, reverse=True)
    company_description_pipe = "|".join([re.escape(c.strip(".").lower())
                                         for c in company_description_list])
    return company_description_pipe


# Commonly re-used regular expression components
ARTICLES = r'by\ and\ between|by\ and\ among|among|between|with|the|and|to|by|an|a|all'
ARTICLE_RE = re.compile(ARTICLES,
                        re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)
ARTICLE_PATTERN = r'''
(?:
    (?:\W|^)
    (?P<article>{})
    \s+
)?
'''.format(ARTICLES)

# COMPANY_NAME_PATTERN = r'(?-i:[A-Z0-9])[a-z0-9 \'\,\.\-&]+?(?:\([a-z0-9][a-z0-9 \,\.\-\&]+?\))?'

# !!! Assume that company TYPE or DESCRIPTION shouldn't precede " and"
COMPANY_NAME_PATTERN = r'''
    (?:
        (?:(?-i:[A-Z0-9][A-Z0-9a-z\'\`\-&]+)
           |of
           |(?<!(?:{company_type_pattern}|{company_description_pattern})\s+)and(?=\s+(?-i:[A-Z0-9][A-Z0-9a-z\'\`\-&]+))
        )[,\.& ]*
    ){{1,5}}
    (?:\([a-z0-9][a-z0-9 \,\.\-\&]+?\))?
'''.format(
    company_type_pattern=get_company_type_pipe(),
    company_description_pattern=get_company_description_pipe())

# Setup template expression for name matches alone
COMPANY_PATTERN_TEMPLATE = r'''
{article_pattern}
(?P<full_name>
    (?P<company_name>{company_name_pattern})[\s\,]+
    (?:
        (?P<company_description_and>{company_description_pattern})\s+and
    )
    |
    (?P<company_name>
        (?:{company_name_pattern})?
        (?P<company_description_of>{company_description_pattern})\s+of\s+{company_name_pattern})
        (?:\W+|$)(?P<company_type_of>{company_type_pattern})?
    |
    (?P<company_name>{company_name_pattern})[\s\,]+
    (?:
        (?P<company_description>{company_description_pattern})(?:\s\w+)*[\s\,]+(?P<company_type>{company_type_pattern})
        |
        (?P<company_description_single>{company_description_pattern})(?!\s+\p{{Lu}})(?!\s+&\s+)
        |
        (?P<company_type_single>{company_type_pattern})
    )
)
(?:\s*\((?P<abbr_name>[A-Z1-9\&]+)(?:\)|$))?
(?:\,|\.|\;|\s|$)
'''


def create_company_pattern(company_pattern_template=None,
                           company_name_pattern=None,
                           company_type_list=None,
                           company_description_list=None,
                           article_pattern=''):
    """
    Create a company pattern for regular expression.
    :param company_pattern_template:
    :param company_name_pattern:
    :param article_pattern:
    :param company_type_list:
    :param company_description_list:
    :return:
    """
    company_pattern_template = company_pattern_template or COMPANY_PATTERN_TEMPLATE
    company_name_pattern = company_name_pattern or COMPANY_NAME_PATTERN
    company_type_pattern = get_company_type_pipe(company_type_list)
    company_description_pattern = get_company_description_pipe(company_description_list)
    return company_pattern_template \
        .format(company_name_pattern=company_name_pattern,
                article_pattern=article_pattern,
                company_type_pattern=company_type_pattern,
                company_description_pattern=company_description_pattern)


# Create patterns from parameters
COMPANY_PATTERN = create_company_pattern()
COMPANY_ARTICLE_PATTERN = create_company_pattern(article_pattern=ARTICLE_PATTERN)

# Compile regular expression objects
RE_COMPANY = re.compile(
    COMPANY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)
RE_ARTICLE_COMPANY = re.compile(
    COMPANY_ARTICLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

# Create party...as pattern
PARTY_AS_PATTERN = r'''
    (?P<party_string>.+?)[\s\,]
    (as\ the\s|as\s|\"|“)
    (?P<party_type>.+?)(?=\,|\;|\.|\"|”|\n|$)
'''
RE_PARTY_AS = re.compile(PARTY_AS_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.VERBOSE)

FALSE_POS_SUB_PTN = r'''
(?:
    (?:the\s+)?Borrower
    |
    \p{L}+\s+Agent
)
'''
FALSE_POS_SUB_RE = re.compile(FALSE_POS_SUB_PTN, re.IGNORECASE | re.UNICODE | re.VERBOSE)

DEFAULT_COMPANY_DESC_RE = re.compile(
    r'(?:^|\W)(?:{})(?:$|\W)'.format('|'.join(COMPANY_DESCRIPTIONS)), re.I)

BACKTRACK_CATASTROPHY_COMPANY_PATTERN = r'[0-9A-Za-z]{80,}'

BACKTRACK_CATASTROPHY_COMPANY_RE = re.compile(BACKTRACK_CATASTROPHY_COMPANY_PATTERN)


def get_companies(text: str,
                  use_article: bool = False,
                  use_sentence_splitter: bool = True) -> Generator[CompanyAnnotation, None, None]:
    """
    Find company names in text, optionally using the stricter article/prefix expression.
    """
    # Select regex
    re_c = RE_ARTICLE_COMPANY if use_article else RE_COMPANY

    # Iterate through sentences
    sent_list = get_sentence_span_list(text) if use_sentence_splitter else [(0, len(text), text)]
    for start, _, sentence in sent_list:
        if check_backtrack_catastrophy(sentence):
            continue

        for match in re_c.finditer(sentence):
            captures = match.capturesdict()
            company_type = captures["company_type_of"] or \
                           captures["company_type"] or \
                           captures["company_type_single"]
            company_type = "".join(company_type).strip(
                string.punctuation.replace(".", "") + string.whitespace)
            company_type = company_type or None

            company_name = "".join(captures["full_name"])
            if company_type:
                company_name = re.sub(r'%s$' % company_type, '', company_name)
            company_name = FALSE_POS_SUB_RE.sub('', company_name)
            company_name = company_name.strip(
                string.punctuation.replace('&', '').replace(')', '') + string.whitespace)
            company_name = re.sub(r'^\s*(?:and|&|of)\s+|\s+(?:and|&|of)\s*$', '',
                                  company_name, re.IGNORECASE)
            if not company_name:
                continue

            # catch a Delaware company
            if company_name.lower().startswith('a ') or captures.get('article') == ['a']:
                continue

            company_description = captures.get("company_description", '')
            if not company_description:
                company_description_match = DEFAULT_COMPANY_DESC_RE.findall(company_name)
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
                        ARTICLE_RE.fullmatch(_company_name) or \
                        re.match(r'.+?\s(?:of|in)$', _company_name.lower()):
                    continue
            if company_name in COMPANY_DESCRIPTIONS:
                continue

            abbr_name = "".join(captures["abbr_name"]) or None

            ret = CompanyAnnotation(
                (match.start() + start, match.end() + start),
                name=company_name, company_type_full=company_type)
            ret.company_type_abbr = COMPANY_TYPES[company_type.lower()]['abbr'] if company_type else None
            ret.company_type_label = COMPANY_TYPES[company_type.lower()]['label'] if company_type else None
            ret.description = company_description
            ret.name_abbr = abbr_name
            ret.text = sentence
            # no args:         = [company_name, company_type, company_description]
            # detail_type:     + [company_type_abbr, company_type_label]
            # parse_name_abbr: + [abbr_name]
            # return_source:   + [source]
            yield ret


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


def check_backtrack_catastrophy(text: str) -> bool:
    return BACKTRACK_CATASTROPHY_COMPANY_RE.search(text)
