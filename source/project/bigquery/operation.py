from cmath import exp
from dataclasses import dataclass
from typing import Any, Dict, Final, List
import logging

from google.api_core.exceptions import NotFound
from prettydiff import print_diff
import google.cloud.bigquery
import project

from .tables import ManagedTable


@dataclass
class CreateTableOp:
    """Create table operation."""

    table: ManagedTable

    def execute(self):
        client = project.bigquery.client()
        table = self.table.as_table()
        try:
            existing = client.get_table(table)
        except NotFound:
            client.create_table(table)
            LOGGER.info('Created table %s.', self.table.id)
        else:
            existing_repr = _to_api_repr(existing)
            expected_repr = _to_api_repr(table)
            if existing_repr == expected_repr:
                LOGGER.debug('Table %s is up-to-date.', self.table.id)
                return

            print_diff(existing_repr, expected_repr)
            LOGGER.info('Updating %s in place.', self.table.id)

            client.update_table(table, fields=UPDATE_FIELDS)


def _to_api_repr(table: google.cloud.bigquery.Table) -> Dict[str, Any]:
    api_repr = {
        key: value
        for key, value in table.to_api_repr().items()
        if key in TRACKING_FIELDS
    }
    return api_repr


LOGGER = logging.getLogger(__name__)

TRACKING_FIELDS: Final[List[str]] = [
    'description', 'friendlyName', 'labels', 'schema', 'timePartitioning',
    'rangePartitioning', 'clustering', 'requirePartitionFilter',
    'expiration_timestamp', 'location',
]

UPDATE_FIELDS: Final[List[str]] = [
    'description', 'friendly_name', 'labels', 'schema',
    'time_partitioning', 'range_partitioning',
    'clustering_fields', 'require_partition_filter',
    'expires', 'location',
]
