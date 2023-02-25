#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.nlp.en.segments.sentences import get_sentence_list, build_sentence_model, \
    pre_process_document, post_process_sentence, get_sentence_span, get_sentence_span_list
from lexnlp.tests import lexnlp_tests


class TestGetSentenceSpan(TestCase):
    def test_hard_case(self):
        text = '“U.S. Person” means any Person that is a “United States Person” as defined ' + \
               '          in Section 7701(a)(30) of the Code.'
        spans = list(get_sentence_span(text))
        self.assertEqual(1, len(spans))
        self.assertEqual(text.strip(), spans[0][2].strip())

    def test_sentence_segmenter_empty(self):
        """
        Test basic sentence segmentation.
        """
        _ = get_sentence_list("")

    def test_sentence_segmenter(self):
        lexnlp_tests.test_extraction_func_on_test_data(get_sentence_list)

    def test_titles_in_post_process_sentence1(self):
        sentence = '''This is a title
    
    And this is the next sentence.
    '''

        text = '''Something. ''' + sentence + ''' That's it.'''
        start = text.index(sentence)
        span = (start, start + len(sentence))

        actual = [text[start:end].strip() for start, end in post_process_sentence(text, span)]
        expected = ['This is a title', 'And this is the next sentence.']
        self.assertEqual(expected, actual)

    def test_ocr_artifacts_in_post_process_sentence1(self):
        sentence = '''~~``~~~~```~~
        
        >>
        
        <<
        
        ""'''
        text = '''Something. ''' + sentence + '''That's it.'''
        start = text.index(sentence)
        span = (start, start + len(sentence))

        actual = [text[start:end] for start, end in post_process_sentence(text, span)]
        expected = []
        self.assertEqual(expected, actual)

    def test_ocr_artifacts_in_post_process_sentence2(self):
        sentence = '''\\
        
        ______f
        hello hello
          
        '''
        text = '''Something. ''' + sentence + '''That's it.'''
        start = text.index(sentence)
        span = (start, start + len(sentence))

        actual = [text[start:end] for start, end in post_process_sentence(text, span)]
        expected = ['______f\n        hello hello']
        self.assertEqual(expected, actual)

    def test_ocr_artifacts_in_post_process_sentence3(self):
        sentence = '''\\
        
        ba
         
        Ba ba
        
        Q
        
        F
    
        '''
        text = '''Something. ''' + sentence + '''That's it.'''
        start = text.index(sentence)
        span = (start, start + len(sentence))

        actual = [text[start:end] for start, end in post_process_sentence(text, span)]
        expected = []
        self.assertEqual(expected, actual)

    def test_build_sentence_model(self):
        """
        Test the custom Punkt model.
        :return:
        """
        # Setup training text and model
        training_text = "The I.R.C. is a large body of text produced by the U.S. Congress in D.C. every year."
        sentence_segmenter = lexnlp_tests.benchmark_extraction_func(build_sentence_model, training_text)
        num_sentences_custom = len(
            sentence_segmenter.tokenize("Have you ever cited the U.S. I.R.C. to your friends?"))
        self.assertEqual(1, num_sentences_custom)

    def test_pre_process_document(self):
        lexnlp_tests.test_extraction_func_on_test_data(pre_process_document, actual_data_converter=lambda text: [text])

    def test_36(self):
        text = '''Title-title 

Text goes here and here and here. Text goes here and here and here. Text goes here and here and 
here. Text goes here and here and here. Text goes here and here and here. Text goes here and 
here and here.   

36

'''
        actual = get_sentence_span_list(text)
        assert any('36' in a[2] for a in actual)

    def test_num_table(self):
        text = '''
        This is some text table with amounts.
        $36  37  38

    '''
        actual = get_sentence_span_list(text)
        assert any('37' in a[2] for a in actual)
        assert any('$36' in a[2] for a in actual)
        assert any('38' in a[2] for a in actual)
