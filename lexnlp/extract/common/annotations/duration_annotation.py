from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DurationAnnotation(TextAnnotation):
    record_type = 'duration'
    """
    create an object of DurationAnnotation like
    cp = DurationAnnotation(coords=(0, 100), value='101 ms')
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 amount: float = None,
                 prefix: str = None,
                 duration_days: float = None,
                 duration_type: str = None,
                 duration_type_en: str = None,
                 is_complex: bool = False):
        super().__init__(
            name='',
            locale=locale,
            coords=coords,
            text=text)
        self.amount = float(amount) if amount is not None else None
        self.prefix = prefix
        self.duration_days = float(duration_days) if amount is not None else None
        self.duration_type = duration_type
        self.duration_type_en = duration_type_en
        self.is_complex = is_complex

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
