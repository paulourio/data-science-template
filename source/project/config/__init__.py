"""Project configuration.

This module wraps around Dynaconf to provide configuration for use
in a development and production environments.

Dynaconf has several inconsistencies.
For example, to define which files should be processed, all of

    - settings_files,
    - settings_module,
    - SETTINGS_FILE_FOR_DYNACONF, and
    - SETTINGS_FILES_FOR_DYNACONF,

are used in messy ways by Dynaconf, and we basically need to control all
of them to avoid unexpected results.

We also cannot use dynaconf.Dynaconf directly as it works like a global
singleton, and we rather use dynaconf.base.Settings directly.
"""
# flake8: noqa
from . import loaders
from ._types import ConfigFormat
from ._config import load_config, as_dict
from ._exporter import export_config
