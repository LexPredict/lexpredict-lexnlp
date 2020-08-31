from typing import Tuple, List

from lexnlp.extract.common.annotations.text_annotation import TextAnnotation

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CourtAnnotation(TextAnnotation):
    record_type = 'court'
    """
    create an object of CourtAnnotation like
    cp = CourtAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 name: str = '',
                 text: str = '',
                 jurisdiction: str = '',
                 court_type: str = ''):
        super().__init__(
            locale=locale,
            coords=coords,
            name=name,
            text=text)
        self.jurisdiction = jurisdiction
        self.court_type = court_type

    def get_cite_value_parts(self) -> List[str]:
        parts = [self.name,
                 self.jurisdiction or '',
                 self.court_type or '']
        return parts

    def get_dictionary_values(self) -> dict:
        ant = dict(
            tags={
                'Extracted Entity Court Name': self.name,
                'Extracted Entity Text': self.text,
                'Extracted Entity Court Type': self.court_type,
                'Extracted Entity Court Jurisdiction': self.jurisdiction
            })
        return ant
