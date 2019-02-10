import os
import codecs
from html import escape
from typing import Tuple, List


class TextAnnotation:
    def __init__(self, word_coords: Tuple[int, int], text: str, index: int=0):
        self.word_coords = word_coords
        self.text = text
        self.index = index


def load_resource_document(doc_path: str, encoding: str="ascii") -> str:
    full_path = os.path.dirname(__file__) + '/../../test_data/' + doc_path
    with codecs.open(full_path, encoding=encoding, mode='r') as myfile:
        data = myfile.read()
    return data


def save_test_document(doc_path: str, text: str, encoding: str="utf-8") -> None:
    full_path = os.path.dirname(__file__) + '/../../test_data/' + doc_path
    with codecs.open(full_path, encoding=encoding, mode='w') as myfile:
        myfile.write(text)


def annotate_text(text: str, annotations: List[TextAnnotation]) -> str:
    annotations.sort(key=lambda a: a.word_coords[1])
    for i, ant in enumerate(annotations):
        ant.index = i + 1
    result = """
<html>
<head>
  <meta charset="UTF-8">
</head>
<body>
  <p>
    """
    end = 0
    for ant in annotations:
        part = text[end:ant.word_coords[0]]
        result += escape(part).replace('\n', '<br/>')

        title = '[%d] ' % ant.index + escape(ant.text).replace('"', "'")
        rf = '<a href="#" title="%s">' % title
        link_title = escape(text[ant.word_coords[0]:ant.word_coords[1]])
        if ant.index > 0:
            link_title = 'REFR#%d ' % ant.index + link_title
        rf += link_title
        rf += '</a>'
        result += rf

        end = ant.word_coords[1]
        if end >= len(text):
            break
    if end < len(text):
        part = text[end:-1]
        result += escape(part).replace('\n', '<br/>')

    result += "</p> <ol>"
    for ant in annotations:
        item = text[ant.word_coords[0]:ant.word_coords[1]] + ': ' + ant.text
        result += "<li>%s</li>" % escape(item)
    result += """
  </ol>
</body>
</html>"""
    return result
