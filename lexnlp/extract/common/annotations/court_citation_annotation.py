__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List
from lexnlp.utils.map import Map
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class CourtCitationAnnotation(TextAnnotation):
    """
    create an object of CourtCitationAnnotation like
    cp = CourtCitationAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'court citation'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 name: str = '',
                 short_name: str = None,
                 text: str = None,
                 translated_name: str = None):
        super().__init__(
            coords=coords,
            name=name,
            locale=locale,
            text=text)
        self.short_name = short_name
        self.translated_name = translated_name

    def get_cite_value_parts(self) -> List[str]:
        parts = [self.name or '',
                 self.short_name or '',
                 self.translated_name or '']
        return parts

    def get_dictionary_values(self) -> dict:
        dc = Map({
            'tags': {
                'Extracted Entity Text': self.text or self.name
            }
        })
        if self.name:
            dc.tags["Extracted Entity Name"] = self.name
        if self.short_name:
            dc.tags["Extracted Entity Short Name"] = self.short_name
        return dc
