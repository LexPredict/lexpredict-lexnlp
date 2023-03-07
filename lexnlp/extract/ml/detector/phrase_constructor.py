__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from enum import Enum

from typing import Tuple, Generator, List


class PhraseConstructorMethod(Enum):
    by_class = 1
    by_score = 2


class PhraseTokenClasses:
    def __init__(self,
                 outer_class: int = 0,
                 start_class: int = 1,
                 inner_class: int = 2,
                 end_class: int = 3):
        self.outer_class = outer_class
        self.start_class = start_class
        self.inner_class = inner_class
        self.end_class = end_class


class PhraseConstructorSettings:
    def __init__(self,
                 method: PhraseConstructorMethod = PhraseConstructorMethod.by_class,
                 strict: bool = False,
                 max_zeros: int = 2,
                 min_token_score: int = 2):
        self.method = method
        self.strict = strict
        self.max_zeros = max_zeros
        self.min_token_score = min_token_score

    def __repr__(self):
        if self.method == PhraseConstructorMethod.by_class:
            return f'by class, strict={self.strict}'
        return f'by score, min_score={self.min_token_score}, max_zeros={self.max_zeros}'


class PhraseConstructor:
    """
    Join "empty", "start", "middle" and "end" tokens
    into phrases.
    """

    DEFAULT_TOKEN_CLASSES = PhraseTokenClasses()

    DEFAULT_CONSTRUCTOR_SETTINGS = PhraseConstructorSettings()

    @staticmethod
    def join_tokens(tokens,
                    predicted_class,
                    feature_mask: List[int] = None,
                    settings: PhraseConstructorSettings = None,
                    token_classes: PhraseTokenClasses = None) -> Generator[Tuple[int, int], None, None]:
        settings = settings or PhraseConstructor.DEFAULT_CONSTRUCTOR_SETTINGS
        if settings.method == PhraseConstructorMethod.by_class:
            yield from PhraseConstructor.join_tokens_by_class(
                tokens, predicted_class, strict=settings.strict, token_classes=token_classes)
            return

        yield from PhraseConstructor.join_tokens_by_score(
            tokens,
            predicted_class,
            feature_mask=feature_mask,
            min_token_score=settings.min_token_score,
            max_zeros=settings.max_zeros,
            token_classes=token_classes)

    @staticmethod
    def join_tokens_by_class(
            tokens,
            predicted_class,
            strict: bool = False,
            token_classes: PhraseTokenClasses = None) -> Generator[Tuple[int, int], None, None]:
        """
        Run model on text
        """
        token_classes = token_classes or PhraseConstructor.DEFAULT_TOKEN_CLASSES
        outer_class, start_class, inner_class, end_class = (
            token_classes.outer_class, token_classes.start_class,
            token_classes.inner_class, token_classes.end_class)
        start_pos = -1

        for i in range(0, predicted_class.shape[0]):
            if predicted_class[i] == start_class and start_pos == -1:
                start_pos = i
            elif predicted_class[i] == end_class:
                if strict:
                    if start_pos >= 0:
                        yield min(tokens[start_pos][0], tokens[i][1]), max(tokens[start_pos][0], tokens[i][1])
                        start_pos = -1
                else:
                    yield min(tokens[start_pos][0], tokens[i][1]), max(tokens[start_pos][0], tokens[i][1])
                    start_pos = -1
            elif predicted_class[i] == inner_class and start_pos == -1:
                start_pos = i
            elif predicted_class[i] == outer_class and start_pos > -1:
                if not strict:
                    yield min(tokens[start_pos][0], tokens[i][1]), max(tokens[start_pos][0], tokens[i][1])
                start_pos = -1

    @staticmethod
    def join_tokens_by_score(
            tokens,
            predicted_class,
            feature_mask: List[int] = None,
            max_zeros: int = 2,
            min_token_score: int = 2,
            token_classes: PhraseTokenClasses = None) -> Generator[Tuple[int, int], None, None]:
        """
        Run model on text
        """
        token_classes = token_classes or PhraseConstructor.DEFAULT_TOKEN_CLASSES
        outer_class, start_class, inner_class, end_class = (
            token_classes.outer_class, token_classes.start_class,
            token_classes.inner_class, token_classes.end_class)

        i = -1
        while i < predicted_class.shape[0] - 1:
            i += 1
            if predicted_class[i] == start_class or predicted_class[i] == inner_class:
                token_start = i
                token_end = i
                zeros = 0
                token_score = 1 if predicted_class[i] == start_class else 0
                has_inner_tokens = False
                for j in range(i + 1, predicted_class.shape[0]):
                    if predicted_class[j] == inner_class:
                        token_end = j
                        has_inner_tokens = True
                        continue
                    if predicted_class[j] == outer_class:
                        zeros += 1
                        if zeros > max_zeros:
                            i = j
                            break
                    if predicted_class[j] == end_class:
                        token_score += 1
                        token_end = j
                        i = j
                        break
                    if predicted_class[j] == start_class:
                        i = j - 1  # continue right where stopped
                        break
                if has_inner_tokens:
                    token_score += 1

                word_start = tokens[token_start][0]
                word_end = tokens[token_end][1]
                if feature_mask:
                    for f in feature_mask[word_start: word_end]:
                        if f:
                            token_score += 1
                            break

                if token_score >= min_token_score:
                    yield tokens[token_start][0], tokens[token_end][1]
