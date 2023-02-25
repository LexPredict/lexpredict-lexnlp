__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DetectingSettings:
    def __init__(self,
                 use_spacy: bool = False,
                 pre_window: int = 0,
                 post_window: int = 0,
                 model_type: str = 'random_forest'):
        """
        :param use_spacy: Whether to use spacy to train
        :param pre_window: Number of characters prior to include
        :param post_window: Number of characters after to include
        :param model_type: Classifier mode type
        """
        self.use_spacy = use_spacy
        self.pre_window = pre_window
        self.post_window = post_window
        self.model_type = model_type

    def __repr__(self):
        return f'use_spacy={self.use_spacy}, pre_window={self.pre_window}, ' +\
            f'post_window={self.post_window}, model_type={self.model_type}'
