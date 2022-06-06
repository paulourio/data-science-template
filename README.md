# Project template

This is an example of how a project for data science might be organized.
This example is focused on working with Google Cloud Platform (GCP) services, while development
occurs in an interactive environment with access to editing Python files and Jupyter Notebooks.

## Structure

- `config/` — Collection of configuration files in YAML format.
- `source/` — Code common to many components of the project.  When a specific module uses code from the source, it should copy it to the Docker image.
- `scripts/` — General scripts for running specific tasks and helper tools for the project management.
- `beam/` — Code specific for running Apache Beam pipelines.
- `modeling/` — Code specific for modeling staging, typically code for the inference, optimization, and search of parameters and hyper-parameters. I separate it here because it runs as Vertex AI custom jobs.
- `analysis/` — Jupyter Notebooks, scripts, and ad-hoc queries used in analyses.
- `resources/` — Jinja2 template files rendered during configuration load.
- `data/` — Results and reports. This folder is actually a copy or a "symbolic" link to a remote storage, such a Google Cloud Storage. This data folder never contains the actual data used by ETLs or modeling.  At most only small samples are stored here for development of beam pipelines. In this folder we mostly write and read reports and results.

## Configuration

Configuration is centralized and organized by composable dimensions.
Different components are deployed in custom Docker images, which are configured with custom code.
When running Docker containers from these images, the configuration is passed either through environment variables or command-line arguments.

We wrap around the Dynaconf package to provide a nested configuration in development and production environments.

When working in development environments, configuration settings are loaded from YAML files organized in additive files.
Organize YAML files as independent dimensions — also called orthogonal files by the 12-factor methodology.

When running a production environment, no YAML files should be
deployed with the code, and the configuration will be read entirely
from environment variables or command-line arguments.

Example of how to organize YAML files into composable dimensions.
Consider the following dimensions:

| Dimension | Description |
| :--- | :--- |
| Workspace | Settings common to a single workspace, such as the infrastructure definitions.  May include Google Cloud identifiers such as project, bucket, VPC networks, and other configurations that would be stable within a single workspace. |
| Logging | Dimension with settings for logging. |
| Data | Dimension that maps data sources definitions. |
| Beam | Dimension with configuration for Apache Beam pipelines. |

Files for the some dimensions may have the same definitions of values.
For example, each file for the `data` dimension may have exactly the same keys, and only the values vary.
With the above dimensions we may have the following YAML file organization:

| Dimension | YAML File                   | Description |
| :---      | :---                        | :--- |
| Project   | `project.yml`               | Common definition for the entire project. |
| Workspace | `workspace-dev.yml`         | Configuration for development infrastructure. |
| Workspace | `workspace-prod.yml`        | Configuration for production infrastructure. |
| Logging   | `logging-local.yml`         | Logging configuration when running on an interactive environment. |
| Logging   | `logging-google.yml`        | Logging configuration when running on a VM with Google Agent that accepts Google Structured Logging. |
| Data      | `data-bigquery.yml`         | Definitions for full data in tables located on Google Cloud BigQuery. |
| Data      | `data-bigquery-sample.yml`  | Definitions for sampled data in tables located on Google Cloud Bigquery. |
| Data      | `data-storage-sample.yml`   | Definitions for sampled data in Parquet files located on Google Cloud Storage. |
| Beam      | `beam-local.yml`            | Definitions to run Apache Beam with Direct runner on a local environment. |
| Beam      | `beam-dataflow.yml`         | Definitions to run Apache Beam with Dataflow runner. |

Only one YAML file for each dimension can be loaded:

```python
import project

config = project.load_config(
    workspace='dev',
    logging='local',
    data='storage-sample',
    beam='local',
)
# Reads:
#   config/project.yml
#   config/workspace-dev.yml
#   config/logging-local.yml
#   config/data-storage-sample.yml
#   config/beam-local.yml
```

New dimensions can be added as necessary.

Required dimensions:

