from typing import Any, Dict, List
from pathlib import Path
import os
import sys

from dynaconf.base import Settings
from dynaconf.validator import ValidationError

from project.cli.parser import parse_keyword_args_as_dict
from ._environment import Environment
from ._validator import validators
from ._converters import register_converters


def load_config(
    *,
    load_env: bool = True,
    load_yaml: bool = True,
    load_command_line: bool = False,
    load_command_line_dimensions: bool = False,
    load_validate: bool = True,
    load_verbose: bool = False,
    **dimensions: str,
) -> Settings:
    """Return initialized configuration.

    When loading YAML files, environment variables with prefix
    `PROJECT_DIMENSION_{dim}={value}` are always loaded.

    Parameters
    ----------
    load_env : bool, default=True
        Whether to load variables from the environment.
    load_yaml : bool, default=True
        Whether to load variables from YAML files.
    load_command_line : bool, default=True
        Whether to load variables from the command-line arguments.
    load_command_line_dimensions: bool, default=False
        Whether to load dimensions from the command-line arguments.
        When enable, the prefix `--config_` is used.
    load_validate : bool, default=True
        Whether loaded variables should be validated.
    load_verbose : bool, default=False
        Whether details of the loading process should be printed to
        the standard output and set to the resulting object itself.
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
    sources: List[str] = []
    files: List[str] = []
    loaders: List[str] = []

    if load_env:
        sources.append('env')
        loaders.append('dynaconf.loaders.env_loader')

    if load_command_line:
        sources.append('command_line')
        loaders.append('project.config.loaders.command_line')

    if load_yaml:
        loaders.append('project.config.loaders.yaml')
        if load_command_line_dimensions:
            cli_dims = parse_keyword_args_as_dict(prefix='--project_')
            dimensions.update(cli_dims)
        files += _get_yaml_files(**dimensions)
        sources.append('yaml')

    if load_verbose:
        sys.stdout.write(f'Config sources: {", ".join(sources)}.\n')

    prefix = Environment.variable_prefix()
    config = Settings(
        validators=validators() if load_validate else None,
        CORE_LOADERS_FOR_DYNACONF=[],
        ENVIRONMENTS_FOR_DYNACONF=False,
        ENVVAR_PREFIX_FOR_DYNACONF=prefix,
        LOADERS_FOR_DYNACONF=loaders,
        MAIN_ENV_FOR_DYNACONF='',
        SETTINGS_FILE_FOR_DYNACONF=files,
        SILENT_ERRORS_FOR_DYNACONF=False,
    )

    if load_verbose:
        config.update(dict(loaded_sources=sources, loaded_files=files))

    try:
        # Force loading the configuration data, because the default lazy
        # behavior only loads at the first access.
        config.get('project', None)
    except ValidationError as err:
        fmt = ', '.join(sources)
        sys.stderr.write(
            f'CRITICAL: failed to read configuration {fmt}: {str(err)}.\n')
        raise

    return config


def as_dict(config: Settings) -> Dict[str, Any]:
    """Return mapping with configurations."""
    ignore = ('settings_module', 'settings_files_for_dynaconf',
              'environments', 'stream', 'envvar_prefix')
    config_dict = {k.lower(): v for k, v in config.as_dict().items()
                   if k.lower() not in ignore}
    return config_dict


def _get_yaml_files(**dimensions: str) -> List[str]:
    config = Environment.config_path()

    if not config.is_dir():
        if not config.exists():
            raise FileNotFoundError(
                'config path does not exist: ' + str(config))
        raise FileNotFoundError('config path is not a dir: ' + str(config))

    files = dict(project=config / 'project.yml')

    files.update(_dimensions_from_env(config))

    for dim, value in dimensions.items():
        new_value = config / f'{dim}-{value}.yml'
        existing_value = files.get(dim)
        if new_value == existing_value:
            continue

        files[dim] = new_value

    for dim, fname in dimensions.items():
        files[dim] = config / f'{dim}-{fname}.yml'

    for path in files.values():
        if not path.is_file():
            raise FileNotFoundError('missing configuration file ' + str(path))

    return [str(path) for path in files.values()]


def _dimensions_from_env(config: Path) -> Dict[str, Path]:
    prefix = 'PROJECT_DIMENSION_'
    prefix_len = len(prefix)
    result = dict()

    for name, value in os.environ.items():
        if not name.startswith(prefix):
            continue

        dim = name[prefix_len:].lower()
        result[dim] = config / f'{dim}-{value}.yml'

    return result


register_converters()
