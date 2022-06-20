from itertools import islice
from typing import Any, Dict, Final, List
import logging
import sys

from dynaconf.base import Settings
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from prettydiff import print_diff
from tabulate import tabulate

import project
from .tables import ManagedTable
from .routines import ManagedRoutine


class CreateTableOp:
    """Create table operation."""

    def __init__(self, table: ManagedTable) -> None:
        self.table = table

    def execute(self):
        """Create or update table."""
        client = project.bigquery.client()
        table = self.table.as_table()
        try:
            existing = client.get_table(table)
        except NotFound:
            client.create_table(table)
            LOGGER.info('Created table %s.', self.table.id)
        else:
            existing_repr = _table_to_api_repr(existing)
            expected_repr = _table_to_api_repr(table)
            if existing_repr == expected_repr:
                LOGGER.debug('Table %s is up-to-date.', self.table.id)
                return

            print_diff(existing_repr, expected_repr)
            LOGGER.info('Updating %s in place.', self.table.id)

            client.update_table(table, fields=TABLE_UPDATE_FIELDS)

    def __repr__(self):
        return f'CreateTableOp({self.table})'


class CreateRoutineOp:
    """Create routine operation."""

    def __init__(self, routine: ManagedRoutine) -> None:
        self.routine = routine

    def execute(self):
        """Create or update table."""
        client = project.bigquery.client()
        routine = self.routine.as_routine()
        try:
            existing = client.get_routine(routine)
        except NotFound:
            client.create_routine(routine)
            LOGGER.info('Created routine %s.', self.routine.id)
        else:
            existing_repr = _routine_to_api_repr(existing)
            expected_repr = _routine_to_api_repr(routine)
            if existing_repr == expected_repr:
                LOGGER.debug('Routine %s is up-to-date.', self.routine.id)
                return

            print_diff(existing_repr, expected_repr)

            if self.routine.type == 'stored_procedure':
                fields = PROCEDURE_UPDATE_FIELDS
            elif self.routine.type == 'scalar_function':
                fields = FUNCTION_UPDATE_FIELDS
            elif self.routine.type == 'table_valued_function':
                fields = TVF_UPDATE_FIELDS
            else:
                raise ValueError(
                    'unknown routine type' + str(self.routine.type))

            client.update_routine(routine, fields=fields)
            LOGGER.info('Updated %s in place.', self.routine.id)

    def __repr__(self):
        return f'CreateRoutineOp({self.table})'


class RunQueryOp:

    def __init__(self, config: Settings, query: str) -> None:
        self.config = config
        self.query = query

    def execute(self):
        MAX_ROWS = 20
        client = project.bigquery.client()
        LOGGER.debug('Running job %r', self.query)
        job = client.query(
            query=self.query,
            location=self.config.bigquery.location,
            job_id_prefix=self.config.bigquery.job_id_prefix,
        )
        LOGGER.debug('Waiting job %r', self.query)
        result = job.result()
        if result.total_rows > MAX_ROWS:
            LOGGER.warning(
                'Result size has %d records. Showing the first %d rows.',
                result.total_rows, MAX_ROWS)
        elif result.total_rows > 0:
            LOGGER.debug('Result size has %d records.', result.total_rows)
        else:
            LOGGER.debug('Finished running, empty result set.')
        if result.total_rows:
            rows = islice(result, MAX_ROWS)
            sys.stdout.write(
                tabulate(
                    tabular_data=[row.values() for row in rows],
                    headers=[f.name for f in result.schema],
                    tablefmt='psql',
                )
            )


def _table_to_api_repr(table: bigquery.Table) -> Dict[str, Any]:
    api_repr = {
        key: value
        for key, value in table.to_api_repr().items()
        if key in TABLE_TRACKING_FIELDS
    }
    return api_repr


def _routine_to_api_repr(table: bigquery.Table) -> Dict[str, Any]:
    api_repr = {
        key: value
        for key, value in table.to_api_repr().items()
        if key in TABLE_TRACKING_FIELDS
    }
    return api_repr


LOGGER = logging.getLogger(__name__)

ROUTINE_TRACKING_FIELDS: Final[List[str]] = [
    'routineType', 'language', 'arguments', 'returnType',
    'returnTableType', 'importedLibraries', 'definitionBody',
    'description', 'determinismLevel',
]

PROCEDURE_UPDATE_FIELDS: Final[List[str]] = [
    'routineType', 'language', 'arguments', 'definitionBody', 'description',
]

FUNCTION_UPDATE_FIELDS: Final[List[str]] = [
    'routineType', 'language', 'arguments', 'importedLibraries',
    'definitionBody', 'description', 'determinismLevel',
]

TVF_UPDATE_FIELDS: Final[List[str]] = [
    'routineType', 'language', 'arguments', 'returnType',
    'returnTableType', 'definitionBody', 'description',
]

TABLE_TRACKING_FIELDS: Final[List[str]] = [
    'description', 'friendlyName', 'labels', 'schema', 'timePartitioning',
    'rangePartitioning', 'clustering', 'requirePartitionFilter',
    'expiration_timestamp', 'location',
]

TABLE_UPDATE_FIELDS: Final[List[str]] = [
    'description', 'friendly_name', 'labels', 'schema',
    'time_partitioning', 'range_partitioning',
    'clustering_fields', 'require_partition_filter',
    'expires', 'location',
]
