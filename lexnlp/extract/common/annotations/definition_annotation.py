__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, List

from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class DefinitionAnnotation(TextAnnotation):
    """
    create an object of DefinitionAnnotation like
    cp = DefinitionAnnotation(name='name', coords=(0, 100), text='text text')
    """
    record_type = 'definition'

    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 name: str = '',
                 text: str = None):
        super().__init__(
            name=name,
            locale=locale,
            coords=coords,
            text=text)

    def get_cite_value_parts(self) -> List[str]:
        return [self.name]

    # pylint: disable=unused-argument
    def get_extracted_text(self, full_text: str) -> str:
        return self.text

    def get_dictionary_values(self) -> dict:
        ant = {
            'tags': {
                'Extracted Entity Definition Name': self.name,
                'Extracted Entity Text': self.text or self.name
            }
        }
        return ant
