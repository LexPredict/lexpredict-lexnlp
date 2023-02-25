__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Gensim
from gensim import __version__ as version_gensim
from gensim.models import Doc2Vec
from gensim.models.callbacks import CallbackAny2Vec


class DummyGensimKeyedVectors:
    """
    Used as a substitute for Gensim's `KeyedVectors`; useful for reducing file size.

    Note: models must be saved with `cloudpickle`,
    or DummyGensimKeyedVectors must be imported before a model loaded from disk.

    Example:
        >>> import cloudpickle
        ... doc2vec_model: Doc2Vec = ...
        ... # replace the `KeyedVectors` to reduce serialization size.
        ... doc2vec_model.dv = DummyGensimKeyedVectors(doc2vec_model.vector_size)
        ... # now the model is much, much smaller and can be efficiently saved.
        ... with open('./model.doc2vec', 'wb') as f:
        ...     cloudpickle.dump(doc2vec_model, f)
    """

    def __init__(self, vector_size: int):
        self.vector_size: int = vector_size

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError as attribute_error:
            raise AttributeError('This is a DummyDV!') from attribute_error


class TrainingCallback(CallbackAny2Vec):
    """
    Used for printing Gensim training information.

    Examples:

        >>> from gensim.models import Doc2Vec
        ... doc2vec_model = Doc2Vec(
        ...    callbacks=(TrainingCallback(),)
        ...    ...,
        ... )

    References:
        https://radimrehurek.com/gensim/models/callbacks.html
    """

    def __init__(self) -> None:
        """
        """
        self.completed_epochs: int = 0
        self.epoch: int = 0

    def on_epoch_begin(self, model: Doc2Vec) -> None:
        """
        Called at the start of each training epoch.
        """
        self.epoch += 1
        print(f'Started epoch {self.epoch} / {model.epochs}')

    def on_epoch_end(self, model: Doc2Vec) -> None:
        """
        Called at the end of each training epoch.

        Take note if we want to compute and log loss:
        https://stackoverflow.com/a/58188779/4189676
        https://stackoverflow.com/a/56085717/4189676
        https://datascience.stackexchange.com/a/81926
        """
        print(
            f'...[Epoch {self.epoch} |'
            f' total_train_time: {model.total_train_time}]'
        )
        self.completed_epochs += 1

    def on_train_begin(self, model: Doc2Vec) -> None:
        """
        Called at the start of the training process.
        """
        print('Started training...')
        print(
            f'Gensim version: {version_gensim}, '
            f'{model.vector_size=}, '
            f'{model.window=}, '
            f'{model.min_count=}, '
            f'{model.dm=}'
        )

    def on_train_end(self, model: Doc2Vec) -> None:
        """
        Called at the start of the training process.
        """
        print('Ended training.')
