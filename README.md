[![Coverage Status](https://coveralls.io/repos/github/LexPredict/lexpredict-lexnlp/badge.svg?branch=master)](https://coveralls.io/github/LexPredict/lexpredict-lexnlp?branch=master)[![Build Status](https://travis-ci.org/LexPredict/lexpredict-lexnlp.svg?branch=master)](https://travis-ci.org/LexPredict/lexpredict-lexnlp)

![Logo](https://s3.amazonaws.com/lexpredict.com-marketing/graphics/lexpredict_lexnlp_logo_horizontal_1.png)

# LexNLP by LexPredict
## Information retrieval and extraction for real, unstructured legal text
LexNLP is a library for working with real, unstructured legal text, including contracts, plans, policies, procedures,
and other material.  LexNLP provides functionality such as:
* Segmentation and tokenization, such as
  * A sentence parser that is aware of common legal abbreviations like LLC. or F.3d.
  * Pre-trained segmentation models for legal concepts such as pages or sections.
* Legal-specific stopwords and collocations
* Pre-trained word embedding and topic models, broadly and for specific practice areas
* Pre-trained classifiers for document type and clause type
* Broad range of fact extraction, such as:
  * Monetary amounts, non-monetary amounts, percentages, ratios
  * Conditional statements and constraints, like "less than" or "later than"
  * Dates, recurring dates, and durations
  * Courts, regulations, and citations
* Tools for building new clustering and classification methods
* Hundreds of unit tests from real legal documents

# Information
* Official Website: https://lexnlp.com/
* ContraxSuite: https://contraxsuite.com/
* LexPredict: https://lexpredict.com/
* Documentation: (in progress)
* Contact: support@contraxsuite.com


## Licensing
LexNLP is available under a dual-licensing model.  By default, this library can be used under AGPLv3 terms as detailed
in the repository LICENSE file; however, organizations can request a release from the AGPL terms by contacting
ContraxSuite Licensing at <<license@contraxsuite.com>>.


## Releases
* 0.1.0: Ocotober 1, 2017 - First public release; [code](https://github.com/LexPredict/lexpredict-lexnlp/tree/0.1.0)
