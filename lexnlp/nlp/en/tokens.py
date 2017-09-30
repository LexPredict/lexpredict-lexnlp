"""Token parsing for English.

This module implements token parsing, such as tokens, stems, and lemma tokenization functionality in English.

Todo:
"""
# Imports
import os
import pickle

# NLTK imports
import nltk
from nltk.corpus import wordnet

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Stopwords
STOPWORDS = pickle.load(open(os.path.join(MODULE_PATH, "stopwords.pickle"), "rb"))

# Collocations
COLLOCATION_SIZE = 1000
BIGRAM_COLLOCATIONS = pickle.load(
    open(os.path.join(MODULE_PATH, "collocation_bigrams_{0}.pickle".format(COLLOCATION_SIZE)), "rb"))
TRIGRAM_COLLOCATIONS = pickle.load(
    open(os.path.join(MODULE_PATH, "collocation_trigrams_{0}.pickle".format(COLLOCATION_SIZE)), "rb"))

# Setup default stemmer for English
DEFAULT_STEMMER = nltk.stem.snowball.EnglishStemmer()

# Setup lemmatizers for English
DEFAULT_LEMMATIZER = nltk.stem.wordnet.WordNetLemmatizer()


def get_wordnet_pos(treebank_tag):
    """
    Return wordnet POS object from Treebank POS tag.
    :param treebank_tag:
    :return:
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def get_token_generator(text, lowercase=False, stopword=False):
    """
    Get token generator from text.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    if stopword:
        for token in nltk.word_tokenize(text):
            if token.lower() in STOPWORDS:
                continue
            if lowercase:
                yield token.lower()
            else:
                yield token
    else:
        for token in nltk.word_tokenize(text):
            if lowercase:
                yield token.lower()
            else:
                yield token


def get_tokens(text, lowercase=False, stopword=False):
    """
    Get token list from text.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    return list(get_token_generator(text, lowercase=lowercase, stopword=stopword))


def get_stem_generator(text, lowercase=False, stopword=False, stemmer=DEFAULT_STEMMER):
    """
    Get stems from text.
    N.B.: when stemmer is SnowballStemmer, lowercase is always returned no matter the parameter.
    :param text:
    :param lowercase:
    :param stopword:
    :param stemmer:
    :return:
    """
    for token in get_token_generator(text, lowercase=lowercase, stopword=stopword):
        yield stemmer.stem(token)


def get_stems(text, lowercase=False, stopword=False, stemmer=DEFAULT_STEMMER):
    """
    Get stems materialized from text.
    N.B.: when stemmer is SnowballStemmer, lowercase is always returned no matter the parameter.

    :param text:
    :param lowercase:
    :param stopword:
    :param stemmer:
    :return:
    """
    return list(get_stem_generator(text, lowercase=lowercase, stopword=stopword, stemmer=stemmer))


def get_lemma_generator(text, lowercase=False, stopword=False, lemmatizer=DEFAULT_LEMMATIZER):
    """
    Get lemmas from text.
    :param text:
    :param lowercase:
    :param stopword:
    :param lemmatizer:
    :return:
    """
    tokens = get_tokens(text, lowercase=False, stopword=False)
    pos = nltk.pos_tag(tokens)

    if stopword:
        for i in range(len(tokens)):
            token = pos[i][0]
            wn_pos = get_wordnet_pos(pos[i][1])

            if token.lower() in STOPWORDS:
                continue

            if lowercase:
                yield lemmatizer.lemmatize(token, wn_pos).lower() if wn_pos else lemmatizer.lemmatize(token).lower()
            else:
                yield lemmatizer.lemmatize(token, wn_pos) if wn_pos else lemmatizer.lemmatize(token)
    else:
        for i in range(len(tokens)):
            token = pos[i][0]
            wn_pos = get_wordnet_pos(pos[i][1])

            if lowercase:
                yield lemmatizer.lemmatize(token, wn_pos).lower() if wn_pos else lemmatizer.lemmatize(token).lower()
            else:
                yield lemmatizer.lemmatize(token, wn_pos) if wn_pos else lemmatizer.lemmatize(token)


def get_lemmas(text, lowercase=False, stopword=False, lemmatizer=DEFAULT_LEMMATIZER):
    """
    Get lemmas materialized from text.
    """
    return list(get_lemma_generator(text, lowercase=lowercase, stopword=stopword, lemmatizer=lemmatizer))


def get_verbs(text, lowercase=False, lemmatize=False):
    """
    Get only verbs from text.
    """
    tokens = get_tokens(text)
    pos = nltk.pos_tag(tokens)
    verb_index = [i for i in range(len(pos)) if pos[i][1].startswith("V")]
    if lemmatize:
        lemmas = get_lemmas(text, lowercase=lowercase)
        return [lemmas[j] for j in verb_index]
    else:
        return [tokens[j].lower() if lowercase else tokens[j] for j in verb_index]


def get_nouns(text, lowercase=False, lemmatize=False):
    """
    Get only nouns from text.
    """
    tokens = get_tokens(text)
    pos = nltk.pos_tag(tokens)
    verb_index = [i for i in range(len(pos)) if pos[i][1].startswith("N")]
    if lemmatize:
        lemmas = get_lemmas(text, lowercase=lowercase)
        return [lemmas[j] for j in verb_index]
    else:
        return [tokens[j].lower() if lowercase else tokens[j] for j in verb_index]


def get_adverbs(text, lowercase=False, lemmatize=False):
    """
    Get only nouns from text.
    """
    tokens = get_tokens(text)
    pos = nltk.pos_tag(tokens)
    verb_index = [i for i in range(len(pos)) if pos[i][1].startswith("RB")]
    if lemmatize:
        lemmas = get_lemmas(text, lowercase=lowercase)
        return [lemmas[j] for j in verb_index]
    else:
        return [tokens[j].lower() if lowercase else tokens[j] for j in verb_index]


def get_adjectives(text, lowercase=False, lemmatize=False):
    """
    Get only nouns from text.
    """
    tokens = get_tokens(text)
    pos = nltk.pos_tag(tokens)
    verb_index = [i for i in range(len(pos)) if pos[i][1].startswith("JJ")]
    if lemmatize:
        lemmas = get_lemmas(text, lowercase=lowercase)
        return [lemmas[j] for j in verb_index]
    else:
        return [tokens[j].lower() if lowercase else tokens[j] for j in verb_index]
