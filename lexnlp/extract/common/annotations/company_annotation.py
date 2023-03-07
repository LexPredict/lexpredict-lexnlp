__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List, Optional
from lexnlp.utils.map import Map
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class CompanyAnnotation(TextAnnotation):
    """
    create an object of CompanyAnnotation like
    cp = CompanyAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'company'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 name: Optional[str] = None,
                 name_abbr: Optional[str] = None,
                 company_type_full: Optional[str] = None,
                 company_type_abbr: Optional[str] = None,
                 company_type_label: Optional[str] = None,
                 description: Optional[str] = None,
                 text: Optional[str] = None,
                 counter: int = 1):
        super().__init__(
            name=name,
            coords=coords,
            locale=locale)
        self.name_abbr = name_abbr
        self.company_type_full = company_type_full
        self.company_type_abbr = company_type_abbr
        self.company_type_label = company_type_label
        self.description = description
        self.text = text
        self.counter = counter

    @property
    def company_type(self) -> str:
        return self.company_type_full or self.company_type_abbr \
               or self.company_type_label or ''

    def __repr__(self):
        text = self.name or self.name_abbr or self.text or ''
        if self.company_type:
            text += f' {self.company_type}'
        return f'{text}, ({self.coords[0]}, {self.coords[1]})'

    def get_cite_value_parts(self) -> List[str]:
        parts = [self.name, str(self.company_type)]
        return parts

    def get_dictionary_values(self) -> dict:
        df = Map({
            'tags': {
                'Extracted Entity Name': self.name,
                'Extracted Entity Text': self.text or self.name
            }
        })
        if self.name:
            df.tags["Extracted Entity Company"] = self.name
        if self.company_type:
            df.tags["Extracted Entity Company Type"] = self.company_type
        return df
