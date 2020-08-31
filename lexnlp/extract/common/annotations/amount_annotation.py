from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AmountAnnotation(TextAnnotation):
    record_type = 'amount'
    """
    create an object of AmountAnnotation like
    cp = AmountAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 value: float = 0,
                 text: str = ''):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.value = value

    def get_cite_value_parts(self) -> List[str]:
        return [str(self.value)] if self.value else []

    def get_dictionary_values(self) -> dict:
        df = {
            "tags": {
                'Extracted Entity Value': str(self.value or ''),
                'Extracted Entity Text': self.text
            }
        }
        return df
