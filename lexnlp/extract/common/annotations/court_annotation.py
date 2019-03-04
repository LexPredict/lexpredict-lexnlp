from html import escape
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class CourtAnnotation(TextAnnotation):
    """
    create an object of CourtAnnotation like
    cp = CourtAnnotation(name='name', coords=(0, 100), text='text text')
    """
    def __init__(self, *args, **kwargs):
        super(CourtAnnotation, self).__init__(record_type='court', *args, **kwargs)
        self.jurisdiction = ''
        self.court_type = ''

    def get_cite_value_encoded(self) -> str:
        parts = [escape(self.name),
                 self.jurisdiction,
                 self.court_type]
        return "/".join([p for p in parts if p])

    def to_dictionary(self) -> dict:
        ant = dict(
            attrs={
                'start': self.coords[0],
                'end': self.coords[1]},
            tags={
                'Extracted Entity Type': 'court',
                'Extracted Entity Court Name': self.name,
                'Extracted Entity Text': self.text,
                'Extracted Entity Court Type': self.record_type,
                'Extracted Entity Court Jurisdiction': self.jurisdiction
            })
        return ant
