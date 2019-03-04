import os
import codecs
from html import escape
from typing import List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


def load_resource_document(doc_path: str, encoding: str="ascii") -> str:
    """
    load file as string from test_data folder
    """
    full_path = os.path.dirname(__file__) + '/../../test_data/' + doc_path
    with codecs.open(full_path, encoding=encoding, mode='r') as myfile:
        data = myfile.read()
    return data


def save_test_document(doc_path: str, text: str, encoding: str="utf-8") -> None:
    """
    saves text as a file in test_data folder
    """
    full_path = os.path.dirname(__file__) + '/../../test_data/' + doc_path
    with codecs.open(full_path, encoding=encoding, mode='w') as myfile:
        myfile.write(text)


def annotate_text(text: str, annotations: List[TextAnnotation]) -> str:
    """
    :param text: source text
    :param annotations: text annotations
    :return: html, where annotations are replaced by HREFs + annotations' list in the end of the document
    """
    annotations.sort(key=lambda a: a.coords[1])
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
        part = text[end:ant.coords[0]]
        result += escape(part).replace('\n', '<br/>')

        title = '[%d] ' % ant.index + escape(ant.text).replace('"', "'")
        rf = '<a href="#" title="%s">' % title
        link_title = escape(text[ant.coords[0]: ant.coords[1]])
        if ant.index > 0:
            link_title = 'REFR#%d ' % ant.index + link_title
        rf += link_title
        rf += '</a>'
        result += rf

        end = ant.coords[1]
        if end >= len(text):
            break
    if end < len(text):
        part = text[end:-1]
        result += escape(part).replace('\n', '<br/>')

    result += "</p> <ol>"
    for ant in annotations:
        item = escape(ant.name)
        explanation = escape(ant.get_extracted_text(text))
        result += "<li><b>%s</b>: %s</li>" % (item, explanation)
    result += """
  </ol>
</body>
</html>"""
    return result
