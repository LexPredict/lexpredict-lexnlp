.. _nlp_en_tokens:

============
:mod:`lexnlp.nlp.en.tokens`: Working with tokens
============

The :mod:`lexnlp.nlp.en.tokens` module contains methods that provide a number
of useful functions for extracting and working with tokens in text.

Tokenizing text
----------------
Tokenization is one of the most common and basic operations in natural language processing.
LexNLP supports custom tokenizers, but by default mirrors the behavior of
`word_tokenize <http://www.nltk.org/api/nltk.tokenize.html?highlight=word_tokenize#nltk.tokenize.word_tokenize>`_
from the NLTK package.

This module provides both generator and list tokenization methods for convenience::

    >>> import lexnlp.nlp.en.tokens
    >>> text = "The quick brown fox barely jumps over the lazy dog."
    >>> print(lexnlp.nlp.en.tokens.get_tokens(text))
    <generator object get_tokens at 0x000001C50B4CE5C8>
    >>> print(lexnlp.nlp.en.tokens.get_token_list(text))
    ['The', 'quick', 'brown', 'fox', 'barely', 'jumps', 'over', 'the', 'lazy', 'dog', '.']
    >>> print(lexnlp.nlp.en.tokens.get_token_list(text, lowercase=True))
    ['the', 'quick', 'brown', 'fox', 'barely', 'jumps', 'over', 'the', 'lazy', 'dog', '.']
    >>> print(lexnlp.nlp.en.tokens.get_token_list(text, lowercase=True, stopword=True))
    ['quick', 'brown', 'fox', 'barely', 'jumps', 'lazy', 'dog', '.']


.. note::
    By default, LexNLP uses a custom set of 163 stopwords derived from American English contracts.
    This list is stored in `stopwords.pickle` in the package directory and can customized by setting
    the value of `lexnlp.nlp.en.tokens.STOPWORDS` to a list of alternative strings.  N.B.: stopwording
    is case-insensitive.

Stemming and lemmatizing text
----------------
Stemming and lemmatization are also supported in LexNLP.  Custom stemmers or lemmatizers can be implemented,
as well as any models available in NLTK.  Models from Stanford NLP and spaCy can also be injected subject to
the user's licensing and use case.  By default, the following models are exposed:

 * Stemming: `nltk.stem.snowball.EnglishStemmer <http://www.nltk.org/api/nltk.stem.html?highlight=stemmer#module-nltk.stem.snowball>`_

 * Lemmatizing: `nltk.stem.wordnet.WordNetLemmatizer <http://www.nltk.org/api/nltk.stem.html?highlight=stemmer#module-nltk.stem.wordnet>`_


As with tokenization, this module provides both list and generator methods for convenience::

    >>> import lexnlp.nlp.en.tokens
    >>> text = "The quick brown fox barely jumps over the lazy dog."
    >>> print(lexnlp.nlp.en.tokens.get_stems(text))
    <generator object get_stems at 0x000001C51B3EEFC0>
    >>> print(lexnlp.nlp.en.tokens.get_stem_list(text))
    ['the', 'quick', 'brown', 'fox', 'bare', 'jump', 'over', 'the', 'lazi', 'dog', '.']
    >>> print(lexnlp.nlp.en.tokens.get_stem_list(text, stopword=True)
    ['quick', 'brown', 'fox', 'bare', 'jump', 'lazi', 'dog', '.']
    >>> print(lexnlp.nlp.en.tokens.get_stem_list(text, stemmer=nltk.stem.lancaster.LancasterStemmer()))
    ['the', 'quick', 'brown', 'fox', 'bar', 'jump', 'ov', 'the', 'lazy', 'dog', '.']
    >>> print(lexnlp.nlp.en.tokens.get_lemma_list(text))
    ['The', 'quick', 'brown', 'fox', 'barely', 'jump', 'over', 'the', 'lazy', 'dog', '.']
    >>> print(lexnlp.nlp.en.tokens.get_lemma_list(text, stopword=True, lowercase=True))
    ['quick', 'brown', 'fox', 'barely', 'jump', 'lazy', 'dog', '.']


.. note::
    Note that the default stemmer, Snowball, is case-insensitive and returns all lowercased text.
    Future versions of LexNLP will re-case the returned tokens to match the original text.

Working with parts-of-speech
----------------
LexNLP can also provide access to part of speech (POS) information directly.  By default, LexNLP
uses the pre-trained `nltk.tag.pos_tag <https://www.nltk.org/api/nltk.tag.html#nltk.tag.pos_tag>`_
method, which is built on the Penn Treebank corpus and tags.  The Stanford NLP and spaCy taggers
can also be substituted depending on the user's licensing and use case.

.. note::
    Future versions of LexNLP will add functionality to simplify the training of custom taggers.
    Users interested in building custom taggers should refer to the `ContraxSuite <https://contraxsuite.com>`_
    web application for now to see how annotation and machine learning models are developed.

In addition to exposing token and tag information, basic methods are provided to extract tokens
of certain part of speech types like nouns or verbs::

    >>> import lexnlp.nlp.en.tokens
    >>> text = "The brown fox barely jumps over the lazy dog."
    >>> print(list(lexnlp.nlp.en.tokens.get_nouns(text)))
    ['fox', 'dog']
    >>> print(list(lexnlp.nlp.en.tokens.get_verbs(text)))
    ['jumps']
    >>> print(list(lexnlp.nlp.en.tokens.get_verbs(text, lemmatize=True)))
    ['jump']
    >>> print(list(lexnlp.nlp.en.tokens.get_adjectives(text)))
    ['brown', 'lazy']
    >>> print(list(lexnlp.nlp.en.tokens.get_adverbs(text)))
    ['barely']


Collocations
-------
LexNLP provides common bigram and trigram collocations for supported languages.
The `lexnlp.nlp.en` includes bigram and trigram collocations trained on American
English contracts.  The `lexnlp.nlp.en.tokens.COLLOCATION_SIZE` variable controls
the default size for collocations; currently, pre-calculated pickles including
the top 100, 1,000, and 10,000 bigram and trigram collocations are provided with
LexNLP.


.. attention::
    This section is a work in progress.  Thank you for your patience
    while we continue to expand and improve our documentation coverage.

    If you have any questions in the meantime, please feel free to log issues on
    GitHub at the URL below or contact us at the email below:

    - GitHub issues: https://github.com/LexPredict/lexpredict-lexnlp
    - Email: support@contraxsuite.com


.. automodapi:: lexnlp.nlp.en.tokens
    :include-all-objects:
    :members:

