from typing import Final
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
    def config_path() -> str:
        """Return the relative path where YAML files are located."""
        return os.environ.get('PROJECT_CONFIG_PATH', _DEFAULT_CONFIG_PATH)

    @staticmethod
    def variable_prefix() -> str:
        """Return the environment variable name prefix."""
        return os.environ.get('PROJECT_VARIABLE_PREFIX',
                              _DEFAULT_VARIABLE_PREFIX)

    @staticmethod
    def workspace() -> str:
        """Return the workspace setting from the environment."""
        return os.environ['PROJECT_WORKSPACE']

    @staticmethod
    def logging() -> str:
        """Return the logging setting from the environment."""
        return os.environ['PROJECT_LOGGING']


def _env_as_bool(value: str) -> bool:
    if value == 'false':
        return False
    if value == 'true':
        return True
    raise ValueError('boolean must be "false" or "true", got ' + str(value))


_DEFAULT_VARIABLE_PREFIX: Final = 'app'

_DEFAULT_CONFIG_PATH: Final = 'config'
