"""
General utility functions.
"""
import re
import hashlib

from pathlib import Path
from subprocess import run

from .log import get_logger

PATTERN_SPACE = re.compile(r" +")
PATTERN_NOT_ALPHANUMERIC = re.compile(r"[^0-9a-zA-Z_]")
PATTERN_UNDERSCORE_DUPLICATED = re.compile(r"_{2,}")


def download_file(url: str, output_file: str):
    """Default function to download a file given an URL and output path"""
    command = ["curl", "-s", "-L", url, "-o", output_file]
    run(command)


def curl(
    url: str,
    output_file: str,
    md5hash: str = None,
    logger=None,
    download_file_func=download_file,
    raise_on_md5hash_mismatch=True,
):
    """Downloads a file from an URL. If the md5hash option is specified, it checks
    if the file was successfully downloaded (whether MD5 matches).

    Before starting the download, it checks if output_file exists. If so, and md5hash
    is None, it quits without downloading again. If md5hash is not None, it checks if
    it matches the file.

    Args:
        url: URL of file to download.
        output_file: path of file to store content.
        md5hash: expected MD5 hash of file to download.
        logger: Logger instance.
        download_file_func: a function that receives two arguments (a url to
            a file and an output file path). It is supposed to download the file
            pointed by the URL and save it to the specified path. This argument is
            mainly used for unit testing purposes.
        raise_on_md5hash_mismatch: if the method should raise an AssertionError
            if the downloaded file does not match the given md5 hash.
    """
    logger = logger or get_logger("none")

    Path(output_file).resolve().parent.mkdir(parents=True, exist_ok=True)

    if Path(output_file).exists() and (
        md5hash is None or md5_matches(md5hash, output_file)
    ):
        logger.info(f"File already downloaded: {output_file}")
        return

    logger.info(f"Downloading {output_file}")
    download_file_func(url, output_file)

    if md5hash is not None and not md5_matches(md5hash, output_file):
        msg = "MD5 does not match"
        logger.error(msg)

        if raise_on_md5hash_mismatch:
            raise AssertionError(msg)


def md5_matches(expected_md5: str, filepath: str) -> bool:
    """Checks the MD5 hash for a given filename and compares with the expected value.

    Args:
        expected_md5: expected MD5 hash.
        filepath: file for which MD5 will be computed.

    Returns:
        True if MD5 matches, False otherwise.
    """
    with open(filepath, "rb") as f:
        current_md5 = hashlib.md5(f.read()).hexdigest()
        return expected_md5 == current_md5


def simplify_string(value: str) -> str:
    # replace spaces by _
    value = re.sub(PATTERN_SPACE, "_", value)

    # remove non-alphanumeric characters
    value = re.sub(PATTERN_NOT_ALPHANUMERIC, "", value)

    # replace spaces by _
    value = re.sub(PATTERN_UNDERSCORE_DUPLICATED, "_", value)

    return value


def chunker(seq, size):
    """
    Divides a sequence in chunks according to the given size. For example, if
    given a list
        [0,1,2,3,4,5,6,7]
    and size 3, it will return
        [[0, 1, 2], [3, 4, 5], [6, 7]]
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
