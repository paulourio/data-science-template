import project
import logging


def run():
    config = project.init(load_verbose=True)

    print(config.as_dict())

    project.config.export(
        config=config,
        entries=['project', 'labels', 'bigquery', 'storage'],
    )

    gcs = project.storage.client()
    bucket = gcs.bucket(config.storage.temp_bucket)
    print(list(bucket.list_blobs()))

    fs = project.storage.filesystem()
    print(fs.ls(f'gs://{config.storage.temp_bucket}'))

    bq = project.bigquery.client()
    print(list(bq.list_datasets()))

    _LOGGER.info('%r', config.as_dict())
    _LOGGER.info('%r', config.project)
    _LOGGER.info('%r', config.project.name)
    _LOGGER.info('%r', config.logging)


_LOGGER = logging.getLogger(__name__)

run()
