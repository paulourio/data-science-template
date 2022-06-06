from enum import Enum, auto
import os


class ConfigFormat(Enum):
    """Enum for external configuration format sources and targets."""

    YAML_FILES = auto()
    """Configuration in YAML files."""

    ENVIRONMENT_VARIABLES = auto()
    """Configuration as environment variables."""

    COMMAND_LINE_ARGUMENTS = auto()
    """Configuration as command-line arguments."""

    @classmethod
    def default(cls):
        """Return the default configuration format."""
        fmt = os.environ['CONFIG_FORMAT']
        if fmt == 'ENVIRONMENT_VARIABLES':
            return cls.ENVIRONMENT_VARIABLES
        if fmt == 'YAML_FILES':
            return cls.YAML_FILES
        if fmt == 'COMMAND_LINE_ARGUMENTS':
            return cls.COMMAND_LINE_ARGUMENTS
        raise RuntimeError('unknown CONFIG_FORMAT ' + str(fmt))
