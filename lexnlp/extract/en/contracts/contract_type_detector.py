# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import joblib
from typing import List
from pandas import Series
from gensim.models.doc2vec import Doc2Vec
from sklearn.ensemble import RandomForestClassifier
from lexnlp.nlp.en.tokens import get_tokens


class ContractTypeDetector:
    """
    The class detects document's contract type based on plain text.
    The class has to be initialized (load_models) before using.
    """

    def __init__(
        self,
        rf_model_path: str,
        d2v_model_path: str
    ):
        """
        Args:
            rf_model_path (str):
            d2v_model_path (str):
        """
        with open(rf_model_path, "rb") as rf_model_file:
            self.rf_model: RandomForestClassifier = joblib.load(rf_model_file)
        self.d2v_model: Doc2Vec = Doc2Vec.load(d2v_model_path)

    @staticmethod
    def detect_contract_type(
        type_vector: Series,
        min_prob: float = 0.15,
        max_closest_prob_percent: int = 75,
        unknown_category: str = '',
    ) -> str:
        """
        Decides what document type (string) this is based on sorted type_vector.
        :param type_vector: [('MERGER & ACQUISTION AGREEMENT', 0.16), ('UNKNOWN', 0.15), ...
        :param min_prob: most probable ([0]) vector's value should be >= min_prob
        :param max_closest_prob_percent: the second ([1]) vector's value should be <=
                                         type_vector * X / 100%
        :param unknown_category: what value we return if either of both checks failed
        :return: unknown_category or type_vector[0] title
        """
        if type_vector.empty:
            return unknown_category

        if type_vector[0] < min_prob:
            return unknown_category

        next_closest_probability: float = 0.0 if len(type_vector) < 2 else type_vector[1]
        if next_closest_probability > (type_vector[0] * (max_closest_prob_percent/100)):
            return unknown_category

        return type_vector.index[0]

    def detect_contract_type_vector(self, document_text: str) -> Series:
        """
        """
        if not self.rf_model or not self.d2v_model:
            raise RuntimeError('The class is not initialized')
        class_prob = self.rf_model.predict_proba(
            [
                self.d2v_model.infer_vector(
                    self.process_document(document_text)
                )
            ]
        )
        return Series(class_prob[0], index=self.rf_model.classes_).sort_values(ascending=False).head()

    @classmethod
    def process_document(cls, document_text: str) -> List[str]:
        """
        """
        return [
            token for token
            in get_tokens(document_text, stopword=True, lowercase=True)
            if token.isalpha()
        ]
