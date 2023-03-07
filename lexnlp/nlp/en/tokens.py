"""Token parsing for English.

This module implements token parsing, such as tokens, stems, and lemma tokenization functionality in English.

Todo:
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import pickle
import regex as re
from typing import Any, Generator, List

# NLTK imports
import nltk
from nltk.corpus import wordnet

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Stopwords
STOPWORDS = pickle.load(open(os.path.join(MODULE_PATH, "stopwords.pickle"), "rb"))

# Collocations
COLLOCATION_SIZE = 10000
BIGRAM_COLLOCATIONS = pickle.load(
    open(os.path.join(MODULE_PATH, "collocation_bigrams_{0}.pickle".format(COLLOCATION_SIZE)), "rb"))
TRIGRAM_COLLOCATIONS = pickle.load(
    open(os.path.join(MODULE_PATH, "collocation_trigrams_{0}.pickle".format(COLLOCATION_SIZE)), "rb"))

# Setup default stemmer for English
DEFAULT_STEMMER = nltk.stem.snowball.EnglishStemmer()

# Setup lemmatizers for English
DEFAULT_LEMMATIZER = nltk.stem.wordnet.WordNetLemmatizer()

# REG_WORD_TOKENIZER = re.compile(r'\s+|(\()|(\))|(\[)|(\])|(\{)|(\})')
REG_WORD_TOKENIZER = re.compile(r'(\W)')


def get_wordnet_pos(treebank_tag):
    """
    Return wordnet POS object from Treebank POS tag.
    :param treebank_tag:
    :return:
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    if treebank_tag.startswith('V'):
        return wordnet.VERB
    if treebank_tag.startswith('N'):
        return wordnet.NOUN
    if treebank_tag.startswith('R'):
        return wordnet.ADV


def get_tokens_by_regex(text: str,
                        lowercase=False,
                        preserve_line=True) -> Generator[str, Any, Any]:
    if lowercase:
        text = text.lower()
    tokens = REG_WORD_TOKENIZER.split(text)
    for token in tokens:
        wrd = token.strip()
        if not wrd:
            continue
        if not preserve_line:
            wrd = wrd.strip('.')
            if not wrd:
                continue
        yield wrd


def get_tokens(text: str, lowercase=False, stopword=False, preserve_line=True) -> Generator[str, Any, Any]:
    """
    Get token generator from text.
    :param text:
    :param lowercase:
    :param stopword:
    :param preserve_line: keep the preserve the sentence and not sentence tokenize it.
    :return:
    """
    if stopword:
        for token in nltk.word_tokenize(text, preserve_line=preserve_line):
            if token.lower() in STOPWORDS:
                continue
            if lowercase:
                yield token.lower()
            else:
                yield token
    else:
        for token in nltk.word_tokenize(text, preserve_line=preserve_line):
            if lowercase:
                yield token.lower()
            else:
                yield token


def get_token_list(text: str, lowercase: bool = False, stopword: bool = False,
                   preserve_line: bool = True) -> List:
    """
    Get token list from text.
    :param text:
    :param lowercase:
    :param stopword:
    :param preserve_line: keep the preserve the sentence and not sentence tokenize it.
    :return:
    """
    return list(get_tokens(text, lowercase=lowercase, stopword=stopword,
                           preserve_line=preserve_line))


def get_stems(text, lowercase=False, stopword=False, stemmer=DEFAULT_STEMMER) -> Generator:
    """
    Get stems from text.
    N.B.: when stemmer is SnowballStemmer, lowercase is always returned no matter the parameter.
    :param text:
    :param lowercase:
    :param stopword:
    :param stemmer:
    :return:
    """
    for token in get_tokens(text, lowercase=lowercase, stopword=stopword):
        yield stemmer.stem(token)


def get_stem_list(text, lowercase=False, stopword=False, stemmer=DEFAULT_STEMMER) -> List:
    """
    Get stems materialized from text.
    N.B.: when stemmer is SnowballStemmer, lowercase is always returned no matter the parameter.

    :param text:
    :param lowercase:
    :param stopword:
    :param stemmer:
    :return:
    """
    return list(get_stems(text, lowercase=lowercase, stopword=stopword, stemmer=stemmer))


def get_lemmas(text, lowercase=False, stopword=False, lemmatizer=DEFAULT_LEMMATIZER) -> Generator:
    """
    Get lemmas from text.
    :param text:
    :param lowercase:
    :param stopword:
    :param lemmatizer:
    :return:
    """
    tokens = get_token_list(text, lowercase=False, stopword=False)
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


def get_lemma_list(text, lowercase=False, stopword=False, lemmatizer=DEFAULT_LEMMATIZER) -> List:
    """
    Get lemmas materialized from text.
    """
    return list(get_lemmas(text, lowercase=lowercase, stopword=stopword, lemmatizer=lemmatizer))


def get_verbs(text, lowercase=False, lemmatize=False) -> Generator:
    """
    Get only verbs from text.
    """
    tokens = get_token_list(text)
    pos = nltk.pos_tag(tokens)
    verb_index = [i for i in range(len(pos)) if pos[i][1].startswith("V")]
    if lemmatize:
        lemmas = get_lemma_list(text, lowercase=lowercase)
        for j in verb_index:
            yield lemmas[j]
    else:
        for j in verb_index:
            yield tokens[j].lower() if lowercase else tokens[j]


def get_nouns(text, lowercase=False, lemmatize=False) -> Generator:
    """
    Get only nouns from text.
    """
    tokens = get_token_list(text)
    pos = nltk.pos_tag(tokens)
    noun_index = [i for i in range(len(pos)) if pos[i][1].startswith("N")]
    if lemmatize:
        lemmas = get_lemma_list(text, lowercase=lowercase)
        for j in noun_index:
            yield lemmas[j]
    else:
        for j in noun_index:
            yield tokens[j].lower() if lowercase else tokens[j]


def get_adverbs(text, lowercase=False, lemmatize=False) -> Generator:
    """
    Get only adverbs from text.
    """
    tokens = get_token_list(text)
    pos = nltk.pos_tag(tokens)
    adverb_index = [i for i in range(len(pos)) if pos[i][1].startswith("RB")]
    if lemmatize:
        lemmas = get_lemma_list(text, lowercase=lowercase)
        for j in adverb_index:
            yield lemmas[j]
    else:
        for j in adverb_index:
            yield tokens[j].lower() if lowercase else tokens[j]


def get_adjectives(text, lowercase=False, lemmatize=False) -> Generator:
    """
    Get only adjectives from text.
    """
    tokens = get_token_list(text)
    pos = nltk.pos_tag(tokens)
    adj_index = [i for i in range(len(pos)) if pos[i][1].startswith("JJ")]
    if lemmatize:
        lemmas = get_lemma_list(text, lowercase=lowercase)
        for j in adj_index:
            yield lemmas[j]
    else:
        for j in adj_index:
            yield tokens[j].lower() if lowercase else tokens[j]
