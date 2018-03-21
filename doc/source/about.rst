.. _about:

============
About LexNLP
============

Purpose
----------------
LexNLP is a library for working with real, unstructured legal text, including contracts, plans, policies, procedures, and other material. LexNLP provides functionality such as:

Segmentation and tokenization, such as
 * A sentence parser that is aware of common legal abbreviations like LLC. or F.3d.

   - Pre-trained segmentation models for legal concepts such as pages or sections.
   - Pre-trained word embedding and topic models, broadly and for specific practice areas

 * Pre-trained classifiers for document type and clause type

 * Broad range of fact extraction, such as:

   - Monetary amounts, non-monetary amounts, percentages, ratios
   - Conditional statements and constraints, like "less than" or "later than"
   - Dates, recurring dates, and durations
   - Courts, regulations, and citations

 * Tools for building new clustering and classification methods

 * Hundreds of unit tests from real legal documents

ContraxSuite Projects
----------------
LexNLP is often used as part of ContraxSuite, an open source contract analytics and document exploration
platform built by LexPredict.  LexNLP and ContraxSuite are related through the following project structure:
 * ContraxSuite web application: https://github.com/LexPredict/lexpredict-contraxsuite
 * LexNLP library for extraction: https://github.com/LexPredict/lexpredict-lexnlp
 * ContraxSuite pre-trained models and "knowledge sets": https://github.com/LexPredict/lexpredict-legal-dictionary
 * ContraxSuite agreement samples: https://github.com/LexPredict/lexpredict-contraxsuite-samples
 * ContraxSuite deployment automation: https://github.com/LexPredict/lexpredict-contraxsuite-deploy

Citing for academic use
----------------
We are currently drafting and submitting a technical whitepaper describing the LexNLP library and
documenting its performance on a large corpus of gold-standard contracts.  Please contact us
at support@contraxsuite.com for more information on citing in academic use.