__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os

# Stanford NLP flag


USE_STANFORD = os.environ["LEXNLP_USE_STANFORD"].lower() == "true" if "LEXNLP_USE_STANFORD" in os.environ else False

MODELS_REPO: str = "https://api.github.com/repos/LexPredict/lexpredict-lexnlp/releases/tags/"


def get_module_path():
    """
    Get the module path.
    :return:
    """
    return os.path.dirname(os.path.abspath(__file__))


def get_lib_path():
    """
    Return the base project path.
    :return:
    """
    return os.path.abspath(os.path.join(get_module_path(), "..", "libs"))


def is_stanford_enabled():
    """
    Return flag for whether Stanford NLP library is enabled.
    :return:
    """
    if "LEXNLP_USE_STANFORD" not in os.environ:
        return False
    return os.environ["LEXNLP_USE_STANFORD"].lower() == "true"


def enable_stanford():
    """
    Enable the Stanford NLP library.
    :return:
    """
    os.environ["LEXNLP_USE_STANFORD"] = "true"


def disable_stanford():
    """
    Disable the Stanford NLP library.
    :return:
    """
    os.environ["LEXNLP_USE_STANFORD"] = "false"
