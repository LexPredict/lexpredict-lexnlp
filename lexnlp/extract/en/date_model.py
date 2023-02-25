"""Date extraction for English.

This module implements date extraction functionality in English.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=bare-except

# Standard imports
import os
import string
import joblib


# Setup path


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load model
MODEL_DATE = joblib.load(os.path.join(MODULE_PATH, "./date_model.pickle"))

ALPHA_CHAR_SET = set(string.ascii_letters)
DATE_MODEL_CHARS = []
DATE_MODEL_CHARS.extend(string.ascii_letters)
DATE_MODEL_CHARS.extend(string.digits)
DATE_MODEL_CHARS.extend(["-", "/", " ", "%", "#", "$"])
