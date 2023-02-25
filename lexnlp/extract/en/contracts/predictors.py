"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
from typing import Iterable, Tuple, Union

# third-party imports
from numpy import ndarray
from pandas import Series

# LexNLP
from lexnlp.ml.predictor import ProbabilityPredictor


class ProbabilityPredictorIsContract(ProbabilityPredictor):
    """
    Uses a Scikit-Learn Pipeline to classify textual input as is/is-not a contract.
    """

    _DEFAULT_PIPELINE: str = 'pipeline/is-contract/0.1'

    def _sanity_check(self) -> None:
        """
        Ensures that the classifier makes binary predictions.
        """
        if len(self.pipeline.classes_) != 2:
            raise ValueError

    def is_contract(
        self,
        text: str,
        min_probability: float = 0.5,
        return_probability: bool = False,
    ) -> Union[bool, Tuple[bool, float]]:
        """
        Determines whether text is a contract.

        Args:
            text (str):
                The text to classify as a contract.

            min_probability (float=0.5):
                The minimum predicted probability required to be considered a
                positive sample (a contract).

            return_probability (bool=False):
                Whether to return the predicted probability alongside the
                classification.

        Returns:
            Whether the text is a contract; optionally with a probability score.
        """
        predicted_probability: float = self.pipeline.predict_proba(X=(text,))[0, 1]
        classification: bool = predicted_probability >= min_probability

        if return_probability:
            return classification, predicted_probability
        return classification


class ProbabilityPredictorContractType(ProbabilityPredictor):
    """
    Uses a Scikit-Learn Pipeline to classify textual input as a type of contract.
    """

    _DEFAULT_PIPELINE: str = 'pipeline/contract-type/0.1'

    def _sanity_check(self) -> None:
        """
        Does nothing. No sanity check required.
        """

    def make_predictions(
        self,
        text: Union[str, Iterable[str]],
        top_n: int = 2,
    ) -> Series:
        """
        Args:
            text (str):
                The contract text to classify.

            top_n (int=2):
                The number of predictions to return.

        Returns:
            A descendingly-sorted Pandas Series containing with contract classes
            and the predicted probability for each respective class.

            Example:
                [('MERGER & ACQUISITION AGREEMENT', 0.46), ('UNKNOWN', 0.15), ...]
        """
        predicted_probabilities: ndarray = self.pipeline.predict_proba(X=(text,))[0]
        predictions: Series = Series(
            data=predicted_probabilities,
            index=self.pipeline.classes_,
        )
        predictions.sort_values(ascending=False, inplace=True)
        return predictions.head(n=top_n)

    @staticmethod
    def infer_classification(
        predictions: Series,
        min_probability: float = 0.15,
        max_closest_probability: float = 0.75,
        unknown_classification: str = '',
    ) -> str:
        """
        Args:
            predictions (Series[str, float]):
                A descendingly-sorted Pandas Series containing with contract
                classes and the predicted probability for each respective class.

            min_probability (float=0.15):
                The minimum predicted probability required to be considered a
                positive sample.

            max_closest_probability (float=0.75):
                The second-highest prediction probability must be this less than
                the highest prediction probability multiplied by this value.

                That is, if `predictions[1] > (predictions[0] * max_closest_probability)`,
                then the `unknown_classification` will be returned.

            unknown_classification (str=''):
                The string to return when the contract type classification is
                unknown.

        Returns:
            The string name of a contract type classification.
        """
        if predictions.empty:
            return unknown_classification

        if predictions[0] < min_probability:
            return unknown_classification

        next_closest_probability: float = 0.0 if len(predictions) < 2 else predictions[1]
        if next_closest_probability > (predictions[0] * max_closest_probability):
            return unknown_classification

        return predictions.index[0]

    def detect_contract_type(
        self,
        text: Union[str, Iterable[str]],
        min_probability: float = 0.15,
        max_closest_probability: float = 0.75,
        unknown_classification: str = '',
    ) -> str:
        """
        Assigns text a contract type classification.

        Args:
            text (str):
                The contract text to classify.

            min_probability (float=0.15):
                The minimum predicted probability required to be considered a
                positive sample.

            max_closest_probability (float=0.75):
                The second-highest prediction probability must be this less than
                the highest prediction probability multiplied by this value.

                That is, if `predictions[1] > (predictions[0] * max_closest_probability)`,
                then the `unknown_classification` will be returned.

            unknown_classification (str=''):
                The string to return when the contract type classification is
                unknown.

        Returns:
            The string name of a contract type classification.
        """
        predictions: Series = self.make_predictions(text, top_n=2)
        prediction: str = self.infer_classification(
            predictions=predictions,
            min_probability=min_probability,
            max_closest_probability=max_closest_probability,
            unknown_classification=unknown_classification,
        )
        return prediction
