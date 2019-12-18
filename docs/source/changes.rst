.. _changes:

============
Changelog
============

1.4.0 - December 20, 2019
----------------
 * Improved accuracy of locating and converting date phrases into typed format.
 * Introduced new text vectorizing and classifying models.
 * Implemented ML-based definitions locator.

1.3.0 - November 1, 2019
----------------
 * Made massive improvements to EN definitions and companies parsers.
 * Updated EN dates parser to catch more date formats.
 * Made company parsing strongly typed

0.2.7 - August 1, 2019
----------------
 * Standardized LexNLP methods response to return a generator of Annotation objects or a generator of dictionaries (tuples)
 * Improved LexNLP handling for definitions for the "EN" locale.
 * Improved LexNLP handling for companies for the "EN" locale.
 * Improved sentence splitting logic.
 * Improved LexNLP unit test coverage.
 * Updated python requirements in python-requirements*.txt.
 * Dropped support for python 3.4 and 3.5.

0.2.6 - Jun 12, 2019
----------------
 * Improved LexNLP handling for dates for all locales.
 * Improved LexNLP handling for currencies for "EN" locale.
 * Updated documentation for ReadTheDocs.
 * Improved LexNLP unit test coverage.

0.2.5 - Mar 1, 2019
----------------
 * Improved LexNLP handling for courts for "DE" and "ES" locales.
 * Improved LexNLP handling for dates for "ES" locale.
 * Improved LexNLP handling for amounts, acts, regulations and definitions for "EN" locale.
 * Added CUSIP parser for "EN" locale.
 * Improved LexNLP unit test coverage.

0.2.4 - Feb 1, 2019
----------------
 * Added universal courts parser, configured LexNLP handling for courts for "DE" locale.
 * Added universal dates parser, configured LexNLP handling for dates for "DE" and "ES" locales.
 * Added definitions, citations and dates parsers for "DE" locale.
 * Added amounts, percents and durations parsers for "DE" locale.
 * Added geo entities parser for "DE" locale.
 * Added courts and definitions parsers for "ES" locale.
 * Added acts parser for "EN" locale.
 * Improved LexNLP unit test coverage.

0.2.3 - Jan 10, 2019
----------------
 * Updated python requirements.
 * Improved LexNLP handling for definitions and paragraphs.
 * Improved LexNLP unit test coverage.

0.2.2 - Sep 30, 2018
----------------
 * Improved LexNLP handling for different date formats.
 * Improved LexNLP handling for titles.
 * Improved LexNLP unit test coverage.

0.2.1 - Aug 24, 2018
----------------
 * Updated python requirements.
 * Improved LexNLP handling for amounts.
 * Optimized processing of sentences and titles.
 * Improved LexNLP unit test coverage.

0.2.0 - Aug 1, 2018
----------------
 * Improved LexNLP handling for addresses and sentences.
 * Improved LexNLP unit test coverage.

0.1.9 - Jul 1, 2018
----------------
 * Improved handling of TOC during sentence processing.
 * Added contracts locator to LexNLP.
 * Improved LexNLP handling for citations, titles and definitions.
 * Improved LexNLP unit test coverage.

0.1.8 - May 1, 2018
----------------
 * Improved LexNLP handling for addresses and currencies.
 * Improved LexNLP unit test coverage.

0.1.7 - Apr 1, 2018
----------------
 * Improved LexNLP handling for companies, organizations and dates.
 * Implemented generating train/test dataset for addresses.
 * Exclude common false positives for persons parser.

0.1.6 - Mar 1, 2018
----------------
 * Improved LexNLP unit test coverage.

0.1.5 - Feb 1, 2018
----------------
 * Improved LexNLP unit test coverage.

0.1.4 - Jan 1, 2018
----------------
 * Improved LexNLP unit test coverage.
 * Implemented method to get sentence ranges in addition to sentence texts.

0.1.3 - Dec 1, 2017
----------------
 * Improved LexNLP unit test coverage.

0.1.2 - Nov 1, 2017
----------------
 * Implemented LexNLP title locator.
 * Implemented additional LexNLP transforms for skipgrams and n-grams.
 * Improved LexNLP handling for parties with abbreviations and other cases.
 * Improved LexNLP handling for amounts with mixed alpha and numeric characters.
 * Improved LexNLP unit test coverage.

0.1.1 - Oct 1, 2017
----------------
 * Improve unit test framework handling for language and locales.
 * Implemented method and input-level CPU and memory benchmarking for unit tests.
 * Migrated all unit tests to 60 separate CSV files.
 * Added over 1,000 new unit tests for most LexNLP methods.
 * Reduced memory usage for paragraph and section segmenters.
 * Improved handling of brackets and parentheses within noun phrases.
 * Added URL locator to LexNLP.
 * Added trademark locator to LexNLP.
 * Added copyright locator to LexNLP.
 * Improved default Punkt sentence boundary detection.
 * Added custom sentence boundary training methods.
 * Improved handling of multilingual text, especially around geopolitical entities.
 * Improved default handling of party names with non-standard characters.
 * Enhanced metadata related to party type in LexNLP.
 * Improved continuous integration for public repositories.

0.1.0 - Sep 1, 2017
----------------
 * Refactored and integrate core extraction into separate LexNLP package.
 * Released nearly 200 unit tests with over 500 real-world test cases in LexNLP.
 * Improved definition, date, and financial amount locators for corner cases.
 * Integrated PII locator for phone numbers, SSNs, and names from LexNLP.
 * Integrated ratio locator from LexNLP.
 * Integrated percent locator from LexNLP.
 * Integrated regulatory locator from LexNLP.
 * Integrated distance locator from LexNLP.
 * Integrated case citation locator from LexNLP.
 * Improved geopolitical locator to allow non-master-data entity location.
 * Improved party locator to allow configuration and better handle corner cases


