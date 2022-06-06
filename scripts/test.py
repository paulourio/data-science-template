import project
import logging


def run():
    config = project.init(logging='local', workspace='dev')

    _LOGGER.info('%r', config.as_dict())
    _LOGGER.info('%r', config.project)
    _LOGGER.info('%r', config.project.name)
    _LOGGER.info('%r', config.logging)


_LOGGER = logging.getLogger(__name__)

run()
