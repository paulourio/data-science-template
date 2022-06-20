from typing import Any, Dict, Optional

from project.bigquery.templates import routine_id


class BookmarkManager:
    """Manager of the pipeline's incremental processing bookmarks."""

    def __init__(self, context: Dict[str, Any]) -> None:
        self._config = context['config']
        self._step = context['step']
        self._context = context
        self._open = routine_id(self._config.routines.bookmark['open'])
        self._close = routine_id(self._config.routines.bookmark['close'])
        self._get = routine_id(self._config.routines.bookmark['get'])
        self._correlation_id = str(context['correlation_id'])

    def get_tstamp(self, bookmark_name: str, output_var_name: str) -> str:
        args = [
            repr(self._step['name']),  # step_name (IN)
            repr(bookmark_name),       # bookmark_name (IN)
            'NULL',                    # id (OUT)
            output_var_name,           # tstamp
        ]
        return f'CALL `{self._get}`({", ".join(map(str, args))});'

    def open(self, bookmark_name: str, id: str = None, tstamp: str = None,
             entry_id: str = None) -> str:
        args = [
            repr(self._step['name']),      # step_name (IN)
            repr(bookmark_name),           # bookmark_name (IN)
            id if id else 'NULL',          # id (IN)
            tstamp if tstamp else 'NULL',  # tstamp (IN),
            repr(self._correlation_id),    # correlation_id (IN)
            entry_id,                      # entry_id (OUT)
        ]
        return f'CALL `{self._open}`({", ".join(map(str, args))});'

    def close(self, *args):
        return f'CALL `{self._close}`({", ".join(map(str, args))});'
