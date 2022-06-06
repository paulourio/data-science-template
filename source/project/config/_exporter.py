from curses.ascii import isdigit
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import json

from dynaconf.base import Settings

from ._config import ENVVAR_PREFIX
from ._types import ConfigFormat


def export_config(
    config: Settings,
    format: ConfigFormat = ConfigFormat.ENVIRONMENT_VARIABLES,
    entries: Optional[Iterable[str]] = None,
) -> Dict[str, str]:
    exporter = ConfigExporter(config, entries)
    return exporter.export(format)


class ConfigExporter:
    """Export loaded configuration."""

    def __init__(self, config: Settings,
                 entries: Optional[Iterable[str]]) -> None:
        self.config = config
        self.entries = set(entries) if entries else set()
        self.vars: List[Variable] = []

    def export(self, format: ConfigFormat):
        self._export(self.config.as_dict(), [])
        if format == ConfigFormat.ENVIRONMENT_VARIABLES:
            return dict(v.as_environment() for v in self.vars)
        if format == ConfigFormat.COMMAND_LINE_ARGUMENTS:
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

    path: List[str]
    value: Any

    def as_environment(self) -> Tuple[str, str]:
        key = ENVVAR_PREFIX + '_' + '__'.join(self.path)

        if self.value is None:
            fmt = '@json null'
        elif isinstance(self.value, bool):
            fmt = f'@bool {_json_dumps(self.value)}'
        elif isinstance(self.value, int):
            fmt = f'@int {self.value}'
        elif isinstance(self.value, float):
            fmt = f'@float {self.value}'
        elif isinstance(self.value, (dict, list)):
            fmt = f'@json {_json_dumps(self.value)}'
        elif isinstance(self.value, str):
            # If the string contents looks like a JSON list or object,
            # we need to escape it to guarantee dynaconf will read it
            # deserialize the value as string.
            to_escape = ['{', '[']
            if any(self.value.startswith(esc) for esc in to_escape):
                fmt = repr(self.value)
            elif self.value and isdigit(self.value[:1]):
                fmt = repr(self.value)
            else:
                fmt = str(self.value)
        else:
            fmt = str(self.value)

        return (key, fmt)

    def as_argument(self) -> Tuple[str, str]:
        key, value = self.as_environment()
        return ('--' + key, value)


def _json_dumps(obj):
    return json.dumps(obj, separators=(',', ':'))
