from pathlib import Path
from typing import Optional
import logging

from dynaconf.base import Settings

from project.core.templates import render


class Reader:
    """Reader materializes configuration and resources files."""

    def __init__(self, config: Settings, base: Optional[str] = None) -> None:
        self.config = config
        if base is None:
            self.base = Path.cwd()
        else:
            self.base = Path(base)

    def read(self, fname: str) -> str:
        params = dict(config=self.config)
        with open(self.base / fname, 'rt') as input:
            return render(input.read(), params=params)


LOGGER = logging.getLogger(__name__)
