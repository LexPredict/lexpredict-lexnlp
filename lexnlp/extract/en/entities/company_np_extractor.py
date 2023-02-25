# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import string
from typing import Optional

import nltk
import regex as re

from lexnlp.extract.en.entities.nltk_tokenizer import NltkTokenizer
from lexnlp.extract.en.utils import NPExtractor


class CompanyNPExtractor(NPExtractor):

    def __init__(self, grammar: Optional[str] = None):
        grammar = grammar or r"""
            NBAR:
                {<DT>?<NNP.*|JJ|POS|\(|\)|,>*<NNP.*>}  # DeTerminer, Proper Noun, Adjective, brackets, terminated by Proper Noun
            IN:
                {<CC|IN>}   # Coordinating Conjunction, Preposition/Subordinating Conjunction
            NP:
                {(<NBAR><IN>)*<NBAR><VBD>*}  # Delaver Housing Incorporated (NNP-NNP-VBD)
        """
        super().__init__(grammar)

    def get_tokenizer(self):
        orig_tokenizer = nltk.tokenize.TreebankWordTokenizer
        punctuation = list(orig_tokenizer.PUNCTUATION)
        punctuation[4] = (re.compile(r'[;@#$%]', re.UNICODE), ' \\g<0> ')
        # for case like "McDonald\'s Incorporated: Burgers" when POS tokenizer treats
        # "Incorporated:" as VBN instead of NNP and NP extractor fails to recognize such grammar
        punctuation.append((re.compile(r':'), r';'))
        # for case when apostrophe is in company name like Moody`s
        starting_quotes = [(re.compile(r'`s '), r'-ES-')] + list(orig_tokenizer.STARTING_QUOTES) + [
            (re.compile(r'-ES-'), r'`s ')]

        tokenizer = NltkTokenizer(punctuation, starting_quotes)
        return tokenizer.tokenize

    @staticmethod
    def strip_np(np):
        return np.strip(string.punctuation + string.whitespace)

    def cleanup_leaves(self, leaves):
        leaves = super().cleanup_leaves(leaves)
        leaves = [i for i in leaves if i[0] != ('a', 'DT') and i[0] != ('A', 'DT') and
                  not (i[0][1] == 'JJ' and i[0][0].islower())]
        return leaves
