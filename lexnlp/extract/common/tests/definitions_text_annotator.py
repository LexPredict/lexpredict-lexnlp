from typing import List
from lexnlp.tests.test_utils import TextAnnotation, save_test_document, annotate_text


def annotate_definitions_text(text: str, definitions: List[dict], save_path: str) -> None:
    ants = []
    for df in definitions:
        ref_text = df["tags"]["Extracted Entity Text"]
        name = df["tags"]["Extracted Entity Definition Name"]
        start = df["attrs"]["start"]
        end = df["attrs"]["end"]
        w_start = text.find(name, start, end + 1)

        if w_start >= 0:
            start = w_start
            end = start + len(name)

        ant = TextAnnotation((start, end), ref_text)
        ants.append(ant)
    markup = annotate_text(text, ants)
    save_test_document(save_path, markup)
