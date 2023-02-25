__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Union, Tuple

import numpy
import pandas

from lexnlp.extract.ml.detector.detecting_settings import DetectingSettings
from lexnlp.extract.ml.detector.sample_processor import process_sample, get_target_start_end_from_corgetes
from lexnlp.extract.ml.detector.artifact_detector import ArtifactDetector


class DefinitionTermDetector(ArtifactDetector):

    def process_sample(self,
                       sample_df: pandas.DataFrame,
                       build_target_data: bool = False) -> Union[numpy.ndarray, Tuple[numpy.ndarray, numpy.ndarray]]:
        return process_sample(sample_df, self.model,
                              get_target_start_end=get_target_start_end_from_corgetes,
                              column_name_formatted='labels')

    def train_and_save(self,
                       settings: DetectingSettings,
                       train_file: str,
                       train_size: int = -1,
                       save_path: str = '',
                       compress: bool = False) -> None:
        # load sample
        train_sample_df = self.read_sample_df(train_file, train_size)

        self.train_and_save_on_dataframe(settings,
                                         train_sample_df,
                                         save_path,
                                         compress)

    def train_and_save_on_dataframe(
            self,
            settings: DetectingSettings,
            train_sample_df: pandas.DataFrame,
            save_path: str = '',
            compress: bool = False) -> None:
        # setup token match strings in locale
        def_tokens = ['shall', 'includes', 'including',
                      'mean', 'meaning', 'referred', 'known',
                      'refers', 'used', 'hereby', 'interpreted',
                      'defined', 'interpreted', 'collectively',
                      'include', 'individually', 'together',
                      'being', 'foregoing', 'purpose', 'purposed']

        # create model class
        self.train_and_save_on_tokens(def_tokens, save_path,
                                      settings, train_sample_df,
                                      punc_set=":\"()",
                                      compress=compress)
