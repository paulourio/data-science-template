from typing import Any, Dict, List
from pathlib import Path
import logging
import sys

from dynaconf.base import Settings
from dynaconf.validator import ValidationError

from project.cli.parser import parse_keyword_args_as_dict
from ._environment import Environment
from ._validator import validators


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

    Dimensions that are not specified are inferred from the context:

    - workspace: value in environment variable PROJECT_WORKSPACE.
    - logging: value in environment variable PROJECT_LOGGING.

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
    config = Path.cwd() / Environment.config_path()

    if not config.is_dir():
        if not config.exists():
            raise FileNotFoundError(
                'config path does not exist: ' + str(config))
        raise FileNotFoundError('config path is not a dir: ' + str(config))

    required_dimensions = {
        'workspace': _infer(config, 'workspace'),
        'logging': _infer(config, 'logging'),
    }

    other_dimensions: Dict[str, Path] = {}

    files: List[Path] = [config / 'project.yml']

    for key, value in dimensions.items():
        path = config / f'{key}-{value}.yml'
        if key in required_dimensions:
            required_dimensions[key] = path
        else:
            other_dimensions[key] = path

    files += required_dimensions.values()
    files += other_dimensions.values()

    for path in files:
        if not path.is_file():
            raise FileNotFoundError('missing configuration file ' + str(path))

    return [str(path) for path in files]


def _infer(path: Path, key: str) -> Path:
    if key == 'workspace':
        return _infer_workspace(path)
    if key == 'logging':
        return _infer_logging(path)
    raise ValueError('no inference for ' + str(key))


def _infer_workspace(path: Path) -> Path:
    workspace = Environment.workspace()
    return path / f'workspace-{workspace}.yml'


def _infer_logging(path: Path) -> Path:
    logging_name = Environment.logging()
    return path / f'logging-{logging_name}.yml'
