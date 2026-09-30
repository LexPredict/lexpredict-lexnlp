__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Tuple
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class AddressAnnotation(TextAnnotation):
    """
    create an object of CopyrightAnnotation like
    cp = CopyrightAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'address'

    def __init__(
        self,
        name: str,
        locale: str,
        coords: Tuple[int, int],
        text: str = '',
    ):
        super().__init__(
            name=name,
            locale=locale,
            coords=coords,
            text=text
        )

    def get_cite_value_parts(self) -> List[str]:
        return [self.text]

    def get_dictionary_values(self) -> dict:
        df = {
            'tags': {
                'Extracted Entity Text': self.text,
            }
        }
        return df
