"""BigQuery Tables."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

from dynaconf.base import Settings
import google.cloud.bigquery

import project


def from_config(config: Settings, spec: Dict[str, Any]) -> 'Table':
    """Return Table from configuration specification."""
    table_type = spec['type']
    params = spec.get('params', dict())

    try:
        if table_type == 'managed_table':
            base = dict(
                labels=dict(config.labels),
                location=config.bigquery.location,
            )

            properties = spec['params']['properties']
            if not hasattr(properties, 'items'):
                ptype = type(properties).__name__
                raise TypeError('properties must be dict-like, got ' + ptype)

            properties = project.core.dictionary.merge(base, properties)
            params['properties'] = properties

            return ManagedTable.from_spec(config, type=table_type,
                                          params=params)

        if table_type == 'external_table':
            return ExternalTable(type=table_type, params=params)

        if table_type == 'public_table':
            return PublicTable(type=table_type, params=params)

        LOGGER.error('Unknown table specification: %r.', spec)
        raise ValueError('unknown table specification')
    except Exception as err:
        LOGGER.error('Failed to initialize table from spec %r: %s',
                     spec, str(err))
        raise ValueError('failed to initialize table from spec') from err


@dataclass
class Table:
    """BigQuery Table."""

    type: str = field(repr=False)
    params: Dict[str, Any] = field(repr=False)


@dataclass
class ExternalTable(Table):
    """External table definition."""

    partitioning_column: Optional[str] = None

    @classmethod
    def from_spec(cls, config: Settings, spec: Dict[str, Any]):
        pcol = spec.get('partitioning_column')
        return cls(**spec, partitioning_column=pcol)


@dataclass
class PublicTable(Table):
    """Table publicly managed by Google."""

    partitioning_column: Optional[str] = None

    @classmethod
    def from_spec(cls, config: Settings, params: Dict[str, Any]):
        partitioned_by = params.get('partitioning_column')
        return cls(**params, partitioning_column=partitioned_by)


@dataclass
class ManagedTable(Table):
    """Table managed by this project."""

    # location: str = field(repr=False)
    # labels: Dict[str, str] = field(repr=False)
    properties: Dict[str, Any] = field(repr=False)

    @classmethod
    def from_spec(cls, config: Settings, type: str, params: Dict[str, Any]):
        """Return table according to the configuration and specification."""
        params = params.copy()
        properties = params['properties']

        # default_project, default_dataset = config.bigquery.dataset.split('.')
        # ref = properties['tableReference']
        # ref['projectId'] = ref.get('projectId', default_project)
        # ref['datasetId'] = ref.get('datasetId', default_dataset)

        return cls(type=type, params=params, properties=properties)

    @property
    def id(self):
        """Return the Standard SQL full table id."""
        ref = self.table_ref()
        project, dataset, table = ref.project, ref.dataset_id, ref.table_id
        return f'{project}.{dataset}.{table}'

    def as_table(self) -> google.cloud.bigquery.Table:
        """Return as BigQuery Table."""
        properties = self.properties.copy()
        for key in properties:
            if key not in KNOWN_FIELDS:
                LOGGER.warning(
                    'Unknown BigQuery Table property field %s in %s.',
                    key, self.properties_file,
                )

        #properties['labels'] = self.labels
        #properties['location'] = self.location

        return google.cloud.bigquery.Table.from_api_repr(properties)

    def table_ref(self) -> google.cloud.bigquery.TableReference:
        data = self.properties['tableReference']
        return google.cloud.bigquery.TableReference.from_api_repr(data)

    def __repr__(self):
        return f'ManagedTable({self.id})'


LOGGER = logging.getLogger(__name__)

KNOWN_FIELDS = [
    'clustering',
    'description',
    'friendlyName',
    'labels',
    'location',
    'rangePartitioning',
    'requirePartitionFilter',
    'schema',
    'tableReference',
    'timePartitioning',
]
