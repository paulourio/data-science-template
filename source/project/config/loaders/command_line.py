"""YAML loader with support to nested references."""
from typing import Optional
import sys

from dynaconf.base import Settings
from dynaconf.utils.parse_conf import parse_conf_data

from project.cli.parser import parse_keyword_args


def load(obj: Settings,
         env: Optional[str] = None,
         silent: bool = True,
         key: Optional[str] = None,
         filename: Optional[str] = None) -> None:
    """Read and load single key or all keys from the command-line.

    The argument env is effectively ignored.
    This loader handles two special cases anywhere in the YAML:

    - `$ref: 'document.json'`

        Uses the whole document located on the same server and in the
        same location.

    - `x-key: value`

        Any key entry at the root-level with prefix `x-` is omitted in
        the loaded settings.

    Parameters
    ----------
    obj : dynaconf.base.Settings
        The setting instance that is modified after loading.
    env : str, optional
        Upper-case current environment.
    silent : bool
        If a errors should be raised.
    key : str, optional
        The only key to be loaded.  When None, everything should be
        loaded.
    filename : str, optional
        A custom filename to load, useful for tests.

    """
    if key is not None:
        raise NotImplementedError()

    try:
        result = _load_args(obj)
    except Exception as err:
        if not silent:
            raise err
    else:
        if env:
            result = result[env]
        if key:
            result = result[key]
        obj.update(result, loader_identifier='command_line', merge=True)


def _load_args(obj: Settings):
    prefix = '--' + obj.get('ENVVAR_PREFIX_FOR_DYNACONF').lower() + '_'
    data = {
        key: parse_conf_data(value, tomlfy=True)
        for key, value in parse_keyword_args(prefix=prefix)
    }
    return data
