"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
from os import PathLike
from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Union

# third-party imports
from numpy import fromiter, ndarray
from gensim.models.doc2vec import Doc2Vec


class Vectorizer(ABC):

    @abstractmethod
    def vectorize(self, tokens) -> ndarray:
        raise NotImplementedError


class VectorizerKeywordSearch(Vectorizer):
    """
    Searches an iterable of strings for an exact matches of keywords.
    If a keyword is in the iterable of elements, then its positive value is returned
    (index=1). Otherwise, the negative value is returned.

    Example:

        tokens = ['a', 'b', 'c', 'e', 'f']

        keywords = [('d', 1.0, 0.0), ('f', 1.0, 0.0)]

        vectorize(tokens) => array([0.0, 1.0])
    """

    def __init__(self, keywords: Iterable[Tuple[str, float, float]]) -> None:
        """
        Args:
            keywords (Iterable[Tuple[str, float, float]]):
                An iterable of tuples in the form of (keyword, value_if_present, value_if_absent).
                Example: ('keyword', 1.0, 0.0)
        """
        self.keywords: Tuple[Tuple[str, float, float]] = tuple(keywords)

    def vectorize(self, tokens: Iterable[str]) -> ndarray:
        return fromiter(
            iter=(
                value_present if keyword in tokens else value_absent
                for keyword, value_present, value_absent in self.keywords
            ),
            dtype=float,
            count=len(self.keywords),
        )


class VectorizerDoc2Vec(Vectorizer):
    """
    Vectorizes an iterable of strings using a Gensim Doc2Vec language model.
    """

    def __init__(self, doc2vec: Union[Doc2Vec, PathLike]) -> None:
        self.doc2vec: Doc2Vec = self._load_doc2vec(doc2vec)

    @staticmethod
    def _load_doc2vec(doc2vec: Union[Doc2Vec, PathLike]) -> Doc2Vec:
        """
        Args:
            doc2vec (Union[Doc2Vec, PathLike]):
                An instantiated Gensim Doc2Vec language model, or a file path
                to be passed to `Doc2Vec.load(...)`.

        Returns:
            An instantiated Gensim Doc2Vec language model.

        Raises:
            ValueError if a Gensim Doc2Vec language model cannot be returned.
        """
        if isinstance(doc2vec, Doc2Vec):
            return doc2vec
        elif isinstance(doc2vec, PathLike):
            return Doc2Vec.load(doc2vec)
        else:
            raise ValueError

    def vectorize(self, tokens) -> ndarray:
        return self.doc2vec.infer_vector(doc_words=tokens)
