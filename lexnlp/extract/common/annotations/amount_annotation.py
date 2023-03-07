__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class AmountAnnotation(TextAnnotation):
    """
    create an object of AmountAnnotation like
    cp = AmountAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'amount'

    def __init__(
        self,
        coords: Tuple[int, int],
        locale: str = 'en',
        value: Decimal = Decimal('0.0'),
        text: str = ''
    ) -> None:
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text
        )
        self.value: Decimal = value

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
