from dataclasses import dataclass, field
from typing import Any, Dict, List, Set
import logging
import re

from project.bigquery.templates import render
from project.core.context import Context


def from_config(ctx: Context, spec: Dict[str, Any]) -> 'Step':
    try:
        step_type = spec['type']
        step = dict(
            name=spec['name'],
            tags=spec['tags'],
            depends_on=spec['depends_on'],
            type=spec['type'],
            params=spec['params'],
        )

        if step_type == 'bigquery':
            return BigQueryStep.from_spec(ctx, step, spec['params'])

        if step_type == 'incremental_bigquery':
            return IncrementalBigQueryStep.from_spec(
                ctx, step, spec['params'])

        raise NotImplementedError('no implementation for ' + str(spec))
    except Exception as err:
        LOGGER.error('Failed to initialize step from spec %r: %s',
                     spec, str(err))
        raise ValueError('failed to initialize step from spec') from err


@dataclass
class Dependency:

    params: Dict[str, Any]

    @classmethod
    def from_spec(cls, ctx: Context, params: Dict[str, Any]):
        dep = Dependency(
            params=dict(params),
        )
        return dep


@dataclass
class Step:

    name: str
    type: str
    tags: Set[str]
    params: Dict[str, Any]
    depends_on: List[Dependency]

    @classmethod
    def from_spec(cls, ctx: Context, params: Dict[str, Any]):
        config = ctx['config']
        dep = cls(
            name=config.name,
            tags=set(config.tags),
            type=config.type,
            params=dict(config.params),
            depends_on=[
                Dependency.from_config(spec)
                for spec in config.depends_on
            ],
        )
        return dep

    def __post_init__(self):
        if not STEP_NAME_PATTERN.match(self.name):
            msg = 'Step name %r does not match %r.'
            if '_' in self.name:
                msg += (' Step names cannot contain underscores, '
                        'replace by hyphens.')

            LOGGER.critical(msg, self.name, STEP_NAME_PATTERN)
            raise ValueError('invalid step name')


@dataclass
class BigQueryStep(Step):

    query: str = field(repr=False)

    @classmethod
    def from_spec(cls, ctx: Context, step: Dict[str, Any],
                  params: Dict[str, Any]):
        query = _read_content(ctx, params.query)
        return cls(query=query, **step)


@dataclass
class IncrementalBigQueryStep(Step):

    reset: str
    update: str
    validate: str

    @classmethod
    def from_spec(cls, ctx: Context, step: Dict[str, Any],
                  params: Dict[str, Any]):
        reset = _read_content(ctx, params['reset'])
        update = _read_content(ctx, params['update'])
        validate = _read_content(ctx, params['validate'])
        return cls(reset=reset, update=update, validate=validate, **step)


def _read_content(ctx: Context, value: str) -> str:
    if not value.startswith('@template_file'):
        return value

    fname = value.split(' ')[-1]
    LOGGER.debug('Reading template file %s.', fname)

    LOGGER.debug('Context: %r.', ctx)

    params = dict(
        context=ctx,
        config=ctx['config'],
        step=ctx['step'],
        bookmarks=ctx['bookmarks'],
    )
    LOGGER.debug('Params: %r.', params)

    with open(fname, 'rt') as input:
        return render(input.read(), params=params)


LOGGER = logging.getLogger(__name__)

STEP_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9\-]*[a-z0-9]$')
