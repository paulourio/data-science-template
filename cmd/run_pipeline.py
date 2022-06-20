"""Provision BigQuery resources.

The command-line arguments with prefix `--project_` are used as
dimension definitions for the configuration setup.

Usage:
 poetry run python cmd/create_bigquery_resources.py \
   --project_workspace dev --project_pipeline full --project_data bigquery
"""
import logging

from project.bigquery.operations import RunQueryOp
from project.pipeline.step import BigQueryStep, IncrementalBigQueryStep
import project


def run_pipeline():
    config = project.load_config(load_command_line_dimensions=True)
    context = project.pipeline.make_context(config=config)

    for spec in config.pipeline.steps:
        spec_context = context.with_values(step=spec)
        step = project.pipeline.step.from_config(spec_context, spec)
        step_context = context.with_values(step=step)

        LOGGER.debug('Loaded step %r.', step)
        if isinstance(step, BigQueryStep):
            op = RunQueryOp(step_context, step.query)
            # op.execute()
        elif isinstance(step, IncrementalBigQueryStep):
            op = RunQueryOp(step_context, step.update)
            op.execute()


LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':
    project.init()
    run_pipeline()
