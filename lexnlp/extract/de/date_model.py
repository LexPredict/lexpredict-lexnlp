__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import string


DE_UNICODE_ALPHAS = 'äöüẞ'
DE_ALPHA_CHAR_SET = set(string.ascii_letters + DE_UNICODE_ALPHAS + DE_UNICODE_ALPHAS.upper())

DE_ALPHABET = DE_UNICODE_ALPHAS + DE_UNICODE_ALPHAS.upper()
DATE_MODEL_CHARS = []
DATE_MODEL_CHARS.extend(DE_ALPHABET + string.ascii_letters)
DATE_MODEL_CHARS.extend(string.digits)
DATE_MODEL_CHARS.extend(['-', '/', ' ', '%', '#', '$', '.', ','])
MONTH_NAMES = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
               'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
