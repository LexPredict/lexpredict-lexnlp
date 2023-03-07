__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List
from lexnlp.utils.map import Map
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class RegulationAnnotation(TextAnnotation):
    """
    create an object of RegulationAnnotation like
    cp = RegulationAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'regulation'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 name: str = '',
                 text: str = None,
                 source: str = '',
                 country: str = ''):
        super().__init__(
            name=name,
            locale=locale,
            coords=coords,
            text=text)
        self.country = country
        self.source = source

    def get_cite_value_parts(self) -> List[str]:
        parts = [self.country or '',
                 self.source or '',
                 self.name or '']
        return parts

    def get_dictionary_values(self) -> dict:
        dic = Map({
            'tags': {
                'External Reference Issuing Country': self.country,
                'External Reference Text': self.name,
                'Extracted Entity Text': self.text or self.name
            }
        })
        if self.source:
            dic.tags['External Reference Source'] = self.source
        return dic

    def to_dictionary_legacy(self) -> dict:
        return {"regulation_type": self.source,
                "regulation_code": self.name,
                "regulation_text": self.text}
