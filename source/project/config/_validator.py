from functools import reduce
from typing import Final, Iterable, List

from dynaconf.validator import Validator


def validators() -> List[Validator]:
    """Return list of all validators."""
    return _logging_validators() + _storage_validators()


def _logging_validators() -> List[Validator]:
    return [
        Validator(
            'logging.type',
            'logging.level',
            'logging.message_format',
            'logging.timestamp_format',
            'logging.loggers',
            must_exist=True,
        ),
        Validator(
            'logging.type',
            must_exist=True,
            is_in=_LOGGING_TYPES,
        ),
        Validator(
            'logging.level',
            must_exist=True,
            is_in=_LOGGING_LEVELS,
        ),
        Validator(
            r'^logging.loggers.',
            is_in=_LOGGING_LEVELS,
            is_type_of=list,
        ),
    ]


def _storage_validators() -> List[Validator]:
    return [
        Validator(
            'storage.scopes',
            is_type_of=list,
        ),
        _each_item_is_one_of(
            'storage.scopes',
            is_in=_STORAGE_SCOPES,
        ),
        Validator(
            'storage.temp_bucket',
            must_exist=True,
            is_type_of=str,
        ),
        Validator(
            'storage.cache_bucket',
            must_exist=True,
            is_type_of=str,
        ),
        Validator(
            'storage.authentication',
            must_exist=True,
            is_in=('default', 'metadata'),
        ),
    ]


def _each_item_is_one_of(name: str, is_in: Iterable[str]) -> Validator:
    expr = reduce(
        lambda a, b: a | b,
        [
            Validator(name, must_exist=True, cont=value)
            for value in is_in
        ],
    )
    return expr


_LOGGING_TYPES: Final = ('default', 'colored', 'google')
"""Domain for logging types."""

_LOGGING_LEVELS: Final = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
"""Domain for logging levels."""

_STORAGE_SCOPES: Final = (
    'https://www.googleapis.com/auth/devstorage.read_only',
    'https://www.googleapis.com/auth/devstorage.read_write',
    'https://www.googleapis.com/auth/devstorage.full_control',
)
"""Allowed storage scopes."""
