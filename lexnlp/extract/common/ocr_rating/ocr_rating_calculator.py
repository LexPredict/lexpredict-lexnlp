"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""

# -*- coding: utf-8 -*-

import codecs
import os
import string
from typing import Dict, Optional, List, Callable

import numpy
import pandas

from lexnlp.nlp.en.transforms.characters import get_character_ngram_distribution

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseOcrRatingCalculator:
    def __init__(self):
        self.distribution_by_lang = {}  # type: Dict[str, pandas.DataFrame]
        self.default_language = 'en'

    def get_rating(self, text: str, language: str) -> float:
        raise NotImplementedError()

    def get_file_rating(self, file_path: str, language: str) -> float:
        with codecs.open(file_path, 'r', encoding='utf-8') as fr:
            text = fr.read()
        return self.get_rating(text, language)

    def vectorize_text(self, text: str):
        file_series = self.get_text_ngram_series(text)
        file_prob_vector = file_series / file_series.sum()
        return file_prob_vector

    def get_text_ngram_series(self, text: str):
        file_buffer_ascii = ''.join([c for c in text if c in string.printable])
        file_buffer_ascii = ''.join([self.good_chars(c) for c in file_buffer_ascii])
        file_vector = get_character_ngram_distribution(file_buffer_ascii, 2, lowercase=False, stopword=False)
        return pandas.Series([v for v in file_vector.values()], index=[''.join(k) for k in file_vector.keys()])

    def init_language_data(self,
                           data_folders: List[str],
                           language_file_paths: Optional[List[str]] = None) -> None:
        """
        Try loading languages from language_file_paths. The try loading pickled
        dataframes (per language) from first data folder in the list,
        then loading dataframes from the second folder without overwriting already
        loaded files.
        :param language_file_paths: try this list (if passed) before trying subfolders
        :param data_folders: first data folders have priority over lest ones
        """
        if language_file_paths:
            for file_path in language_file_paths:
                lang = os.path.splitext(os.path.basename(file_path))[0]
                lang_df = pandas.read_pickle(file_path)
                self.distribution_by_lang[lang] = lang_df

        for lang_data_folder in data_folders:
            model_files = [i for i in os.listdir(lang_data_folder) if i.endswith('.pickle')]
            for file_name in model_files:
                lang = os.path.splitext(file_name)[0]
                if lang in self.distribution_by_lang:
                    continue
                lang_df = pandas.read_pickle(os.path.join(lang_data_folder, file_name))
                self.distribution_by_lang[lang] = lang_df

    @classmethod
    def break_chars(cls, x):
        if x == 'c':
            return 'o'
        elif x == 'd':
            return 'o'
        elif x == 't':
            return '+'
        elif x == 'f':
            return '+'
        else:
            return x

    @classmethod
    def good_chars(cls, x):
        return x


class CosineSimilarityOcrRatingCalculator(BaseOcrRatingCalculator):
    def get_cs(self, text: str, language: str) -> float:
        if not text:
            return 0
        text_prob_vector = self.vectorize_text(text)
        ngram_prob_norm_df = self.distribution_by_lang.get(language)
        if ngram_prob_norm_df is None:
            ngram_prob_norm_df = self.distribution_by_lang.get(self.default_language)
        merge_df = pandas.concat([ngram_prob_norm_df, text_prob_vector], axis=1, sort=True).fillna(0)
        similarity_score = numpy.dot(merge_df.loc[:, 0],
                                     merge_df.loc[:, 1]) / \
                           numpy.linalg.norm(merge_df.loc[:, 0]) / \
                           numpy.linalg.norm(merge_df.loc[:, 1])
        return similarity_score

    def get_rating(self, text: str, language: str) -> float:
        cs = self.get_cs(text, language)
        ocr_grade = numpy.round(int(cs * 100) / 10.)
        return ocr_grade


class QuadraticCosineSimilarityOcrRatingCalculator(CosineSimilarityOcrRatingCalculator):
    def get_rating(self, text: str, language: str) -> float:
        cs = super().get_cs(text, language)
        x = cs * 100  # 0.0 ... 100.0
        ocr_grade = 0 if x < 50 else \
            numpy.round(0.00219033 * (x ** 2) - 0.1239173 * x + 1.1268522)
        ocr_grade = min(ocr_grade, 10)
        return ocr_grade


def build_cs_rating_calculator(
        language_file_paths: Optional[List[str]] = None,
        primary_language_folder: Optional[str] = None) \
        -> CosineSimilarityOcrRatingCalculator:
    # noinspection PyTypeChecker
    return build_rating_calculator(CosineSimilarityOcrRatingCalculator,
                                   language_file_paths, primary_language_folder)


def build_cs_quad_rating_calculator(language_file_paths: Optional[List[str]] = None,
                                    primary_language_folder: Optional[str] = None) \
        -> QuadraticCosineSimilarityOcrRatingCalculator:
    # noinspection PyTypeChecker
    return build_rating_calculator(QuadraticCosineSimilarityOcrRatingCalculator,
                                   language_file_paths, primary_language_folder)


def build_rating_calculator(
        build_calc_object: Callable[[], BaseOcrRatingCalculator],
        language_file_paths: Optional[List[str]] = None,
        primary_language_folder: Optional[str] = None) \
        -> BaseOcrRatingCalculator:
    data_path = os.path.join(os.path.dirname(__file__), './reference_vectors')
    calc = build_calc_object()
    lang_paths = [primary_language_folder, data_path] if primary_language_folder else [data_path]
    calc.init_language_data(lang_paths, language_file_paths)
    return calc
