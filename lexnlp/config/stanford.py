"""
Configuration for the Stanford NLP library
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os

import nltk.data

from lexnlp import get_lib_path


# Setup Stanford configuration


STANFORD_VERSION = "2017-06-09"
STANFORD_BASE_PATH = '/usr/lexnlp/libs/stanford_nlp'

def _resolve_stanford_path(component: str) -> str:
    candidates = []
    for root in nltk.data.path:
        # Bootstrap defaults to root/stanford_nlp. Explicit installations can
        # also declare the Stanford directory itself as an NLTK data root.
        candidates.extend((
            os.path.join(root, "stanford_nlp", component),
            os.path.join(root, component),
        ))
    candidates.extend((
        os.path.join(STANFORD_BASE_PATH, component),
        os.path.join(get_lib_path(), "stanford_nlp", component),
    ))
    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    # Preserve the historical missing-assets path and diagnostics. Legacy
    # installations still require their location to be trusted in NLTK_DATA.
    return candidates[-1]


STANFORD_POS_PATH = _resolve_stanford_path(f"stanford-postagger-full-{STANFORD_VERSION}")
STANFORD_NER_PATH = _resolve_stanford_path(f"stanford-ner-{STANFORD_VERSION}")
