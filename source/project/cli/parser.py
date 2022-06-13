"""Command-line interface parser."""
from typing import Dict, List, Optional, Tuple
import sys
import warnings


def parse_keyword_args_as_dict(
    args: Optional[List[str]] = None, *,
    prefix: str = '--',
) -> Dict[str, str]:
    """Return mapping of parsed keyword-arguments."""
    return dict(parse_keyword_args(args, prefix=prefix))


def parse_keyword_args(args: Optional[List[str]] = None, *,
                       prefix: str = '--') -> List[Tuple[str, str]]:
    """Return keyword-arguments (key, value) in the command line.

    This parser is designed to process an unknown and dynamic list of
    keyword arguments. See tests for examples.

    Parameters
    ----------
    args : list, optional
        Arguments from the command line. By default, fetch arguments
        from sys.argv.
    prefix : str, default=''
        The prefix to filter keyword arguments.
        When prefix '--'

    """
    if args is None:
        args = list(sys.argv)

    if not args:
        return []

    data: List[Tuple[str, str]] = list()
    prefix_len = len(prefix)
    n = len(args)

    i = 0
    while i < n-1:
        if not _match(args[i], prefix):
            if i+2 == n and _match(args[i+1], prefix):
                _warn_bad_keyword(args[i+1], prefix)
            i += 1
            continue

        key = args[i][prefix_len:]
        value = args[i+1]
        i += 2

        data.append((key, value))

    if n % 2 == 1 and _match(args[-1], prefix):
        _warn_bad_keyword(args[-1], prefix)

    return data


def _match(keyword: str, prefix: str) -> bool:
    return keyword.startswith(prefix) and keyword != prefix


def _warn_bad_keyword(keyword: str, prefix: str) -> None:
    warnings.warn(
        (f'Missing value in command-line when parsing keyword '
            f'at the end of argv. The keyword argument {keyword!r} '
            f'matches prefix {prefix!r}.'),
        stacklevel=2)
