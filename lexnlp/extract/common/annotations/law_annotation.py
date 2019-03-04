from html import escape
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class LawAnnotation(TextAnnotation):
    """
    create an object of LawAnnotation like
    cp = LawAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self, *args, **kwargs):
        super(LawAnnotation, self).__init__(record_type='law', *args, **kwargs)

    def get_cite_value_encoded(self) -> str:
        parts = [escape(self.name)]
        return "/".join([p for p in parts if p])

    def to_dictionary(self) -> dict:
        ant = dict(
            attrs={
                'start': self.coords[0],
                'end': self.coords[1]},
            tags={
                'Extracted Entity Type': 'law',
                'Extracted Entity Name': self.name,
                'Extracted Entity Text': self.text if self.text else self.name
            })
        return ant
