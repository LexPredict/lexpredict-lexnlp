__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, Union, List
from lexnlp.utils.map import Map
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class CopyrightAnnotation(TextAnnotation):
    """
    create an object of CopyrightAnnotation like
    cp = CopyrightAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'copyright'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 name: str = '',
                 sign: str = '',
                 company: str = '',
                 text: str = '',
                 date: str = '',
                 year_start: Union[int, str] = '',
                 year_end: Union[str, int] = ''):
        super().__init__(
            name=name,
            coords=coords,
            locale=locale)
        self.sign: str = sign
        self.company: str = company
        self.text: str = text
        self.date: str = date
        self.year_start = TextAnnotation.get_int_value(year_start)
        self.year_end = TextAnnotation.get_int_value(year_end)

    def __repr__(self):
        text = self.company or self.name or self.text or ''
        return f'{text}, ({self.coords[0]}, {self.coords[1]})'

    def get_cite_value_parts(self) -> List[str]:
        parts = [self.company or self.name,
                 str(self.year_start) if self.year_start else '',
                 str(self.year_end) if self.year_end else '']
        return parts

    def get_dictionary_values(self) -> dict:
        df = Map({
            'tags': {
                'Extracted Entity Name': self.name,
                'Extracted Entity Text': self.text or self.name
            }
        })
        if self.company:
            df.tags["Extracted Entity Company"] = self.company
        if self.year_start:
            df.tags["Extracted Entity Start"] = self.year_start
        if self.year_end:
            df.tags["Extracted Entity End"] = self.year_end
        return df
