# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

import gensim
import joblib
import pandas as pd

from lexnlp.nlp.en.tokens import get_token_list


class ContractTypeDetector:
    """
    The class detects document's contract type based on plain text.
    The class has to be initialized (load_models) before using.
    """

    def __init__(self,
                 rf_model_path: str,
                 d2v_model_path: str):
        self.rf_model = None
        self.d2v_model = None
        self.load_models(rf_model_path, d2v_model_path)

    def load_models(self,
                    rf_model_path: str,
                    d2v_model_path):
        with open(rf_model_path, "rb") as rf_model_file:
            self.rf_model = joblib.load(rf_model_file)
        self.d2v_model = gensim.models.word2vec.Word2Vec.load(d2v_model_path)

    def detect_contract_type(self,
                             type_vector: pd.Series,
                             min_prob: float = 0.15,
                             max_closest_prob_percent: int = 75,
                             unknown_category: str = '') -> str:
        """
        Decides what document type (string) is this based on sorted
        type_vector.
        :param type_vector: [('MERGER & ACQUISTION AGREEMENT', 0.16), ('UNKNOWN', 0.15), ...
        :param min_prob: most probable ([0]) vector's value should be >= min_prob
        :param max_closest_prob_percent: the second ([1]) vector's value should be <=
                                         type_vector * X / 100%
        :param unknown_category: what value we return if either of both checks failed
        :return: unknown_category or type_vector[0] title
        """
        items = list(type_vector.items())
        if not items:
            return unknown_category
        if items[0][1] < min_prob:
            return unknown_category
        closest_prob = 0 if len(items) < 2 else items[1][1]
        if closest_prob > items[0][1] * max_closest_prob_percent / 100:
            return unknown_category
        return items[0][0]

    def detect_contract_type_vector(self, document_text: str) -> pd.Series:
        if not self.rf_model or not self.d2v_model:
            raise RuntimeError('The class is not initialized')
        class_prob = self.rf_model.predict_proba([self.d2v_model.infer_vector(
            self.process_document(document_text))])
        return pd.Series(class_prob[0], index=self.rf_model.classes_).sort_values(ascending=False).head()

    @classmethod
    def process_document(cls, document_text: str):
        return [t for t in get_token_list(document_text, stopword=True, lowercase=True) if t.isalpha()]
