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

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Union, List, Dict, Optional

import regex as re
from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS, CompanyDescriptor


def get_company_type_pipe(company_type_list: Union[None, List[str], Dict[str, CompanyDescriptor]] = None) -> str:
    company_type_list = company_type_list or COMPANY_TYPES
    if isinstance(company_type_list, dict):
        company_type_list = list(company_type_list.keys())  # type: List[str]

    # Setup company type list
    company_type_list.sort(key=len, reverse=True)
    company_type_pipe = '|'.join([re.escape(c.lower())
                                  for c in company_type_list])
    return company_type_pipe


def get_company_description_pipe(company_description_list: Optional[List[str]] = None) -> str:
    company_description_list = company_description_list or COMPANY_DESCRIPTIONS
    company_description_list.sort(key=len, reverse=True)
    company_description_pipe = '|'.join([re.escape(c.strip(".").lower())
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
