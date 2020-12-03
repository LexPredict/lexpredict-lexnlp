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
import pandas
import codecs
from typing import Iterable
from lexnlp.extract.common.ocr_rating.ocr_rating_calculator import BaseOcrRatingCalculator

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
