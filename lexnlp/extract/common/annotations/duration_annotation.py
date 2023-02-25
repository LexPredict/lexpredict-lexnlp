__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class DurationAnnotation(TextAnnotation):
    """
    create an object of DurationAnnotation like
    cp = DurationAnnotation(coords=(0, 100), value='101 ms')
    """
    record_type = 'duration'

    def __init__(
        self,
        coords: Tuple[int, int],
        locale: str = 'en',
        text: str = None,
        amount: Decimal = None,
        prefix: str = None,
        duration_days: Decimal = None,
        duration_type: str = None,
        duration_type_en: str = None,
        is_complex: bool = False,
        value_dict: dict = None
    ) -> None:
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text
        )
        self.amount: Decimal = amount
        self.prefix: str = prefix
        self.duration_days: Decimal = duration_days if amount is not None else None
        self.duration_type: str = duration_type
        self.duration_type_en: str = duration_type_en
        self.is_complex: bool = is_complex
        self.value_dict: dict = value_dict

    def get_cite_value_parts(self) -> List[str]:
        parts = [str(self.amount or ''),
                 self.duration_type or '']
        return parts

    def get_dictionary_values(self) -> dict:
        df = {
            'tags': {
                'Extracted Entity Value': str(self.amount or ''),
                'Extracted Entity Text': self.text
            }
        }
        return df
