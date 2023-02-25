"""Urls extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic urls extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
from typing import Final, Generator, List

from lexnlp.extract.common.annotations.url_annotation import UrlAnnotation


URL_PTN = r"""
(?xi)
\b
(                       # Capture 1: entire matched URL
  (?:
    https?://               # http or https protocol
    |                       #   or
    www\d{0,3}[.]           # "www.", "www1.", "www2." … "www999."
    |                           #   or
    [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name followed by a slash
  )
  (?:                       # One or more:
    [^\s()<>]+                  # Run of non-space, non-()<>
    |                           #   or
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
  )+
  (?:                       # End with:
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
    |                               #   or
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]        # not a space or one of these punct chars
  )
)
"""
URL_PTN_RE: Final[re.Pattern] = re.compile(URL_PTN, re.IGNORECASE | re.MULTILINE | re.VERBOSE)


def get_urls(text: str) -> Generator[str, None, None]:
    """
    Find urls in text.
    """
    for ant in get_url_annotations(text):
        yield ant.url


def get_url_list(text: str) -> List[str]:
    """
    Get a list of URLs found in text.
    """
    return list(get_urls(text))


def get_url_annotations(text: str) -> Generator[UrlAnnotation, None, None]:
    """
    Get UrlAnnotations corresponding to URLs found in text.
    """
    for match in URL_PTN_RE.finditer(text):
        url = match.group()
        ant = UrlAnnotation(coords=match.span(), url=url)
        yield ant


def get_url_annotation_list(text: str) -> List[UrlAnnotation]:
    """
    Get a list of UrlAnnotations corresponding to URLs found in text.
    """
    return list(get_url_annotations(text))
