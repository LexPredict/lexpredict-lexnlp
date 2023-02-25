__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.nlp.en.segments.sentences import pre_process_document
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.utils.lines_processing.parsed_text_quality_estimator import ParsedTextQualityEstimator


class TestParsedTextQualityEstimator(TestCase):
    def test_estimate_dense_text(self):
        text = load_resource_document(
            "lexnlp/utils/parsing/pdf_malformat_parsed_default.txt", 'utf-8')
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        self.assertGreater(estim.extra_line_breaks_prob, 50)

        text = load_resource_document(
            'lexnlp/utils/parsing/pdf_malformat_parsed_stripper.txt', 'utf-8')
        estim = estimator.estimate_text(text)
        self.assertLess(estim.extra_line_breaks_prob, 30)

    def test_estimate_text_abusing_headers(self):
        text = load_resource_document(
            'lexnlp/utils/parsing/text_abusing_headers.txt', 'utf-8')
        text = pre_process_document(text)
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        self.assertLess(estim.extra_line_breaks_prob, 50)

    def test_estimate_fishy_header(self):
        text = """
Notwithstanding anything in this Section (B) of Article IV to the contrary, in the event any such disruption to Shmenant's operations and use of the demised premises is attributable to Landlord's negligence, or that of its agents, contractors, servants or employees, or is attributable to a breach by Landlord of its obligations under this lease, and if such disruption shall materially impair Shmenant's use of the demised premises for a period in excess of five (5) business days in duration, then a just proportion of the Rent, according to the nature and extent of the impairment to Shmenant's operation and use of the demised premises shall abate for any such period of time from the date of disruption which is in excess of said five (5) business days in duration.



ARTICLE V


RENT"""
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        self.assertLess(estim.extra_line_breaks_prob, 50)
