"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
from pathlib import Path
from typing import Dict, Optional

# NLTK
import nltk.data


CATALOG: Path = Path(nltk.data.find('')) / 'lexpredict-lexnlp'


def _build_tag_dict() -> Dict[str, Path]:
    """
    Builds a dictionary with the following structure:

    - keys (str): directory paths relative to CATALOG, each corresponding to GitHub release tags.
    - values (Path): file path under the directory ("tag").

    Returns:
        A dictionary.
    """
    return {
        str(path.parent.relative_to(CATALOG)): path
        for path in CATALOG.rglob('*')
        if path.is_file()
    }


def get_path_from_catalog(tag: str) -> Path:
    """
    Args:
        tag (str):

    Returns:
        A file path.
    """
    d: Dict[str, Path] = _build_tag_dict()
    path: Optional[Path] = d.get(tag)
    if path is None:
        raise FileNotFoundError(
            f'Could not find tag={tag} in CATALOG={CATALOG}. '
            f'Please download using `lexnlp.ml.catalog.download.download_github_release("{tag}")`'
        )
    else:
        return path
