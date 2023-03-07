# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import locale
from typing import Sequence, Union


class LocaleContextManager:

    def __init__(self, category: int, _locale: str) -> None:
        """
        Set the locale for the given category. The locale can be
        a string, an iterable of two strings (language code and encoding),
        or None.

        Iterables are converted to strings using the locale aliasing
        engine. Locale strings are passed directly to the C lib.

        `category` may be given as one of the LC_* values.
        """
        self._original_locale: Sequence = locale.getlocale()
        self.category: int = category
        self.locale: str = _locale

    def __enter__(self) -> Union[str, str]:
        try:
            return locale.setlocale(self.category, self.locale)
        except locale.Error:
            ...

    def __exit__(self, type, value, traceback) -> None:
        locale.setlocale(self.category, self._original_locale)


class Language:
    def __init__(self,
                 code: str,  # ISO 639-1 2-symbol code
                 code_3: str,  # ISO 639-2 3-symbol code
                 title: str):
        self.code = code
        self.code_3 = code_3
        self.title = title

    def __str__(self):
        return self.code


class Locale:
    def __init__(self,
                 locale: str = ''):
        self.language = locale[:2].lower()
        self.locale_code = locale[3:].upper()
        if self.language and not self.locale_code:
            self.locale_code = self.language.upper()

    def get_locale(self):
        return f"{self.language}-{self.locale_code}"


LANG_EN = Language('en', 'eng', 'English')
LANG_DE = Language('de', 'ger', 'German')
LANG_ES = Language('es', 'spa', 'Spanish')

LANGUAGES = [
    LANG_EN,
    LANG_DE,
    LANG_ES
]

DEFAULT_LANGUAGE = LANG_EN
