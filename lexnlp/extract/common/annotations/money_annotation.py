__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class MoneyAnnotation(TextAnnotation):
    """
    create an object of MoneyAnnotation like
    cp = MoneyAnnotation(coords=(0, 100), value='10 000 USD')
    """
    record_type = 'money'

    def __init__(
        self,
        coords: Tuple[int, int],
        locale: str = 'en',
        text: str = None,
        amount: Decimal = None,
        currency: str = None
    ) -> None:
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text
        )
        self.amount: Decimal = amount
        self.currency: str = currency

    def get_cite_value_parts(self) -> List[str]:
        parts = [str(self.amount or ''),
                 self.currency or '']
        return parts

    def get_dictionary_values(self) -> dict:
        df = {
            'tags': {
                'Extracted Entity Value': str(self.amount or ''),
                'Extracted Entity Text': self.text
            }
        }
        return df
