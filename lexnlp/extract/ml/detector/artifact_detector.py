__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from abc import abstractmethod
from typing import Optional, Tuple, Union, List, Any, Generator
import string

import num2words
import numpy
import pandas
import sklearn.ensemble

from lexnlp.extract.ml.classifier.base_token_sequence_classifier_model import BaseTokenSequenceClassifierModel
from lexnlp.extract.ml.detector.detecting_settings import DetectingSettings
from lexnlp.extract.ml.detector.phrase_constructor import PhraseConstructorSettings, PhraseConstructor


class ArtifactDetector:
    def __init__(self):
        self.model = None  # type: Optional[BaseTokenSequenceClassifierModel]
        self.join_token_settings = PhraseConstructorSettings()

    def load(self, file_path: str):
        self.model = BaseTokenSequenceClassifierModel.load_from_file(file_path)

    def load_compressed(self, file_path: str):
        self.model = BaseTokenSequenceClassifierModel.load_from_file_compressed(file_path)

    def load_from_stream(self, stream: Any):
        self.model = BaseTokenSequenceClassifierModel.load_from_stream(stream)

    def predict(self, sample_df: pandas.DataFrame,
                size_limit: int = 0) -> Tuple[numpy.ndarray, numpy.ndarray]:
        if size_limit:
            sample_df = sample_df.head(size_limit)
        test_feature_data, test_target_data = self.process_sample(sample_df, build_target_data=True)
        test_predicted = self.model.model.predict(test_feature_data)
        return test_predicted, test_target_data

    @abstractmethod
    def process_sample(self,
                       sample_df: pandas.DataFrame,
                       build_target_data: bool = False) -> Union[numpy.ndarray, Tuple[numpy.ndarray, numpy.ndarray]]:
        raise NotImplementedError('process_sample() should be implemented in derived class')

    def predict_text(self,
                     text: str,
                     join_settings: PhraseConstructorSettings = None,
                     feature_mask: List[int] = None) -> Generator[Tuple[int, int], None, None]:
        feature_data, tokens = self.model.get_feature_data(text, feature_mask)
        predicted_class = self.model.model.predict(feature_data)
        join_settings = join_settings or self.join_token_settings
        yield from PhraseConstructor.join_tokens(
            tokens, predicted_class, settings=join_settings, feature_mask=feature_mask)

    def train_and_save(self,
                       settings: DetectingSettings,
                       train_file: str,
                       train_size: int = -1,
                       save_path: str = '',
                       compress: bool = False) -> None:
        """
        Create a percent identification model using tokens.
        :param settings: Model settings
        :param train_file: File to load training samples from
        :param train_size: Number of records to use
        :param save_path: Output (pickle model) file path
        :param compress: Save compressed file
        """
        # load sample
        train_sample_df = self.read_sample_df(train_file, train_size)

        # setup token match strings in locale
        amount_tokens = self.build_amount_tokens()

        # create model class
        self.train_and_save_on_tokens(amount_tokens, save_path,
                                      settings, train_sample_df,
                                      compress=compress)

    def train_and_save_on_tokens(self,
                                 tokens: List[str],
                                 save_path: str,
                                 settings: DetectingSettings,
                                 train_sample_df: pandas.DataFrame,
                                 punc_set: str = ".,/-",
                                 symbol_set: Optional[str] = None,
                                 string_checks: bool = False,
                                 compress: bool = False):
        self.model = BaseTokenSequenceClassifierModel.get_classifier(
            settings.use_spacy,
            pre_window=settings.pre_window, post_window=settings.post_window,
            match_tokens=tokens, letter_set=string.ascii_letters,
            digit_set=string.digits, punc_set=punc_set, symbol_set=symbol_set,
            string_checks=string_checks)

        # build feature and target training sample
        train_feature_data, train_target_data = self.process_sample(
            train_sample_df, build_target_data=True)
        # initialize sklearn model based on request
        if settings.model_type == 'extra_trees':
            model = sklearn.ensemble.ExtraTreesClassifier(class_weight="balanced")
        elif settings.model_type == 'random_forest':
            model = sklearn.ensemble.RandomForestClassifier(class_weight="balanced")
        # train
        self.model.train_model(model, train_feature_data, train_target_data)
        if compress:
            self.save_compressed_model(save_path)
        else:
            self.save_model(save_path)

    def save_model(self, save_path: str) -> None:
        self.model.save_in_file(save_path)

    def save_compressed_model(self, save_path):
        self.model.save_in_file_compressed(save_path)

    def read_sample_df(self, train_file: str, train_size: int) -> pandas.DataFrame:
        train_sample_df = pandas.read_csv(train_file, encoding="utf-8", low_memory=False)
        if train_size > 0:
            train_sample_df = train_sample_df.head(train_size)
        return train_sample_df

    def build_amount_tokens(self) -> List[str]:
        amount_tokens = []
        for day in range(1, 101):
            amount_tokens.extend([num2words.num2words(day, to='ordinal'),
                                  num2words.num2words(day, to='ordinal').lower(),
                                  num2words.num2words(day, to='ordinal').upper(),
                                  num2words.num2words(day, to='ordinal_num'),
                                  num2words.num2words(day, to='ordinal_num').lower(),
                                  num2words.num2words(day, to='ordinal_num').upper(),
                                  ])
        amount_tokens.extend(["dozen", "million", "millionth", "billion", "billionth", "trillion", "trillionth"])
        return amount_tokens
