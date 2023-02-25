"""
Geo Entities extraction configuration.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Minimal length of geo entity aliases to search for.
# Allows avoiding false-positives on first and last names abbreviations (A.M. Best) e.t.c.


MIN_ALIAS_LEN = 2

# List of aliases to exclude from search: [(alias:str, language:str, is_abbrev:bool), ...]
ALIAS_BLACK_LIST = []
