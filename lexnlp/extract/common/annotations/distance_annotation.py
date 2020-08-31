from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DistanceAnnotation(TextAnnotation):
    record_type = 'distance'
    """
    create an object of DistanceAnnotation like
    cp = DistanceAnnotation(coords=(0, 100), value='101 km')
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 amount: float = None,
                 distance_type: str = None):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.amount = amount
        self.distance_type = distance_type

    def get_cite_value_parts(self) -> List[str]:
        parts = [str(self.amount or ''),
                 self.distance_type or '']
        return parts

    def get_dictionary_values(self) -> dict:
        df = {
            'tags': {
                'Extracted Entity Value': str(self.amount or ''),
                'Extracted Entity Text': self.text
            }
        }
        return df
