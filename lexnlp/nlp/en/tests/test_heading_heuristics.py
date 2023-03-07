__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import json
from typing import Dict, Any, List
from unittest import TestCase
import os
import codecs

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.nlp.en.segments.heading_heuristics import HeadingHeuristics
from lexnlp.nlp.en.segments.sections import find_section_titles, DocumentSection


class TestHeadingHeuristics(TestCase):
    def test_too_short(self):
        self.assertEqual(True,
                         HeadingHeuristics.is_new_title_better('B', 'Title B'))
        self.assertEqual(False,
                         HeadingHeuristics.is_new_title_better('A', 'B2'))

    def test_too_long(self):
        long_text = 'Hea' + 'd' * 200 + 'ing'
        self.assertEqual(True,
                         HeadingHeuristics.is_new_title_better(long_text, 'Title B'))

    def test_new_better(self):
        self.assertEqual(True,
                         HeadingHeuristics.is_new_title_better('Some title', 'II.IV Some other title'))

    def test_old_better(self):
        self.assertEqual(False,
                         HeadingHeuristics.is_new_title_better('II.IV Some title', 'II.IV Some other title'))

    def test_find_better_titles(self):
        full_text = self.load_resource_document('heading_document.txt')
        sections_txt = self.load_resource_document('heading_doc_sections.txt')
        sections = self.parse_section(json.loads(sections_txt))
        section_titles = [s.title for s in sections]

        sentences_txt = self.load_resource_document('heading_doc_sentences.txt')
        sentence_coords = json.loads(sentences_txt)

        find_section_titles(sections, sentence_coords, full_text)
        new_section_titles = [s.title for s in sections]
        self.assertNotEqual(section_titles[16], new_section_titles[16])

    @classmethod
    def load_resource_document(cls, doc_name: str) -> str:
        file_path = os.path.join(lexnlp_test_path, f'lexnlp/nlp/en/heading/{doc_name}')
        with codecs.open(file_path, 'r', encoding='utf-8') as fr:
            text = fr.read()
        return text

    @classmethod
    def parse_section(cls, section_dict: List[Dict[str, Any]]) -> List[DocumentSection]:
        sections = []
        for item in section_dict:
            s = DocumentSection()
            for key in item:
                setattr(s, key, item[key])
            sections.append(s)
        return sections