- Project — `config/project.yml` must be defined.
- Workspace — Falls back to value in environment variable `DEFAULT_PROJECT_WORKSPACE`.
- Logging — Falls back to value in environment variable `DEFAULT_PROJECT_LOGGING`.

## Production configuration

Depending on the deployment, the configuration may be passed either as environment variables (usually passed to a docker container) or command-line arguments (for example when running an Apache Beam pipeline).

Exporting a configuration as environment variables:

```python
from project.config import ConfigFormat, load_config, export_config

config = load_config(workspace='prod', logging='google', ...)
env = export_config(
    config=config,
    format=ConfigFormat.ENVIRONMENT_VARIABLES,
    entries=('project', 'storage', 'bigquery', 'labels'),  # Optional
)
# env: Dict[str, str
# Use env mapping to include as environment variables of your container.
```

Use `ConfigFormat.COMMAND_LINE_ARGUMENTS` to export for command-line arguments.

When running in a production environment, `load_config()` will determine  source of configuration from the value in environment variable `CONFIG_FORMAT`, but you may load it explicitly:

```python
from project.config import ConfigFormat, load_config

config = load_config(format=ConfigFormat.ENVIRONMENT_VARIABLES)
```

## Controlling the default configuration

To control the behavior of the default configuration loading

```python
import project
config = project.load_config()
```

set the following environment variables:

- `CONFIG_FORMAT` - One of `ConfigFormat` enum: `YAML_FILES`, `ENVIRONMENT_VARIABLES`, `COMMAND_LINE_ARGUMENTS`.
- `DEFAULT_PROJECT_WORKSPACE` - value for workspace dimension.
- `DEFAULT_PROJECT_LOGGING` - value for the logging dimension.

Example for development:

```bash
CONFIG_FORMAT=YAML_FILES
DEFAULT_PROJECT_WORKSPACE=dev
DEFAULT_PROJECT_LOGGING=local
```

Example for production:

```bash
CONFIG_FORMAT=ENVIRONMENT_VARIABLES
DEFAULT_PROJECT_WORKSPACE=prod
DEFAULT_PROJECT_LOGGING=google
```

## Interaction with Google Cloud Platform

BigQuery and GCS clients are properly initialized and configured automatically by `project.bigquery` and `project.storage` modules.
Default clients may be obtained anywhere with the following commands:

```python
import project

bq = project.bigquery.client()     # google.cloud.bigquery.Client
gcs = project.storage.client()     # google.cloud.storage.Client
fs = project.storage.filesystem()  # gcsfs.GCSFileSystem
```

Clients are initialized according to the configuration context with adequate

- Authentication scopes,
- GCP Project,
- Default datasets,
- Maximum billing in jobs,
- Default priority,
- Job locations,
- Caching,
- Tracking labels, and so on.

### BigQuery

For running queries with small or no results, use `project.bigquery.query`:

```python
result = project.bigquery.query(sql)   # Blocks until finished.
```

To download a table or to run query and read medium-sized result, use `project.bigquery.read(sql_or_table)`:

```python
ds = project.bigquery.extract(sql_or_table)  # pyarrow.parquet.ParquetDataset
```

Use the internal classes for finer control.
Example for extraction:

```python
config = project.load_config(...)
bq = project.bigquery.make_client(config)

reader = project.bigquery.BigQueryReader(
    client=bq,      # Optional.
    config=config,  # Optional.
)
DAYS = 1*60*60*24
ds = reader.read(
    source=table,
    columns=['a', 'b'],
    cache_expiration_secs=7 * DAYS,
)
```

Example for running a query:

```python
import project

config = project.load_config()
bq = project.bigquery.client()

job_config = project.bigquery.job_config(
    query_parameters=dict(
        query_param_a=1.0,
        other_param=datetime(2022, 1, 1),
    ),
)

job = bq.query(
    query=sql,
    job_id_prefix=config.bigquery.job_id_prefix,
    job_config=job_config,
)
job.result()
```

or, use the query job helper.
