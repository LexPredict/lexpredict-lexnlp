"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
from typing import Generator, Iterable, List, Optional, Union, Tuple

# LexNLP
from lexnlp.ml.normalizers import Normalizer
from lexnlp.ml.vectorizers import Vectorizer
from lexnlp.nlp.en.tokens import get_lemmas
from lexnlp.nlp.en.segments.sentences import get_sentences

# third-party imports
from joblib import delayed, Parallel
from scipy.sparse import issparse, vstack
from numpy import ceil, concatenate, ndarray
from sklearn.base import BaseEstimator, TransformerMixin


# -----------------------------------------------------------------------------
# Parallelization Utility Functions
# -----------------------------------------------------------------------------


def _predict(estimator, X, method: str, start: int, stop: int):
    return getattr(estimator, method)(X[start:stop])


def parallel_estimator(
    estimator,
    X,
    method: str,
    n_jobs: int = 1,
    batches_per_job: int = 10,  # TODO: what is the optimal value?
) -> ndarray:
    """
    Permits parallel execution of some Scikit-Learn operations.

    Args:
        estimator:
        X:
        method (str):
        n_jobs (int=1):
        batches_per_job (int=10):

    Returns:

    """
    n_samples: int = len(X)
    batch_size = int(ceil(n_samples / (batches_per_job * n_jobs)))
    parallel = Parallel(n_jobs=n_jobs)
    results = parallel(
        delayed(_predict)(estimator, X, method, i, i + batch_size)
        for i in range(0, n_samples, batch_size)
    )
    if issparse(results[0]):
        return vstack(results)
    return concatenate(results)


# -----------------------------------------------------------------------------
# Scikit-Learn Transformers for usage in Scikit-Learn Pipelines
# -----------------------------------------------------------------------------
class TransformerVectorizer(BaseEstimator, TransformerMixin):
    """
    """
    def __init__(self, vectorizers: Iterable[Vectorizer]) -> None:
        """
        Successively transforms X using each Vectorizer, concatenating their outputs.

        Args:
            vectorizers (Iterable[Vectorizer]):
                An iterable of Vectorizers which will vectorize X.
        """
        self.vectorizers: Tuple[Vectorizer] = tuple(vectorizers)

    # noinspection PyPep8Naming
    def fit(self, X, y: Optional = None) -> 'TransformerVectorizer':
        return self

    # noinspection PyPep8Naming
    def transform(self, X, y: Optional = None) -> Tuple[ndarray, ...]:
        vectors: List[ndarray] = []
        for document in X:  # type: str
            vector: ndarray = concatenate(
                [
                    vectorizer.vectorize(document.split())
                    for vectorizer in self.vectorizers
                ],
                axis=0,
            )
            vectors.append(vector)
        return tuple(vectors)


class TransformerPreprocessor(BaseEstimator, TransformerMixin):
    """
    Preprocesses X using a `Normalizer`.
    """

    def __init__(self, normalizer: Normalizer, head_character_n: int = 0) -> None:
        """
        Args:
            normalizer (Normalizer):
                An instantiated Normalizer for substring replacement.

            head_character_n (int=0):
                An integer equal to or greater than zero.
                Sentence segments will be streamed from input text until the
                sum of their lengths equals or exceeds head_character_n. If
                head_character_n is 0, then this limit is ignored. Values less
                than 0 will throw a ValueError.

        """
        self.normalizer: Normalizer = normalizer
        if head_character_n < 0:
            raise ValueError(
                f'`head_character_n` must be equal to or greater than 0.'
                f' Received: {head_character_n}'
            )
        self.head_character_n: int = head_character_n

    def _sentence_counter(self, sentences: Iterable[str]) -> Generator[str, None, None]:
        character_count: int = 0
        for sentence in sentences:
            character_count += len(sentence)
            yield sentence
            if character_count >= self.head_character_n:
                break

    def _handle_block_text(self, text: str) -> Generator[str, None, None]:
        if self.head_character_n > 0:
            text: Generator[str, None, None] = get_sentences(text)
            yield from self._sentence_counter(text)
        else:
            yield from get_sentences(text)

    def preprocess(self, text: Union[str, Iterable[str]]) -> str:
        """
        Args:
            text (Union[str, Iterable[str]]):
                A string to preprocess. Alternatively, input can be a list of
                strings which, when concatenated, represent the entirety of a
                document.

        Returns:
            A preprocessed string.
        """
        document: List[str] = []

        if isinstance(text, str):
            text: Generator[str, None, None] = self._handle_block_text(text)
        else:
            if self.head_character_n > 0:
                text: Generator[str, None, None] = self._sentence_counter(text)

        # strangely, functions passed to the Normalizer perform poorly on individual sentences.
        # ...instead, we concatenate sentences into one string and then split again on newlines after normalization.
        text: List[str] = self.normalizer('\n'.join(text)).split('\n')

        for sentence in text:
            lemmas: str = ' '.join(
                get_lemmas(
                    sentence,
                    stopword=True,
                    lowercase=True,
                )
            )
            document.append(lemmas)
        return ' '.join(document)

    # noinspection PyPep8Naming
    def fit(self, X, y: Optional = None) -> 'TransformerPreprocessor':
        return self

    # noinspection PyPep8Naming
    def transform(self, X, y: Optional = None) -> Tuple[str, ...]:
        return tuple(
            self.preprocess(text)
            for text in X  # type: Union[str, Iterable[str]]
        )
