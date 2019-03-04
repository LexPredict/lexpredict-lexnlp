"""Entity extraction for English using NLTK and basic regular expressions with
master data.

This module implements basic entity extraction functionality in English, but does NOT
rely on the pre-trained NLTK maximum entropy classifier.  Instead, it uses the NLTK English
grammar in combination with regular expressions and tested master data re: company types and
abbreviations (e.g., LLC).

Todo:
  * Better define interface for sentences vs. raw text
  * Standardize generator vs list
"""

# Imports
import string

from typing import Generator

import regex as re

from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS
from lexnlp.nlp.en.segments.sentences import get_sentence_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

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
COMPANY_NAME_PATTERN = r'[a-z0-9][a-z0-9 \,\.\-&]+?(?:\([a-z0-9][a-z0-9 \,\.\-\&]+?\))?'

# Setup template expression for name matches alone
COMPANY_PATTERN_TEMPLATE = r'''
{article_pattern}
(?P<full_name>
    (?P<company_name>
        (?P<company_description_of>{company_description_pattern})\s+of\s+{company_name_pattern})
        (?:\W+|$)(?P<company_type_of>{company_type_pattern})?
    |
    (?P<company_name>{company_name_pattern})[\s\,]+
    (?:
        (?P<company_description_and>{company_description_pattern})\s+and
        |
        (?P<company_description>{company_description_pattern})(?:\s\w+)*[\s\,]+(?P<company_type>{company_type_pattern})
        |
        (?P<company_description_single>{company_description_pattern})
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
    s:return:
    """
    company_pattern_template = company_pattern_template or COMPANY_PATTERN_TEMPLATE
    company_name_pattern = company_name_pattern or COMPANY_NAME_PATTERN
    company_type_list = company_type_list or COMPANY_TYPES
    if isinstance(company_type_list, dict):
        company_type_list = list(company_type_list.keys())

    # Setup company type list
    company_type_list.sort(key=len, reverse=True)
    company_type_pipe = "|".join([re.escape(c.lower())
                                  for c in company_type_list])

    # Setup description list
    company_description_list = company_description_list or COMPANY_DESCRIPTIONS
    company_description_list.sort(key=len, reverse=True)
    company_description_pipe = "|".join([re.escape(c.strip(".").lower())
                                         for c in company_description_list])

    # Materialize pattern form intermediate word lists
    return company_pattern_template \
        .format(company_name_pattern=company_name_pattern,
                article_pattern=article_pattern,
                company_type_pattern=company_type_pipe,
                company_description_pattern=company_description_pipe)


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


def get_companies(text: str,
                  use_article: bool = False,
                  detail_type: bool = False,
                  parse_name_abbr: bool = False,
                  return_source: bool = False) -> Generator:
    """
    Find company names in text, optionally using the stricter article/prefix expression.
    :param text:
    :param use_article:
    :param detail_type:
    :param parse_name_abbr:
    :param return_source:
    :return:
    """
    # Select regex
    re_c = RE_ARTICLE_COMPANY if use_article else RE_COMPANY

    # Iterate through sentences
    for sentence in get_sentence_list(text):
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
            company_name = company_name.strip(
                string.punctuation.replace('&', '').replace(')', '') + string.whitespace)
            company_name = re.sub(r'^\s*(?:and|&|of)\s+|\s+(?:and|&|of)\s*$', '',
                                  company_name, re.IGNORECASE)
            if not company_name:
                continue

            # f.e., a Delaware company
            if company_name.lower().startswith('a ') or captures.get('article') == ['a']:
                continue

            company_description = captures["company_description_of"] or \
                                  captures["company_description_and"] or \
                                  captures["company_description"] or \
                                  captures["company_description_single"]
            company_description = "".join(company_description).strip(
                string.punctuation + string.whitespace)
            # catch ABC & Company LLC case
            if company_description.lower() == 'company' and \
                    ('& company' in company_name.lower() or 'and company' in company_name.lower()):
                company_description = None
            company_description = company_description or None
            if company_description:
                company_name = re.sub(r'[\s,]%s$' % company_description, '', company_name)
                if not company_name or \
                        ARTICLE_RE.fullmatch(company_name) or \
                        re.match(r'.+?\s(?:of|in)$', company_name.lower()):
                    continue
            if company_name in COMPANY_DESCRIPTIONS:
                continue

            abbr_name = "".join(captures["abbr_name"]) or None

            ret = (company_name,
                   company_type)
            if detail_type:
                ret += (COMPANY_TYPES[company_type.lower()]['abbr'] if company_type else None,
                        COMPANY_TYPES[company_type.lower()]['label'] if company_type else None)
            ret += (company_description,)
            if parse_name_abbr:
                ret += (abbr_name,)
            if return_source:
                ret += (sentence,)
            # no args:         = [company_name, company_type, company_description]
            # detail_type:     + [company_type_abbr, company_type_label]
            # parse_name_abbr: + [abbr_name]
            # return_source:   + [source]
            yield ret


def get_parties_as(text, detail_type=False) -> Generator:
    """
    Return parties.
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

        for co_name, co_type, co_desc in get_companies(party_string, detail_type=detail_type):
            yield co_name, co_type, co_desc, party_type
