from html import escape
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class DefinitionAnnotation(TextAnnotation):
    """
    create an object of DefinitionAnnotation like
    cp = DefinitionAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self, *args, **kwargs):
        super(DefinitionAnnotation, self).__init__(record_type='definition', *args, **kwargs)

    def get_cite_value_encoded(self) -> str:
        parts = [escape(self.name)]
        return "/".join([p for p in parts if p])

    def get_extracted_text(self, full_text: str):
        return self.text

    def to_dictionary(self) -> dict:
        ant = {
            "attrs": {
                "start": self.coords[0],
                "end": self.coords[1]},
            "tags": {
                'Extracted Entity Type': 'definition',
                'Extracted Entity Definition Name': self.name,
                'Extracted Entity Text': self.text if self.text else self.name
            }
        }
        return ant
