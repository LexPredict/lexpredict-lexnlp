from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MoneyAnnotation(TextAnnotation):
    record_type = 'money'
    """
    create an object of MoneyAnnotation like
    cp = MoneyAnnotation(coords=(0, 100), value='10 000 USD')
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 amount: float = None,
                 currency: str = None):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.amount = amount
        self.currency = currency

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
