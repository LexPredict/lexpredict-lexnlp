"""Stanford parsing methods for English.

This module implements an interface to Stanford parsing methods for English, including token and parts of speech.

Todo:
"""

# Imports
import os

# NLTK imports
from nltk.tag import StanfordPOSTagger
from nltk.tokenize import StanfordTokenizer

# Project imports
from lexnlp import is_stanford_enabled
from lexnlp.nlp.en.tokens import STOPWORDS, get_lemmas
from lexnlp.config.stanford import STANFORD_POS_PATH

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Setup Stanford POS configuration
STANFORD_POS_FILE = os.path.join(STANFORD_POS_PATH, "stanford-postagger.jar")
STANFORD_TOKENIZER = StanfordTokenizer(path_to_jar=STANFORD_POS_FILE)
STANFORD_DEFAULT_TAG_MODEL = os.path.join(STANFORD_POS_PATH, "models", "english-bidirectional-distsim.tagger")
STANFORD_TAGGER = StanfordPOSTagger(STANFORD_DEFAULT_TAG_MODEL, STANFORD_POS_FILE)


def get_tokens(text, lowercase=False, stopword=False):
    """
    Get token list form text using Stanford libraries.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    if not is_stanford_enabled():
        raise RuntimeError("USE_STANFORD is set to False.  No Stanford functionality available.")

    return list(get_token_generator(text, lowercase=lowercase, stopword=stopword))


def get_token_generator(text, lowercase=False, stopword=False):
    """
    Get token generator from text using Stanford libraries.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    if not is_stanford_enabled():
        raise RuntimeError("USE_STANFORD is set to False.  No Stanford functionality available.")

    if stopword:
        for token in STANFORD_TOKENIZER.tokenize(text):
            if token.lower() in STOPWORDS:
                continue
            if lowercase:
                yield token.lower()
            else:
                yield token
    else:
        for token in STANFORD_TOKENIZER.tokenize(text):
            if lowercase:
                yield token.lower()
            else:
                yield token


def get_verbs(text, lowercase=False, lemmatize=False):
    """
    Get only verbs from text using Stanford libraries.

    :param text:
    :param lowercase:
    :param lemmatize:
    :return:
    """
    if not is_stanford_enabled():
        raise RuntimeError("USE_STANFORD is set to False.  No Stanford functionality available.")

    # Get tokens and tag
    tokens = get_tokens(text)
    pos = STANFORD_TAGGER.tag(tokens)

    verb_index = [i for i in range(len(pos)) if pos[i][1].startswith("V")]
    if lemmatize:
        lemmas = get_lemmas(text, lowercase=lowercase)
        return [lemmas[j] for j in verb_index]
    else:
        return [tokens[j].lower() if lowercase else tokens[j] for j in verb_index]


def get_nouns(text, lowercase=False, lemmatize=False):
    """
    Get only nouns from text using Stanford libraries.

    :param text:
    :param lowercase:
    :param lemmatize:
    :return:
    """
    if not is_stanford_enabled():
        raise RuntimeError("USE_STANFORD is set to False.  No Stanford functionality available.")

    # Get tokens and tag
    tokens = get_tokens(text)
    pos = STANFORD_TAGGER.tag(tokens)

    noun_index = [i for i in range(len(pos)) if pos[i][1].startswith("N")]
    if lemmatize:
        lemmas = get_lemmas(text, lowercase=lowercase)
        return [lemmas[j] for j in noun_index]
    else:
        return [tokens[j].lower() if lowercase else tokens[j] for j in noun_index]
