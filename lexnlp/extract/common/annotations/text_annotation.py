from typing import Tuple
from html import escape


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
    def __init__(self,
                 record_type: str,
                 name: str,
                 locale: str,
                 coords: Tuple[int, int],
                 text: str = ''):
        self.record_type = record_type
        self.coords = coords
        self.name = name
        self.text = text
        self.locale = locale

    def __repr__(self):
        s = "%s [%s] at (%d..%d)" % (self.name, self.record_type, self.coords[0], self.coords[1])
        if self.locale:
            s += ", loc: %s" % self.locale
        return s

    def get_cite(self) -> str:
        path = [escape(p) for p in [self.locale, self.record_type] if p]
        val = self.get_cite_value_encoded()
        if val:
            path.append(val)
        return "/" + "/".join(path)

    def get_cite_value_encoded(self) -> str:
        # should be overriden in derived classes
        return self.name

    def get_extracted_text(self, full_text: str):
        # could be overriden
        return full_text[self.coords[0]: self.coords[1]]

    def to_dictionary(self) -> dict:
        # should be overriden
        return {}
