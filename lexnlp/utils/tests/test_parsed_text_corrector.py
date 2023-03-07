__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import codecs
from os import listdir
from os.path import isfile, join

from unittest import TestCase
from lexnlp.nlp.en.segments.sentences import pre_process_document
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.utils.lines_processing.parsed_text_corrector import ParsedTextCorrector


class TestParsedTextCorrector(TestCase):
    def test_estimate_dense_text(self):
        text = load_resource_document(
            'lexnlp/utils/parsing/pdf_malformat_parsed_default.txt', 'utf-8')
        corrector = ParsedTextCorrector()
        corr = corrector.correct_line_breaks(text)
        self.assertLess(len(corr), len(text))

    def test_correct_if_corrupted(self):
        ok_text = """
While we pursued the horsemen of the north, He slily stole away and left his men:
Whereat the great Lord of Northumberland. Whose warlike ears could never brook retreat. Cheer'd up the drooping army; 
and himself, Lord Clifford and Lord Stafford, all abreast, Charged our main battle's front, and breaking in
were by the swords of common soldiers slain.


Lord Stafford's father, Duke of Buckingham, is either slain or wounded dangerously;
I cleft his beaver with a downright blow: that this is true, father, behold his blood."""
        corrector = ParsedTextCorrector()
        corr = corrector.correct_if_corrupted(ok_text)
        self.assertEqual(len(corr), len(ok_text))

        corr = corrector.correct_line_breaks(ok_text)
        self.assertLess(len(corr), len(ok_text))

    def test_estimate_fishy_header(self):
        text = """
Notwithstanding anything in this Section (B) of Article IV to the contrary, in the event any such disruption to Tenant's operations and use of the demised premises is attributable to Landlord's negligence, or that of its agents, contractors, servants or employees, or is attributable to a breach by Landlord of its obligations under this lease, and if such disruption shall materially impair Tenant's use of the demised premises for a period in excess of five (5) business days in duration, then a just proportion of the Rent, according to the nature and extent of the impairment to Tenant's operation and use of the demised premises shall abate for any such period of time from the date of disruption which is in excess of said five (5) business days in duration.



ARTICLE V


RENT"""
        text = pre_process_document(text)
        corrector = ParsedTextCorrector()
        corr = corrector.correct_line_breaks(text)
        self.assertLess(len(corr), len(text))

    def process_text_files_in_folder(self, src_folder, dst_folder):
        corrector = ParsedTextCorrector()

        files = [f for f in listdir(src_folder) if isfile(join(src_folder, f))]
        for file in files:
            text = ''
            full_path = src_folder + file
            with codecs.open(full_path, encoding='utf-8', mode='r') as myfile:
                text = myfile.read()
            text = pre_process_document(text)

            corr = corrector.correct_if_corrupted(text)
            if len(text) == len(corr):
                continue    # corr = ''

            savepath = dst_folder + file
            with codecs.open(savepath, encoding='utf-8', mode='w') as myfile:
                myfile.write(corr)
