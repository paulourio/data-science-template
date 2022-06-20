from typing import Final
from pathlib import Path
import os


class Environment:
    """Environment settings."""

    @staticmethod
    def load_env() -> bool:
        """Return whether configuration should be loaded from environment."""
        return _env_as_bool(os.environ['PROJECT_LOAD_ENV'])

    @staticmethod
    def load_yaml() -> bool:
        """Return whether configuration should be loaded from YAML files."""
        return _env_as_bool(os.environ['PROJECT_LOAD_YAML'])

    @staticmethod
    def load_command_line() -> bool:
        """Return whether configuration should be loaded from environment."""
        return _env_as_bool(os.environ['PROJECT_LOAD_COMMAND_LINE'])

    @staticmethod
    def config_path() -> Path:
        """Return the relative path where YAML files are located."""
        config = os.environ.get('PROJECT_CONFIG_PATH', _DEFAULT_CONFIG_PATH)
        return Path.cwd() / config

    @staticmethod
    def data_path() -> Path:
        """Return the relative path where data files are located."""
        data = os.environ.get('PROJECT_DATA_PATH', _DEFAULT_DATA_PATH)
        return Path.cwd() / data

    @staticmethod
    def resources_path() -> Path:
        """Return the relative path where data resources are located."""
        resources = os.environ.get('PROJECT_RESOURCES_PATH',
                                   _DEFAULT_RESOURCES_PATH)
        return Path.cwd() / resources

    @staticmethod
    def variable_prefix() -> str:
        """Return the environment variable name prefix."""
        return os.environ.get('PROJECT_VARIABLE_PREFIX',
                              _DEFAULT_VARIABLE_PREFIX)


def _env_as_bool(value: str) -> bool:
    if value == 'false':
        return False
    if value == 'true':
        return True
    raise ValueError('boolean must be "false" or "true", got ' + str(value))


_DEFAULT_VARIABLE_PREFIX: Final = 'app'

_DEFAULT_CONFIG_PATH: Final = 'config'

_DEFAULT_DATA_PATH: Final = 'data'

_DEFAULT_RESOURCES_PATH: Final = 'resources'
