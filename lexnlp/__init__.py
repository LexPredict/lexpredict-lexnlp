__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os

# Stanford NLP flag


USE_STANFORD = os.environ["LEXNLP_USE_STANFORD"].lower() == "true" if "LEXNLP_USE_STANFORD" in os.environ else False

DEFAULT_MODELS_REPO_SLUG: str = "LexPredict/lexpredict-lexnlp"
DEFAULT_MODELS_REPO: str = (
    f"https://api.github.com/repos/{DEFAULT_MODELS_REPO_SLUG}/releases/tags/"
)


def get_models_repo() -> str:
    """
    Base GitHub API URL for LexNLP release tags used by model/corpus downloads.

    Override options:
    - LEXNLP_MODELS_REPO: full base URL (should end with `/releases/tags/`)
    - LEXNLP_MODELS_REPO_SLUG: GitHub slug like `owner/repo`

    Note: This returns a *base* URL; callers append the tag name.
    """
    url = (os.getenv("LEXNLP_MODELS_REPO") or "").strip()
    if url:
        return url if url.endswith("/") else f"{url}/"

    slug = (os.getenv("LEXNLP_MODELS_REPO_SLUG") or "").strip()
    if slug:
        return f"https://api.github.com/repos/{slug}/releases/tags/"

    # ``MODELS_REPO`` was historically a mutable module-level setting.  Keep
    # assignments made by existing integrations effective when no environment
    # override is configured.  Environment configuration remains preferred so
    # it can be changed after import without mutating Python module state.
    legacy_value = str(globals().get("MODELS_REPO", "") or "").strip()
    imported_value = str(globals().get("_IMPORTED_MODELS_REPO", "") or "").strip()
    if legacy_value and legacy_value != imported_value:
        return legacy_value if legacy_value.endswith("/") else f"{legacy_value}/"

    return DEFAULT_MODELS_REPO


MODELS_REPO: str = get_models_repo()
_IMPORTED_MODELS_REPO: str = MODELS_REPO


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
