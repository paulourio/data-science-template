"""Provision BigQuery resources.

The command-line arguments with prefix `--project_` are used as
dimension definitions for the configuration setup.

Usage:
 poetry run python cmd/create_bigquery_resources.py \
   --project_workspace dev --project_pipeline full --project_data bigquery
"""
from typing import Any, Iterator, Mapping, Tuple
import logging

from project.bigquery.operations import CreateTableOp, CreateRoutineOp
from project.bigquery.tables import ManagedTable
from project.bigquery.routines import ManagedRoutine
import project


def create_resources():
    config = project.load_config(load_command_line_dimensions=True)

    for _, spec in _find(config.tables):
        table = project.bigquery.tables.from_config(config, spec)
        LOGGER.debug('Loaded table %r.', table)
        if isinstance(table, ManagedTable):
            op = CreateTableOp(table)
            op.execute()

    for _, spec in _find(config.routines):
        routine = project.bigquery.routines.from_config(config, spec)
        LOGGER.debug('Loaded routine %r.', routine)
        if isinstance(routine, ManagedRoutine):
            op = CreateRoutineOp(routine)
            op.execute()


def _find(map: Mapping) -> Iterator[Tuple[str, Mapping[str, Any]]]:
    # Find resource definitions in a nested structure.
    # All dictionaries with `type` entry are yielded.
    for key, value in map.items():
        if isinstance(value, dict) and 'type' in value:
            yield (key, value)
        else:
            yield from _find(value)


LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':
    project.init()
    create_resources()
