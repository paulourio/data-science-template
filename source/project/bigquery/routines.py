"""BigQuery procedures."""
from dataclasses import dataclass, field
from typing import Any, Dict
import logging

from dynaconf.base import Settings
from google.cloud.bigquery import RoutineReference
from google.cloud import bigquery

import project

from ._templates import render


def from_config(config: Settings, spec: Dict[str, Any]):
    routine_type = spec['type']
    params = spec.get('params', dict())

    try:
        if routine_type in ('stored_procedure', 'scalar_function'):
            return ManagedRoutine.from_spec(config, routine_type, params)

        raise NotImplementedError('no implementation for ' + routine_type)
    except Exception as err:
        LOGGER.error('Failed to initialize routine from spec %r: %s.',
                     spec, str(err))
        raise ValueError('failed to initialize routine') from err


@dataclass
class Routine:

    type: str
    params: Dict[str, Any] = field(repr=False)


@dataclass
class ManagedRoutine(Routine):
    """Routine managed by this project."""

    properties: Dict[str, Any] = field(repr=False)

    @classmethod
    def from_spec(cls, config: Settings, type_: str, params: Dict[str, Any]):
        params = params.copy()

        properties = params['properties']
        if not hasattr(properties, 'items'):
            rtype = type(properties).__name__
            raise TypeError('properties must be dict-like, got ' + rtype)

        body = properties['definitionBody']
        if body.startswith('@template_file'):
            fname = body.split(' ')[-1]
            LOGGER.debug('Reading template file %s.', fname)
            with open(fname, 'rt') as input:
                body = render(input.read(), params=dict(config=config))

        body = project.core.templates.render(body, params=dict(config=config))
        properties['definitionBody'] = body

        return cls(type=type_, params=params, properties=properties)

    @property
    def id(self):
        """Return the Standard SQL full table id."""
        ref = self.routine_ref()
        project, dataset, routine = (
            ref.project, ref.dataset_id, ref.routine_id
        )
        return f'{project}.{dataset}.{routine}'

    def as_routine(self) -> bigquery.Routine:
        """Return as Google's Routine."""
        return bigquery.Routine.from_api_repr(self.properties)

    def routine_ref(self) -> RoutineReference:
        """Return as Google's RoutineReference."""
        return self.as_routine().reference

    def __repr__(self):
        return f'ManagedRoutine({self.id})'


LOGGER = logging.getLogger(__name__)
