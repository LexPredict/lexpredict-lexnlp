"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
from typing import Callable, Generator, Iterable, Tuple

# LexNLP
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation


class Normalizer:
    """
    Searches for and replaces substrings in input text.

    Example:

        >>> from lexnlp.ml.normalizers import Normalizer
        >>> normalizer: Normalizer = Normalizer(
        ...     normalizations=(
        ...         (get_ratio_annotations, '__RATIO__'),
        ...         (get_date_annotations, '__DATE__'),
        ...         (get_percent_annotations, '__PERCENT__'),
        ...         (get_amount_annotations, '__AMOUNT__'),
        ...     ),
        ... )
        >>> normalizer(text='7% is due on 2022-01-01')
        '__PERCENT__ is due on __DATE__'
    """

    def __init__(
        self,
        normalizations: Iterable[Tuple[Callable[[str], Generator[TextAnnotation, None, None]], str]],
    ) -> None:
        """

        Args:
            normalizations (Iterable[Tuple[Callable[[str], Generator[TextAnnotation, None, None]], str]]):

        """
        self.normalizations = normalizations

    def __call__(self, text) -> str:
        for function, replacement in self.normalizations:
            # Note: adding whitespace to the replacement ensures proper tokenization later
            text: str = ''.join(self._find_replace(text, function, f' {replacement.strip()} '))
        return text

    @classmethod
    def _find_replace(
        cls,
        text: str,
        function: Callable[[str], Generator[TextAnnotation, None, None]],
        replacement: str,
    ) -> Generator[str, None, None]:
        i: int = 0
        try:
            for annotation in function(text):  # type: TextAnnotation
                len_left_strip, len_right_strip = cls._get_strip_offsets(annotation.text)
                start, end = annotation.coords
                start += len_left_strip
                end -= len_right_strip
                yield text[i:start]
                yield replacement
                i: int = end
            yield text[i:]
        except Exception:
            yield text

    @staticmethod
    def _get_strip_offsets(text: str) -> Tuple[int, int]:
        """
        Args:
            text (str):

        Returns:
            A tuple of offsets with whitespace remove
        """
        length_original: int = len(text)
        length_left_strip: int = length_original - len(text.lstrip())
        length_right_strip: int = length_original - len(text.rstrip())
        return length_left_strip, length_right_strip
