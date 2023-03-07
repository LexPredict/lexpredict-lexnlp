"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
import logging
from pathlib import Path
from hashlib import md5
from base64 import b64encode
from math import floor, log, pow
from typing import Any, Dict, Generator, Iterator, Union

# third-party libraries
from tqdm import tqdm
from requests import get, Response
from requests.structures import CaseInsensitiveDict

# LexNLP
from lexnlp import MODELS_REPO
from lexnlp.ml.catalog import CATALOG


logging.basicConfig(
    format='[LexNLP][%(asctime)s][%(levelname)s]: %(message)s',
    level=logging.INFO
)
LOGGER: logging.Logger = logging.getLogger()


class ChecksumError(Exception):
    pass


class GitHubReleaseDownloader:
    """
    """

    @classmethod
    def download_release(cls, tag: str):
        response: Response = cls.get_tag(tag)
        asset: Dict[str, Any] = cls.get_asset(response)
        destination_directory: Path = CATALOG / tag
        cls.download_asset(asset, destination_directory)

    @staticmethod
    def get_tag(tag: str) -> Response:
        response: Response = get(
            url=f'{MODELS_REPO}{tag}',
            headers={
                'Accept': 'application/vnd.github.v3+json',
            },
        )
        return response

    @staticmethod
    def get_asset(response: Response, index: int = 0) -> Dict[str, Any]:
        try:
            asset: Dict[str, Any] = response.json()['assets'][index]
        except KeyError as key_error:
            raise KeyError(f'Available keys: {response.json().keys()}') from key_error
        return asset

    @staticmethod
    def yield_asset(
        content_iterator: Iterator,
        content_length: int,
        chunk_size: int,
    ) -> Generator[bytes, None, None]:
        """
        Args:
            content_iterator:
            content_length:
            chunk_size:

        Yields:
            File bytes.

        Raises:
            ValueError:
                Raised if `content_length == 0`.
        """
        if content_length == 0:
            raise ValueError('content_length == 0; nothing to download.')

        with tqdm(
            total=content_length,
            unit='iB',
            unit_scale=True,
        ) as progress_bar:
            for chunk in content_iterator:
                progress_bar.update(chunk_size)
                yield chunk

    @classmethod
    def download_asset(
        cls,
        asset: Dict[str, Any],
        destination_directory: Union[Path, str],
        *,
        # TODO: is there a way to infer optimum chunk_size? Filesystem chunks?
        chunk_size: int = 8192,
    ) -> None:
        """
        Args:
            asset (Dict[str, Any]):
            destination_directory (Union[Path, str]):
            chunk_size (int=8192):

        Returns:
            None

        References:
            https://docs.github.com/en/rest/reference/releases#get-a-release-asset
        """
        response: Response = get(
            url=asset['url'],
            stream=True,
            headers={
                'Accept': 'application/octet-stream',
            },
        )
        headers: CaseInsensitiveDict[str, Any] = response.headers
        name: str = asset.get('name')
        content_length: int = int(headers.get('Content-Length', asset.get('size', 0)))
        content_iterator: Iterator = response.iter_content(chunk_size=chunk_size)

        LOGGER.info(f'Downloading {name}...')
        path_file: Path = Path(destination_directory, name)
        destination_directory.mkdir(exist_ok=True, parents=True)
        with open(path_file, 'wb') as f:
            for chunk in cls.yield_asset(content_iterator, content_length, chunk_size):
                f.write(chunk)
        LOGGER.info(f'...downloaded {name} to {destination_directory}')
        content_md5: str = headers.get('Content-MD5')
        if content_md5:
            LOGGER.info(f'Detected MD5; verifying ({content_md5})...')
            cls.verify_md5(path_file, content_md5)
            LOGGER.info('...verified.')

    @staticmethod
    def verify_md5(
        filepath: Union[Path, str],
        checksum: str,
    ) -> None:
        """
        Args:
            filepath (Union[Path, str]):
                A filepath to verify.
            checksum (str):
                A Base64-encoded string, like "VLI7BOFu+GFE39vo+3UfaQ=="

        Raises:
            ChecksumError:
                 Raised if MD5 hashes do not match.
        """
        with open(filepath, 'rb') as f:
            h = md5(f.read())

        h_b64: str = b64encode(h.digest()).decode()
        if h_b64 != checksum:
            raise ChecksumError(
                'MD5 checksum verification failed! '
                f'Received: {h_b64} '
                f'Expected: {checksum}'
            )


def download_github_release(tag: str, prompt_user: bool = True) -> None:
    """
    Downloads a GitHub release from the release repository, optionally confirming
    download behavior with a human user.

    If `prompt_user == True`:
        1. Prompt user for download [Y/n]
        2. If [Y], fetch file size
        3. Ask user if downloading file size is acceptable [Y/n]
        4. If [Y], download file

    Args:
        tag (str):
            The GitHub release tag to download.
        prompt_user (bool=True):
            Whether to prompt the user before downloading.

    Returns:
        None

    Raises:
        ValueError:
            Raised if `prompt_user == True` and user does not enter valid input.
    """
    # TODO: use a proper CLI library like Typer if we make this any more complex

    def _input_yes_no(prompt: str):
        answer: str = input(prompt).lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            raise ValueError("User input must be 'Y' or 'n'.")

    def _get_asset() -> Dict[str, Any]:
        response: Response = GitHubReleaseDownloader.get_tag(tag)
        response.raise_for_status()
        return GitHubReleaseDownloader.get_asset(response)

    def _download_asset() -> None:
        destination_directory: Path = CATALOG / tag
        GitHubReleaseDownloader.download_asset(asset, destination_directory)

    def bytes_to_human_readable(number_of_bytes: int) -> str:
        magnitude: int = int(floor(log(number_of_bytes, 1024)))
        value: float = number_of_bytes / pow(1024, magnitude)
        if magnitude > 3:
            return f'{value:.1f} TiB'
        return '{:3.2f} {}B'.format(value, ('', 'Ki', 'Mi', 'Gi')[magnitude])

    if prompt_user:
        answer_download = _input_yes_no(f'Download `{tag}` from {MODELS_REPO}? [Y/n]')
        if answer_download:
            asset: Dict[str, Any] = _get_asset()
            try:
                content_length: int = asset['size']
            except KeyError as key_error:
                raise Exception('Could not determine download size') from key_error
        else:
            print(f'Not downloading `{tag}`. Exiting.')
            return

        answer_download_size = _input_yes_no(
            f'Download ~{bytes_to_human_readable(content_length)}? [Y/n]'
        )
        if answer_download_size:
            _download_asset()
        else:
            print(f'Not downloading `{tag}`. Exiting.')

    else:
        asset: Dict[str, Any] = _get_asset()
        _download_asset()
