"""Dump the configuration file.

The command-line arguments with prefix `--project_` are used as
dimension definitions for the configuration setup.
Output is written to data/dumped_config.yml.

Usage:
 poetry run python cmd/dump_config.py --project_pipeline full
"""
import logging

import project


def export_config():
    config = project.load_config(load_command_line_dimensions=True,
                                 load_verbose=True)

    data = project.config.as_dict(config)

    loaded_files = list(config.loaded_files)
    LOGGER.info('Loaded files: %r', loaded_files)

    fname = project.config.Environment.data_path() / 'dumped_config.yml'
    with open(fname.as_posix(), 'wt') as out:
        out.write('---\n')
        project.core.yaml.dump(data, out)

    LOGGER.info('Output written to %s.', fname)


LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    project.init()
    export_config()
