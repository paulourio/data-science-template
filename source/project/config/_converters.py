from typing import Any

from dynaconf.utils.parse_conf import (
    BaseFormatter, converters, parse_conf_data,
)
import yaml


def _read_yaml_file(value: str) -> Any:
    loaded = yaml.safe_load(_read_file(value))
    return parse_conf_data(loaded)


def _read_file(value: str, **context) -> str:
    with open(value, 'rt') as input:
        return input.read()


YAMLFileConverter = BaseFormatter(_read_yaml_file, '@yaml_file')
"""Implementation for the @yaml_file token."""


def register_converters() -> None:
    """Register converters in Dynaconf."""
    # Dynaconf does not provide a decent API to register new converters,
    # hence we manually change the converters dictionary
    # `dynaconf.utils.parse_conf.converters`.
    converters['@yaml_file'] = YAMLFileConverter
