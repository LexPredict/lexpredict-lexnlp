.. _nlp:

============
:mod:`lexnlp.nlp`: Natural language processing
============

The :mod:`lexnlp.nlp` module contains methods that assist in natural
language processing (NLP) tasks, especially in the context of developing
unsupervised, semi-supervised, or supervised machine learning.  Methods
range from tokenizing, stemming, and lemmatizing to the creation of
custom sentence segmentation or word embedding models.

This module is structured along ISO 2-character language codes.  Currently, the following languages are stable:
 * English: `lexnlp.nlp.en`

Extraction methods follow a simple `get_X` pattern as demonstrated below::

    >>> import lexnlp.nlp.en.tokens
    >>> text = "There are ten cows in the 2 acre pasture."
    >>> print(list(lexnlp.nlp.en.tokens.get_nouns(text)))
    ['cows', 'pasture']

The methods in this package are primarily built on the Natural Language Toolkit (NLTK),
but some functionality from the Stanford NLP, gensim, and spaCy packages is available
to users depending on their use case.

Tokenization and related methods
----------------
 * lexnlp.nlp.en.tokens

Segmentation and related methods
----------------
 * lexnlp.nlp.en.segments.pages
 * lexnlp.nlp.en.segments.paragraphs
 * lexnlp.nlp.en.segments.sections
 * lexnlp.nlp.en.segments.sentences
 * lexnlp.nlp.en.segments.titles
 * lexnlp.nlp.en.segments.utils

Transforms and related methods
----------------
 * lexnlp.nlp.en.transforms.characters
 * lexnlp.nlp.en.transforms.tokens
