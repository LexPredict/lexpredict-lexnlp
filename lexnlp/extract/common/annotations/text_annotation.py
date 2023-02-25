__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List
from html import escape
from lexnlp.utils.map import Map


class TextAnnotation:
    """
    It can be a CopyrightAnnotation, CourtAnnotation and so on...

    Example:
        cp = CopyrightAnnotation(name='Siemens', coords=(0, 100), text='text text')
        cp.company = 'Siemens'
        cp.year_start = 1996
        s1 = cp.get_cite()  # '/copyright/Siemens/1996'

        cp.year_end = 2019
        cp.locale = 'en'
        s2 = cp.get_cite()  # '/en/copyright/Siemens/1996/2019'
    """
    record_type = ''

    def __init__(self,
                 name: str,
                 locale: str,
                 coords: Tuple[int, int],
                 text: str = ''):
        self.coords = coords
        self.name = name
        self.text = text
        self.locale = locale

    def __repr__(self):
        s = f'{self.name} [{self.record_type}] at ({self.coords[0]}..{self.coords[1]})'
        if self.locale:
            s += f', loc: {self.locale}'
        return s

    def get_cite(self) -> str:
        path = [self.locale, self.record_type]
        val = self.get_cite_value_parts()
        if val:
            path += val
        return "/" + "/".join([escape(p) for p in path if p])

    def get_cite_value_parts(self) -> List[str]:
        # should be overriden in derived classes
        return [self.name]

    def get_extracted_text(self, full_text: str) -> str:
        # could be overriden
        return full_text[self.coords[0]: self.coords[1]]

    def to_dictionary(self) -> dict:
        df = Map({
            "attrs": {
                "start": self.coords[0],
                "end": self.coords[1]
            },
            "tags": {
                'Extracted Entity Type': self.record_type
            }
        })
        extras = self.get_dictionary_values()
        for key in extras:
            if key not in df:
                df[key] = extras[key]
            else:
                df[key] = {**df[key], **extras[key]}

        return df

    def get_dictionary_values(self) -> dict:
        # could be overriden
        return {}

    @staticmethod
    def safe_cast(val, to_type, default=None):
        try:
            return to_type(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def get_int_value(obj, def_value=None) -> int:
        if obj is None:
            return def_value
        if isinstance(obj, int):
            return obj
        try:
            return int(obj)
        # pylint:disable=bare-except
        except:
            return def_value
