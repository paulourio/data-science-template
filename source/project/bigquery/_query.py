from google.cloud.bigquery import Client


class BigQueryRunner:
    """Execute BigQuery queries."""

    def __init__(self, client: Client) -> None:
        self.client = client
