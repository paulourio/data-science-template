from enum import Enum, auto
from functools import reduce
from typing import Any, Dict, Iterable, List
import logging
import os
import sys

from dynaconf.base import Settings
from dynaconf.validator import Validator, ValidationError

from ._types import ConfigFormat


def load_config(*, format: ConfigFormat = None,
                **dimensions: Dict[str, str]) -> Settings:
    """Return initialized configuration.

    Dimensions that are not specified are inferred from the context:

    - workspace: value in environment variable PROJECT_WORKSPACE.
    - logging: value in environment variable PROJECT_LOGGING.

    Parameters
    ----------
    format : ConfigFormat, optional
        The external source for loading configuration.
        Dimensions are only defined for ConfigFormat.YAML_FILES.
    dimensions : keyword arguments
        Keyword arguments may be specified to select specific
        dimensions.

    Raises
    ------
    ValueError
        When trying to read specific dimensions from a source that
        does not support dimension selection.

    Examples
    --------
    Load configuration based on the current environment context and
    current working directory.
    >>> config = load_config()

    Load configuration for a specific workspace and logging.
    >>> config = load_config(workspace='dev', logging='local')

    """
    if format is None:
        format = ConfigFormat.default()

    if format == ConfigFormat.YAML_FILES:
        return _load_config_yaml(**dimensions)

    if dimensions:
        raise ValueError('dimensions cannot be set for ' + str(format))

    if format == ConfigFormat.ENVIRONMENT_VARIABLES:
        return _load_config_env()

    raise NotImplementedError()


def as_dict(config: Settings) -> Dict[str, Any]:
    """Return mapping with configurations."""
    ignore = ('settings_module', 'settings_files_for_dynaconf',
              'environments', 'stream', 'envvar_prefix')
    config_dict = {k.lower(): v for k, v in config.as_dict().items()
                   if k.lower() not in ignore}
    return config_dict


def _load_config_env() -> Settings:
    config = Settings(
        settings_module=[],
        environments=False,
        stream=logging.StreamHandler(sys.stdout),
        envvar_prefix=ENVVAR_PREFIX,
        SETTINGS_FILES_FOR_DYNACONF=[],
        ENVVAR_PREFIX_FOR_DYNACONF=ENVVAR_PREFIX,
        CORE_LOADERS_FOR_DYNACONF=[],
        ENVIRONMENTS_FOR_DYNACONF=False,
        MAIN_ENV_FOR_DYNACONF='',
        LOADERS_FOR_DYNACONF=['dynaconf.loaders.env_loader'],
        SILENT_ERRORS_FOR_DYNACONF=False,
    )
    return config


def _load_config_yaml(**dimensions: Dict[str, str]) -> Settings:
    required_dimensions = {'workspace', 'logging'}

    files = ['config/project.yml']
    for key, value in dimensions.items():
        if key in required_dimensions:
            required_dimensions.remove(key)
        files.append(f'config/{key}-{value}.yml')

    if required_dimensions:
        # Fill missing required dimensions.
        for key in required_dimensions:
            files += _infer(key)

    try:
        return _load_config(files)
    except ValidationError as err:
        fmt = f'[{", ".join(files)}]'
        sys.stderr.write(
            f'CRITICAL: failed to read configuration {fmt}: {str(err)}.\n')
        raise


def _load_config(files):
    for fname in files:
        if not os.path.isfile(fname):
            raise RuntimeError('missing configuration file ' + fname)

    config = Settings(
        settings_module=files,
        environments=False,
        stream=logging.StreamHandler(sys.stdout),
        validators=[
            Validator('logging.type',
                      'logging.level',
                      'logging.message_format',
                      'logging.timestamp_format',
                      'logging.loggers',
                      must_exist=True),
            Validator('logging.type', must_exist=True, is_in=LOGGING_TYPES),
            Validator('logging.level', must_exist=True, is_in=LOGGING_LEVELS),
            Validator(r'^logging.loggers.', is_in=LOGGING_LEVELS),
            Validator('storage.scopes', is_type_of=list),
            _each_is_one_of('storage.scopes', STORAGE_SCOPES),
            Validator('storage.temp_bucket', must_exist=True, is_type_of=str),
            Validator('storage.cache_bucket', must_exist=True,
                      is_type_of=str),
            Validator('storage.authentication', must_exist=True,
                      is_in=('google_default', 'cloud')),
        ],
        CORE_LOADERS_FOR_DYNACONF=[],
        ENVIRONMENTS_FOR_DYNACONF=False,
        MAIN_ENV_FOR_DYNACONF='',
        LOADERS_FOR_DYNACONF=['project.config.loaders.yaml'],
        SILENT_ERRORS_FOR_DYNACONF=False,
    )

    # This line exists solely to force loading the configuration
    # data, because the default lazy behavior only loads at the
    # first access.
    assert config.project.name != ''

    return config


def _each_is_one_of(name: str, values: Iterable[str]) -> Validator:
    expr = reduce(
        lambda a, b: a | b,
        [
            Validator(name, must_exist=True, cont=value)
            for value in values
        ],
    )
    return expr


def _infer(key: str) -> List[str]:
    if key == 'workspace':
        return _infer_workspace()
    if key == 'logging':
        return _infer_logging()
    raise ValueError('no inference for ' + str(key))


def _infer_workspace() -> List[str]:
    workspace = os.environ['DEFAULT_PROJECT_WORKSPACE']
    return [f'config/workspace-{workspace}.yml']


def _infer_logging() -> List[str]:
    logging_name = os.environ['DEFAULT_PROJECT_LOGGING']
    return [f'config/logging-{logging_name}.yml']


ENVVAR_PREFIX = 'PROJECT'
"""Prefix for environment variables. This value must be upper case to
work with dynaconf."""

LOGGING_TYPES = ('default', 'colored', 'google')

LOGGING_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

STORAGE_SCOPES = (
    'https://www.googleapis.com/auth/devstorage.read_only',
    'https://www.googleapis.com/auth/devstorage.read_write',
    'https://www.googleapis.com/auth/devstorage.full_control',
)
