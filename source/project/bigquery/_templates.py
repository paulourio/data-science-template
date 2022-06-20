from functools import wraps
from typing import Any, Callable, Dict, Mapping
import logging

import project


def render(content: str, params: Dict[str, Any]) -> str:
    result = project.core.templates.render(
        content=content,
        params=params,
        globals=dict(
            table_id=table_id,
            routine_id=routine_id,
        )
    )
    return result


def log_spec_on_error(fn: Callable) -> Callable:
    """Wraps a function to log the spec parameter on error."""

    @wraps(fn)
    def wrapper(spec: Mapping):
        try:
            return fn(spec)
        except Exception as err:
            LOGGER.error(
                'Failed to compute %s with spec %r: %s',
                fn.__name__, spec, str(err)
            )
            raise err

    return wrapper


@log_spec_on_error
def table_id(spec: Mapping[str, str]) -> str:
    """Return fully qualified table identifier."""
    ref = spec['params']['properties']['tableReference']

    project_id = ref['projectId']
    dataset_id = ref['datasetId']
    table_id = ref['tableId']

    return f'{project_id}.{dataset_id}.{table_id}'


@log_spec_on_error
def routine_id(spec: Mapping[str, str]) -> str:
    """Return fully qualified table identifier."""
    ref = spec['params']['properties']['routineReference']

    project_id = ref['projectId']
    dataset_id = ref['datasetId']
    routine_id = ref['routineId']

    return f'{project_id}.{dataset_id}.{routine_id}'


LOGGER = logging.getLogger(__name__)
