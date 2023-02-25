__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Callable, Tuple


@dataclass
class TokenPosTagAdjustment:
    """
    A condition-based transformation rule for converting nltk.tag.pos_tags output.
    If both `from` callables return True, then the `to` callables are applied.

    Args:
        from_token(Callable): filter condition on the input token,
            defaults to `lambda token: True`
        from_pos(Callable): filter condition on the input POS,
            defaults to `lambda pos: True`
        to_token(Callable): transformation for the output token,
            defaults to `lambda token: token`
        to_pos(Callable): transformation for the output POS,
            defaults to `lambda pos: pos`

    Example:
        ```
        token_pos_tag_adjustments: Tuple[TokenPosTagAdjustment] = (
            TokenPosTagAdjustment(
                from_token=lambda _t: _t == 'inc.' or _t == 'inc',
                from_pos=lambda _p: _p == 'NN',
                to_token=lambda _t: _t,
                to_pos=lambda _p: 'NNP'
            ),
        )
        pos_tokens = nltk.tag.pos_tag(tokens)
        for adjustment in self.token_pos_tag_adjustments:
            pos_tokens = [*map(adjustment, pos_tokens)]
        ```
    """
    from_token: Callable = lambda token: True
    from_pos: Callable = lambda pos: True
    to_token: Callable = lambda token: token
    to_pos: Callable = lambda pos: pos

    def __call__(self, token_pos: Tuple[str, str]) -> Tuple[str, str]:
        """
        Args:
            token_pos: a tuple of (token, pos);
                usually an element from the output from nltk.tags.pos_tags()

        Returns:
            A tuple of (token, pos)
        """
        token, pos = token_pos
        if self.from_token(token) and self.from_pos(pos):
            return self.to_token(token), self.to_pos(pos)
        return token_pos
