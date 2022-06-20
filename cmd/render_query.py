"""Provision BigQuery resources.

The command-line arguments with prefix `--project_` are used as
dimension definitions for the configuration setup.

Usage:
 poetry run python cmd/create_bigquery_resources.py \
   --project_workspace dev --project_pipeline full --project_data bigquery
"""
from pathlib import Path
import os
import logging

from project.bigquery.operations import RunQueryOp
from project.pipeline.step import BigQueryStep, IncrementalBigQueryStep
import project


def render_pipeline():
    config = project.load_config(load_command_line_dimensions=True)
    context = project.pipeline.make_context(config=config)
    data = Path(config.data_path) / 'rendered'

    for spec in config.pipeline.steps:
        step_context = context.with_values(step=spec)
        bookmarks = project.pipeline.bookmarks.BookmarkManager(step_context)
        step_context = step_context.with_values(bookmarks=bookmarks)
        step = project.pipeline.step.from_config(step_context, spec)
        LOGGER.debug('Loaded step %r.', step)
        if isinstance(step, BigQueryStep):
            fname = data / f'{step.name}.bql'
            _out(fname, step.query)
        elif isinstance(step, IncrementalBigQueryStep):
            fname = data / f'{step.name}-update.bql'
            _out(fname, step.update)
            fname = data / f'{step.name}-validate.bql'
            _out(fname, step.validate)
            fname = data / f'{step.name}-reset.bql'
            _out(fname, step.reset)


def _out(path: Path, content: str) -> None:
    encoded = content.encode()
    if not encoded:
        LOGGER.warning('No bytes to write to %s.', path.as_posix())
        if path.exists():
            os.remove(path)
            LOGGER.debug('Deleted existing %s.', path.as_posix())
        return

    os.makedirs(os.path.dirname(path.as_posix()), exist_ok=True)
    with open(path, 'wb') as output:
        output.write(
            b'RAISE USING MESSAGE = '
            b"'DO NOT RUN OR EDIT THIS FILE DIRECTLY!';\n\n")
        output.write(encoded)
    LOGGER.debug('Written %d bytes to %s.', len(encoded), path.as_posix())


LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':
    project.init()
    render_pipeline()
