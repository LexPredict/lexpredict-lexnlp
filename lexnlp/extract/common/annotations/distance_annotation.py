__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class DistanceAnnotation(TextAnnotation):
    """
    create an object of DistanceAnnotation like
    cp = DistanceAnnotation(coords=(0, 100), value='101 km')
    """
    record_type = 'distance'

    def __init__(
        self,
        coords: Tuple[int, int],
        locale: str = 'en',
        text: str = None,
        amount: Decimal = None,
        distance_type: str = None,
    ) -> None:
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text,
        )
        self.amount: Decimal = amount
        self.distance_type: str = distance_type

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
