__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import gzip
import os
import pickle
from abc import abstractmethod
from typing import Any, Tuple, Generator, List

from lexnlp.utils.unpickler import renamed_load

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))


class BaseTokenSequenceClassifierModel:
    """
    Base classifier class for generic text sequence objects.
    """

    unicode_character_categories = pickle.load(
        open(os.path.join(MODULE_PATH, 'data/unicode_character_categories.pickle'), 'rb'))
    unicode_character_category_mapping = pickle.load(
        open(os.path.join(MODULE_PATH, 'data/unicode_character_category_mapping.pickle'), 'rb'))
    unicode_character_top_category_mapping = pickle.load(
        open(os.path.join(MODULE_PATH, 'data/unicode_character_top_category_mapping.pickle'), 'rb'))
    unicode_top_category_set = set(unicode_character_top_category_mapping.values())
    unicode_category_set = set(unicode_character_category_mapping.values())

    @staticmethod
    # pylint: disable=unused-argument
    def get_classifier(
            use_spacy: bool,
            letter_set=None, digit_set=None, punc_set=None, symbol_set=None, match_tokens=None,
            pre_window=0, post_window=0, calculate_sum=False, normalize=False, string_checks=False):
        init_args = dict(locals())
        del init_args['use_spacy']
        from lexnlp.extract.ml.classifier.spacy_token_sequence_model import SpacyTokenSequenceClassifierModel
        from lexnlp.extract.ml.classifier.token_sequence_model import TokenSequenceClassifierModel
        return SpacyTokenSequenceClassifierModel(**init_args) if use_spacy \
            else TokenSequenceClassifierModel(**init_args)

    # pylint: disable=unused-argument
    def __init__(self, letter_set=None, digit_set=None, punc_set=None, symbol_set=None, match_tokens=None,
                 pre_window=0, post_window=0, calculate_sum=False, normalize=False, string_checks=False):
        # store init arguments for saving model
        init_args = dict(locals())
        del init_args['self']
        self.init_args = (type(self), init_args)
        # Classifier parameters
        self.letter_set = letter_set if letter_set else []
        self.digit_set = digit_set if digit_set else []
        self.punc_set = punc_set if punc_set else []
        self.symbol_set = symbol_set if symbol_set else []
        self.match_tokens = match_tokens if match_tokens else []
        self.pre_window = pre_window
        self.post_window = post_window
        self.calculate_sum = calculate_sum
        self.normalize = normalize
        self.string_checks = string_checks

        # "Private" class variables
        self.model = None
        self.feature_list = self.get_feature_list(self.letter_set, self.digit_set,
                                                  self.punc_set, self.symbol_set,
                                                  self.pre_window, self.post_window)
        self._feature_index_map = {f: i for i, f in enumerate(self.feature_list)}
        self._base_feature_list = [f[2:] for f in self.feature_list if f.startswith('0_')]

    def save_in_file(self, save_path: str):
        with open(save_path, 'wb') as fw:
            pickle.dump(self, fw)

    def save_in_file_compressed(self, save_path: str):
        with gzip.GzipFile(save_path, 'w') as fw:
            pickle.dump(self, fw)

    @staticmethod
    def load_from_file(save_path: str):
        with open(save_path, 'rb') as fr:
            model = renamed_load(fr)
        return model

    @staticmethod
    def load_from_file_compressed(save_path: str):
        with gzip.GzipFile(save_path, 'r') as fr:
            model = pickle.load(fr)
        return model

    @staticmethod
    def load_from_stream(stream: Any):
        model = pickle.load(stream)
        return model

    @abstractmethod
    def get_feature_list(self, letter_set=None, digit_set=None, punc_set=None, symbol_set=None,
                         pre_window=None, post_window=None):
        raise NotImplementedError('get_feature_list() should be implemented in derived class')

    @abstractmethod
    def get_feature_data(self, text: str, feature_mask: List[int] = None):
        raise NotImplementedError('get_feature_data() should be implemented in derived class')

    def train_model(self, model, feature_data, target_data):
        """
        Train a model and set into class.
        """
        self.model = model.fit(feature_data, target_data)

    def run_model(self, text: str, outer_class=0,
                  start_class=1, inner_class=2, end_class=3, strict=True,
                  feature_mask: List[int] = None)\
            -> Generator[Tuple[int, int], None, None]:
        """
        Run model on text
        """

        feature_data, tokens = self.get_feature_data(text, feature_mask)
        predicted_class = self.model.predict(feature_data)
        start_pos = -1

        for i in range(0, predicted_class.shape[0]):
            if predicted_class[i] == start_class and start_pos == -1:
                start_pos = i
            elif predicted_class[i] == end_class:
                if strict:
                    if start_pos >= 0:
                        yield (tokens[start_pos][0], tokens[i][1])
                        start_pos = -1
                else:
                    yield (tokens[start_pos][0], tokens[i][1])
                    start_pos = -1
            elif predicted_class[i] == inner_class and start_pos == -1:
                start_pos = i
            elif predicted_class[i] == outer_class and start_pos > -1:
                if not strict:
                    yield (tokens[start_pos][0], tokens[i][1])
                start_pos = -1
