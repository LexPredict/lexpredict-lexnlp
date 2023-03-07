__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=unused-import

from shutil import copyfile
from typing import Dict, Any
from collections import OrderedDict
import os


def ensure_documents_in_folder(
        document_paths: Dict[str, Any],
        target_folder: str,
        folder_alias: 'OrderedDict[str, str]') -> Dict[str, Any]:
    """
    Example call:
      ensure_documents_in_folder([{'./data/agreements/agreement01.txt': [10, 57, 121]},
                                 '/tmp/documents/',
                                  {'./data/': '<path_to_samples_repository>/data/'})
    The function ensures the files listed as keys in the "document_paths" in the "target_folder"
    folder, searching the files into the "folder_alias" referenced directories.
    """

    updated_paths = {}

    for path in document_paths:
        name_only = os.path.basename(path)
        target_path = os.path.join(target_folder, name_only)
        if os.path.isfile(target_path):
            updated_paths[target_path] = document_paths[path]
            continue

        for alias in folder_alias:
            if not path.startswith(alias):
                continue
            src_path = path.replace(alias, folder_alias[alias])
            if not os.path.isfile(src_path):
                continue
            copyfile(src_path, target_path)
            updated_paths[target_path] = document_paths[path]
            break

    return updated_paths
