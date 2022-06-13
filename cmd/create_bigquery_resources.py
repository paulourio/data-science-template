"""Provision BigQuery resources.

The command-line arguments with prefix `--project_` are used as
dimension definitions for the configuration setup.

Usage:
 poetry run python cmd/create_bigquery_resources.py \
   --project_workspace dev --project_pipeline full --project_data bigquery
"""
import logging

from project.bigquery.operation import CreateTableOp
from project.bigquery.tables import ManagedTable
import project


def create_resources():
    config = project.load_config(load_command_line_dimensions=True)
    for name, spec in config.tables.items():
        LOGGER.debug('Loading %s %r', name, dict(spec))
        table = project.bigquery.tables.from_config(config, spec)
        if isinstance(table, ManagedTable):
            op = CreateTableOp(table)
            op.execute()


LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':
    project.init()
    create_resources()
