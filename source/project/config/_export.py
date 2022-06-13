from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Iterable, List, Optional, Tuple
from string import digits
import json

from dynaconf.base import Settings
from dynaconf.utils.parse_conf import parse_conf_data
from numpy import isnan

import logging

from ._environment import Environment


class ExportFormat(Enum):
    """Export format for configuration."""

    ENVIRONMENT_VARIABLES = auto()
    COMMAND_LINE_ARGUMENTS = auto()


def export(
    config: Settings,
    format: ExportFormat = ExportFormat.ENVIRONMENT_VARIABLES,
    entries: Optional[Iterable[str]] = None,
) -> Dict[str, str]:
    """Return exported configuration.

    Parameters
    ----------
    format : ExportFormat
        Set ExportFormat.ENVIRONMENT_VARIABLES to export as environment
        variables.
        Set ExportFormat.COMMAND_LINE_ARGUMENTS to export as command
        line arguments.
    entries : list, optional, default=all
        Selection of root keys that should be exported.

    Returns
    -------
    dict
        The dictionary of selected entries, or all of them, in the
        requested format.

    """
    exporter = ConfigExporter(config, entries)
    return exporter.export(format)


class ConfigExporter:
    """Export loaded configuration."""

    def __init__(self, config: Settings,
                 entries: Optional[Iterable[str]]) -> None:
        self.config = config
        self.entries = set(entries) if entries else set()
        self.vars: List[Variable] = []

    def export(self, format: ExportFormat) -> Dict[str, str]:
        """Return mapping with configuration exported to requested format."""
        self._export(self.config.as_dict(), [])
        if format == ExportFormat.ENVIRONMENT_VARIABLES:
            return dict(v.as_environment() for v in self.vars)
        if format == ExportFormat.COMMAND_LINE_ARGUMENTS:
            return dict(v.as_argument() for v in self.vars)
        raise ValueError('exported not supported for ' + str(format))

    def _export(self, mapping, path):
        if not mapping:
            # The dictionary is empty we still need to export it
            # as an empty dictionary.
            self.vars.append(Variable(path, mapping))
            return

        has_filters = not path and self.entries
        for key, value in mapping.items():
            if key == 'SETTINGS_FILES':
                continue
            if has_filters and key.lower() not in self.entries:
                continue
            if isinstance(value, dict):
                self._export(value, path + [key.lower()])
            else:
                self.vars.append(Variable(path + [key.lower()], value))


@dataclass
class Variable:
    """Configuration variable formatter for exporting."""

    path: List[str]
    value: Any

    def as_environment(self) -> Tuple[str, str]:
        """Return tuple (name, value) to set as an environment variable."""
        prefix = Environment.variable_prefix().upper() + '_'
        key = prefix + '__'.join(self.path)
        fmt = self._formatted_value()
        return (key, fmt)

    def as_argument(self) -> Tuple[str, str]:
        """Return tuple (name, value) to set as an command line argument."""
        prefix = Environment.variable_prefix().lower() + '_'
        key = prefix + '__'.join(self.path)
        fmt = self._formatted_value()
        return ('--' + key.lower(), fmt)

    def _formatted_value(self) -> str:
        validate_type = True
        if self.value is None:
            fmt = '@json null'
        elif isinstance(self.value, bool):
            fmt = f'{_json_dumps(self.value)}'
        elif isinstance(self.value, int):
            fmt = f'{self.value}'
            if not _test_parsing(fmt, self.value):
                fmt = '@int ' + fmt
        elif isinstance(self.value, float):
            fmt = f'{self.value}'
            if not _test_parsing(fmt, self.value):
                fmt = '@float ' + fmt
        elif isinstance(self.value, (dict, list)):
            fmt = f'@json {_json_dumps(self.value)}'
            validate_type = False
        elif isinstance(self.value, str):
            # If the string contents looks like a JSON list or object,
            # we need to escape it to guarantee dynaconf will read it
            # deserialize the value as string.
            fmt = str(self.value)
            if not _test_parsing(fmt, self.value):
                LOGGER.debug(
                    'Invalid round-trip of %r encoded as %r, trying quoted.',
                    self.value, fmt)
                fmt = f'{_json_dumps(self.value)}'
                if not _test_parsing(fmt, self.value):
                    LOGGER.debug(
                        ('Invalid round-trip of %r encoded as %r, '
                         'trying JSON.'),
                        self.value, fmt)
                    fmt = f'@json {_json_dumps(self.value)}'
            validate_type = False
        else:
            fmt = str(self.value)

        if not _test_parsing(fmt, self.value, validate_type=validate_type):
            parsed, ok = _maybe_parse(fmt)
            parsed_type = type(parsed).__name__
            if ok:
                parsed_info = f'{parsed!r} (type {parsed_type})'
            else:
                parsed_info = parsed
            LOGGER.error(
                ('Internal error when trying to export path %s '
                 'with data %r (type %s). Exported value %r is '
                 'parsed as %s.'),
                self.path,
                self.value, type(self.value).__name__, fmt,
                parsed_info,
            )
            raise RuntimeError('failed to export data')

        return fmt


def _json_dumps(obj):
    return json.dumps(obj, separators=(',', ':'))


def _test_parsing(serialized: str, expected: Any,
                  validate_type: bool = False) -> bool:
    # TOML decoder has some bugs when processing escaped sequences, and
    # we need to wrap around those unhandled errors.
    try:
        result = parse_conf_data(serialized, tomlfy=True)
    except IndexError as err:
        LOGGER.debug('TOML cannot parse serialized data %r into %r: %s.',
                     serialized, expected, str(err))
        return False
    else:
        value_ok = result == expected
        type_ok = True
        if validate_type:
            type_ok = type(result) == type(expected)
            if type_ok and not value_ok and isinstance(result, float):
                value_ok = isnan(result) and isnan(expected)
        return type_ok and value_ok


def _maybe_parse(serialized: str) -> Tuple[str, bool]:
    try:
        result = parse_conf_data(serialized, tomlfy=True)
    except IndexError as err:
        return f'<FAILED: {str(err)}>', False
    else:
        return result, True


LOGGER = logging.getLogger(__name__)
