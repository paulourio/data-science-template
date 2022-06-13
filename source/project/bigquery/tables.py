"""BigQuery Tables."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import logging
import os

from dynaconf.base import Settings
from google.cloud.bigquery import DatasetReference, Table, TableReference
from project.config import Environment, load_config
import google.cloud.bigquery
import yaml


def from_config(config: Settings, spec: Dict[str, Any]):
    if spec['type'] == 'managed_table':
        return ManagedTable(labels=dict(config.labels), **spec)

    if spec['type'] == 'external_table':
        return ExternalTable(**spec)

    LOGGER.error('Unknown table specification: %r.', spec)
    raise ValueError('unknown table specification')


@dataclass
class Table:
    """BigQuery Table."""

    id: str
    type: str

    @property
    def project(self) -> str:
        """Return GCP project location."""
        return self.id.split('.')[0]

    @property
    def dataset(self) -> str:
        """Return BigQuery dataset location."""
        return self.id.split('.')[1]

    @property
    def name(self) -> str:
        """Return BigQuery table name."""
        return self.id.split('.')[2]

    def as_table_ref(self) -> TableReference:
        """Return as google's TableReference."""
        ref = TableReference(
            dataset_ref=DatasetReference(
                project=self.project,
                dataset_id=self.dataset,
            ),
            table_id=self.name,
        )
        return ref


@dataclass
class ExternalTable(Table):

    pass


@dataclass
class ManagedTable(Table):

    labels: Dict[str, str]
    properties_file: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def as_table(self) -> google.cloud.bigquery.Table:
        properties = self.properties.copy()
        for key in properties:
            if key not in KNOWN_FIELDS:
                LOGGER.warning(
                    'Unknown BigQuery Table property field %s in %s.',
                    key, self.properties_file,
                )
        properties['tableReference'] = self.as_table_ref().to_api_repr()
        properties['labels'] = self.labels
        return google.cloud.bigquery.Table.from_api_repr(properties)

    def __post_init__(self):
        config = Path(Environment.config_path())
        pfile = config / self.properties_file
        if not pfile.exists():
            raise FileNotFoundError(
                'properties file not found: ' + pfile.as_posix())

        with open(pfile.as_posix(), 'rt') as input:
            self.properties = yaml.safe_load(input)

        assert isinstance(self.labels, dict)
        assert isinstance(self.properties, dict)


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
