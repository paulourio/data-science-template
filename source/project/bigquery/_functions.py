"""Template functions."""
from typing import Any

import google.cloud.bigquery


def make_identifier(obj: Any) -> str:
    """Return Standard SQL identifier."""
    if isinstance(obj, str):
        return _make_id(obj)

    if isinstance(obj, google.cloud.bigquery.Table):
        return _make_id(obj.full_table_id)

    raise NotImplementedError()


def _make_id(obj: str) -> str:
    if '`' in obj:
        raise ValueError('character "`" not allowed in identifiers')
    return f'`{obj}`'
