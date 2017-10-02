"""Court extraction for English.

This module implements extraction functionality for courts in English, including formal names, abbreviations,
and aliases.

Todo:
  * Add utilities for loading court data
"""

from lexnlp.nlp.en.tokens import get_tokens


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CourtConfig(object):
    """
    Court configuration object, containing the structured data for each
    courts to be located and extracted.
    """

    def __init__(self, idx, name, level=None, jurisdiction=None, court_type=None, court_aliases=None):
        """
        Constructor
        """
        self.id = idx
        self.name = name
        self.level = level
        self.jurisdiction = jurisdiction
        self.court_type = court_type
        if court_aliases is not None:
            self.court_aliases = court_aliases
        else:
            self.court_aliases = []

    def get(self, arg):
        return getattr(self, arg, None)

    def __str__(self):
        """
        String representation for CourtConfig
        :return:
        """
        return "{0} (id={1})".format(self.name, self.id)

    def __repr__(self):
        """
        Representation for CourtConfig
        :return:
        """
        return str(self)


def get_courts(text, court_config_list, return_source=False):
    """
    Get all courts based on the provided list of CourtConfig objects.
    :param text:
    :param court_config_list: list of dict or list of CourtConfig
    :param return_source:
    :return:
    """
    tokenized_text = ' %s ' % ' '.join(get_tokens(text, lowercase=True))

    # Iterate through all CourtConfig objects
    for court_config in court_config_list:
        # Check for name match
        if ' %s ' % court_config.get('name').lower() in tokenized_text:
            if return_source:
                yield court_config, court_config.get('name')
            else:
                yield court_config

        # Check for alias match
        for alias in court_config.get('court_aliases'):
            if ' %s ' % ' '.join(get_tokens(alias, lowercase=True)) in tokenized_text:
                if return_source:
                    yield court_config, alias
                else:
                    yield court_config
