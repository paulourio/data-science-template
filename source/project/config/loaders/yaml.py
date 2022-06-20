"""YAML loader with support to nested references."""
from multiprocessing.sharedctypes import Value
from typing import Any, List, Optional
import os

from dynaconf.base import Settings
import yaml


def load(obj: Settings,
         env: Optional[str] = None,
         silent: bool = True,
         key: Optional[str] = None,
         filename: Optional[str] = None) -> None:
    """Read and load single key or all keys from a YAML files.

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

    files = filename or obj.get('SETTINGS_FILE_FOR_DYNACONF')
    existing = [fname for fname in files if os.path.isfile(fname)]

    if not silent:
        if len(files) != len(existing):
            missing = str(list(set(files) - set(existing)))
            raise FileNotFoundError('missing config files: ' + missing)

    _load(obj, existing, env, key, silent)


def _load(obj: Settings, files: List[str],
          env: Optional[str], key: Optional[str], silent: bool) -> None:
    # Iteratively read YAML files processing references.
    for fname in files:
        try:
            result = _load_yaml(fname)
        except Exception as err:
            if not silent:
                raise err
        else:
            if env:
                result = result[env]
            if key:
                result = result[key]
            obj.update(result, loader_identifier='custom_yaml', merge=True)


def _load_yaml(fname: str):
    with open(fname, 'rt') as yaml_in:
        data = yaml.safe_load(yaml_in)

    dirname = os.path.dirname(fname)
    data = _process(data, dirname)
    return data


def _process(data: Any, dirname: str):
    if isinstance(data, dict):
        data = data.copy()
        for key, value in list(data.items()):
            value = _process(value, dirname)
            data[key] = value
            # If you are trying to set a name with dot, hyphen, or two
            # underscores, you should probably created another structure
            # where this dotted/hyphened key becomes the value.
            if '.' in key:
                raise ValueError('dotted names are not allowed: ' + key)
            if '-' in key and not key.startswith('x-'):
                raise ValueError('names with hyphen are not allowed: ' + key)
            if '__' in key:
                raise ValueError(
                    'double underscores names are not allowed: ' + key)
            if key == '$ref':
                del data[key]
                result = _load_yaml(os.path.join(dirname, value))
                data.update(result)
            elif key.startswith('x-'):
                del data[key]
        return data
    elif isinstance(data, list):
        return [_process(elem, dirname) for elem in data]

    return data
