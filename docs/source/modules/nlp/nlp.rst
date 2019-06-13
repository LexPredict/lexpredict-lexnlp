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

.. attention::
    The sections below are a work in progress.  Thank you for your patience
    while we continue to expand and improve our documentation coverage.

    If you have any questions in the meantime, please feel free to log issues on
    GitHub at the URL below or contact us at the email below:

    - GitHub issues: https://github.com/LexPredict/lexpredict-lexnlp
    - Email: support@contraxsuite.com


Tokenization and related methods
----------------

 * :ref:`Extracting tokens, stems, lemmas, and parts of speech <nlp_en_tokens>`



Segmentation and related methods for real-world text
----------------

 * :ref:`Sentences <nlp_en_segments_sentences>`

 * :ref:`Paragraphs <nlp_en_segments_paragraphs>`

 * :ref:`Sections <nlp_en_segments_sections>`

 * :ref:`Pages <nlp_en_segments_pages>`

 * :ref:`Titles <nlp_en_segments_titles>`

 * :ref:`Utilities <nlp_en_segments_utils>`

Transforming text into features
----------------

 * :ref:`Character Transforms <nlp_en_transforms_characters>`

 * :ref:`Token Transforms <nlp_en_transforms_tokens>`, including n-grams and skip-grams
