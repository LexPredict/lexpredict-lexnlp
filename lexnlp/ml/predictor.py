"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, runtime_checkable

# third-party imports
from cloudpickle import load
from sklearn.pipeline import Pipeline
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

# LexNLP
from lexnlp.ml.catalog import get_path_from_catalog


@runtime_checkable
class ScikitLearnHasPredictProba(Protocol):
    """
    Permits structural subtyping. Used for type-checking to ensure that
    classifiers implement a `predict_proba(self, X)` method.

    TODO: investigate if we can also imply inheritance from sklearn.base.BaseEstimator
    """
    classes_: list

    # noinspection PyPep8Naming
    def predict_proba(self, X) -> Any: ...


@runtime_checkable
class PipelinePredictProba(Protocol):
    """
    Currently unused.
    """
    _final_estimator: ScikitLearnHasPredictProba


class ProbabilityPredictor(ABC):
    """
    Subclasses of ``ProbabilityPredictor`` should use a Scikit-Learn Pipeline
    to transform input and make classification predictions.

    This Abstract Base Class provides a default constructor as well as relevant
    class and abstract methods.
    """

    _DEFAULT_PIPELINE: str = NotImplemented

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls._DEFAULT_PIPELINE is NotImplemented:
            raise NotImplementedError('Class attribute `_DEFAULT_PIPELINE` not implemented.')

    # noinspection PyProtectedMember
    def __init__(self, pipeline: Optional[Pipeline] = None) -> None:
        """
        Args:
            pipeline (Optional[Pipeline]=None):
                The Scikit-Learn Pipeline used to transform input and make classification predictions.
                The default Scikit-Learn Pipeline is loaded if no Pipeline is provided.
        """
        self.pipeline: Pipeline = pipeline or self.get_default_pipeline()
        try:
            check_is_fitted(self.pipeline._final_estimator)
        except NotFittedError as not_fitted_error:
            raise ValueError(
                f'self.pipeline._final_estimator={self.pipeline._final_estimator} is not fitted.'
            ) from not_fitted_error

        if not isinstance(self.pipeline._final_estimator, ScikitLearnHasPredictProba):
            raise ValueError(
                f'self.pipeline._final_estimator of type `{type(self.pipeline._final_estimator)}`'
                f'does not follow the `ScikitLearnHasPredictProba` protocol.'
            )

        # Fix AttributeError: 'MinMaxScaler' object has no attribute 'clip'
        for _, name, transform in self.pipeline._iter(with_final=False):
            transform.clip = hasattr(transform, 'clip') and transform.clip

        self._sanity_check()

    @abstractmethod
    def _sanity_check(self) -> None:
        """
        Validate instance attributes as needed.
        """
        raise NotImplementedError

    @classmethod
    def get_default_pipeline(cls) -> Pipeline:
        """
        Gets the default Scikit-Learn Pipeline for usage with this ProbabilityPredictor.

        Returns:
            A default Scikit-Learn Pipeline for usage with this ProbabilityPredictor.
        """
        path: Path = get_path_from_catalog(cls._DEFAULT_PIPELINE)
        with open(path, 'rb') as f:
            return load(f)
