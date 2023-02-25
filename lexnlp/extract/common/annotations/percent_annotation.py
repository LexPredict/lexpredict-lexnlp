__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.utils.map import Map


class PercentAnnotation(TextAnnotation):
    """
    create an object of PercentAnnotation like
    cp = PercentAnnotation(coords=(0, 100), value='10 000 USD')
    """
    record_type = 'percent'

    def __init__(
        self,
        coords: Tuple[int, int],
        locale: str = 'en',
        text: str = None,
        amount: Decimal = None,
        sign: str = None,
        fraction: Decimal = None
    ) -> None:
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text
        )
        self.amount: Decimal = amount
        self.sign: str = sign
        self.fraction: Decimal = fraction

    def get_cite_value_parts(self) -> List[str]:
        return [str(self.amount or '0'),
                self.sign or '']

    def get_dictionary_values(self) -> dict:
        df = Map({
            'tags': {
                'Extracted Entity Value': str(self.amount or ''),
                'Extracted Entity Text': self.text
            }
        })
        if self.sign:
            df.tags['sign'] = self.sign
        return df
