# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import pandas
import codecs
from typing import Iterable
from lexnlp.extract.common.ocr_rating.ocr_rating_calculator import BaseOcrRatingCalculator


# class builds language reference vectors that are used
# to compare N-gram distribution in a text given with
# "normal" N-gram distribution


class LangVectorDistributionBuilder:
    def build_texts_reference_distribution(self, texts: Iterable[str]):
        ngram_vector_list = []
        calc = BaseOcrRatingCalculator()
        for text in texts:
            if not text or len(text) < 100:
                continue
            file_series = calc.get_text_ngram_series(text)
            ngram_vector_list.append(file_series)

        if not ngram_vector_list:
            return None

        ngram_vector_df = pandas.DataFrame(ngram_vector_list).fillna(0)
        ngram_vector_df = ngram_vector_df.loc[:, sorted(ngram_vector_df.columns)]

        ngram_prob_vector_df = ngram_vector_df.div(ngram_vector_df.sum(axis=1), axis=0)
        ngram_prob_norm_df = ngram_prob_vector_df.mean(axis=0)
        return ngram_prob_norm_df

    def build_files_reference_distribution(self, file_paths: Iterable[str]):
        def get_texts(f_paths):
            for file_path in f_paths:
                with codecs.open(file_path, 'r', encoding='utf-8') as fr:
                    text = fr.read()
                    yield text

        return self.build_texts_reference_distribution(get_texts(file_paths))
