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

import regex as re

from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS
from lexnlp.nlp.en.segments.sentences import get_sentences

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Commonly re-used regular expression components
ARTICLE_PATTERN = r'''[\s][\n]?(by\ and\ between|by\ and\ among|among|between|with|the|and|to|by|an|a)[\s]+'''
COMPANY_NAME_PATTERN = r'[a-z0-9 \,\.\-\(\)&]+?'

# Setup template expression for name matches alone
COMPANY_PATTERN_TEMPLATE = r'''
(
    (?P<company_name>{company_name_pattern})
    [\s\n]*
    (
        (?P<company_description>{company_description_pattern})
        |
        (?P<company_type>{company_type_pattern})
    ){{1,}}
    (\,|\.|\;|\s|$)
)+?
'''

# Setup template expression for matches including preceding article/preposition
COMPANY_ARTICLE_PATTERN_TEMPLATE = r'''
(
    (
        (?P<article>{article_pattern})
    ){{1,}}
    (?P<company_name>{company_name_pattern})
    [\s\n]*
    (
        (?P<company_description>{company_description_pattern})
        |
        (?P<company_type>{company_type_pattern})
    ){{1,}}
    (\,|\.|\;|\s|$)
)+?
'''


def create_company_article_pattern(company_article_pattern_template, company_name_pattern, article_pattern,
                                   company_type_list=None,
                                   company_description_list=None):
    """
    Create a company-article pattern for regular expression.
    :param company_article_pattern_template:
    :param company_name_pattern:
    :param article_pattern:
    :param company_type_list:
    :param company_description_list:
    s:return:
    """
    # Setup company type list
    if not company_type_list:
        company_type_list = COMPANY_TYPES
    company_type_list.sort(key=len, reverse=True)
    company_type_pipe = "|".join([c.strip(".").lower().replace(" ", "\\ ").replace(".", "\\.")
                                  for c in company_type_list])

    # Setup description list
    if not company_description_list:
        company_description_list = COMPANY_DESCRIPTIONS
    company_description_list.sort(key=len, reverse=True)
    company_description_pipe = "|".join([c.strip(".").lower().replace(" ", "\\ ").replace(".", "\\.")
                                         for c in company_description_list])

    # Materialize pattern form intermediate word lists
    return company_article_pattern_template \
        .format(company_name_pattern=company_name_pattern,
                article_pattern=article_pattern,
                company_type_pattern=company_type_pipe,
                company_description_pattern=company_description_pipe)


def create_company_pattern(company_pattern_template, company_name_pattern, company_type_list=None,
                           company_description_list=None):
    """
    Create a company pattern for regular expression.
    :param company_description_list:
    :param company_pattern_template:
    :param company_name_pattern:
    :param company_type_list:
    s:return:
    """
    # Setup company type list
    if not company_type_list:
        company_type_list = COMPANY_TYPES
    company_type_list.sort(key=len, reverse=True)
    company_type_pipe = "|".join([c.strip(".").lower().replace(" ", "\\ ").replace(".", "\\.")
                                  for c in company_type_list])

    # Setup description list
    if not company_description_list:
        company_description_list = COMPANY_DESCRIPTIONS
    company_description_list.sort(key=len, reverse=True)
    company_description_pipe = "|".join([c.strip(".").lower().replace(" ", "\\ ").replace(".", "\\.")
                                         for c in company_description_list])

    # Materialize pattern form intermediate word lists
    return company_pattern_template \
        .format(company_name_pattern=company_name_pattern,
                company_type_pattern=company_type_pipe,
                company_description_pattern=company_description_pipe)


# Create patterns from parameters
COMPANY_PATTERN = create_company_pattern(COMPANY_PATTERN_TEMPLATE, COMPANY_NAME_PATTERN, COMPANY_TYPES)
COMPANY_ARTICLE_PATTERN = create_company_article_pattern(COMPANY_ARTICLE_PATTERN_TEMPLATE, COMPANY_NAME_PATTERN,
                                                         ARTICLE_PATTERN, COMPANY_TYPES)

# Compile regular expression objects
RE_COMPANY = re.compile(COMPANY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)
RE_ARTICLE_COMPANY = re.compile(COMPANY_ARTICLE_PATTERN,
                                re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

# Create party...as pattern
PARTY_AS_PATTERN = r'''
(?P<party_string>.+?)[\s\,]
(as\ the\s|as\s|\"|“)
(?P<party_type>.+?)(?=\,|\;|\.|\"|”|\n|$)
'''
RE_PARTY_AS = re.compile(PARTY_AS_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.VERBOSE)


def get_companies(text, use_article=False, return_source=False):
    """
    Find company names in text, optionally using the stricter article/prefix expression.
    :param text:
    :param use_article:
    :param return_source:
    :return:
    """
    # Select regex
    re_c = RE_ARTICLE_COMPANY if use_article else RE_COMPANY

    # Iterate through sentences
    for sentence in get_sentences(text):
        for match in re_c.finditer(sentence):
            captures = match.capturesdict()
            company_name = "".join(captures["company_name"]).strip(string.punctuation).strip(string.whitespace)
            company_type = "".join(captures["company_type"]).strip(string.punctuation).strip(string.whitespace)
            if len(company_type) == 0:
                company_type = None
            company_description = "".join(captures["company_description"]).strip(string.punctuation) \
                .strip(string.whitespace)
            if len(company_description) == 0:
                company_description = None
            if company_name.lower().startswith("and "):
                company_name = company_name[3:].strip()

            if return_source:
                yield (company_name, company_type, company_description, sentence)
            else:
                yield (company_name, company_type, company_description)


def get_parties_as(text):
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

        for company_match in RE_COMPANY.finditer(party_string):
            yield company_match.capturesdict(), party_type
