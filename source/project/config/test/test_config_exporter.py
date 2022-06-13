import os

from dynaconf.base import Settings
from numpy import inf

from project.config import ExportFormat, export, load_config, as_dict

from environment import cleanup_environment


def test_export_nested_config():
    """Test exporting nested config to environment variables."""
    cleanup_environment()

    cfg = Settings(
        SETTINGS_FILE_FOR_DYNACONF=[],
        CORE_LOADERS_FOR_DYNACONF=[],
        ENVIRONMENTS_FOR_DYNACONF=False,
        MAIN_ENV_FOR_DYNACONF='',
        LOADERS_FOR_DYNACONF=[],
        SILENT_ERRORS_FOR_DYNACONF=False,
    )
    cfg.update(CONFIG)

    exported = export(cfg, format=ExportFormat.ENVIRONMENT_VARIABLES)
    assert exported == EXPECTED_ENV

    # Reading it back should give the original input.
    os.environ.update(exported)

    config = load_config(
        load_env=True,
        load_yaml=False,
        load_command_line=False,
        load_validate=False,
        load_verbose=False,
    )

    assert as_dict(config) == CONFIG


OBJECT = {
    'foo_bar': 'value',
    'integer': 123456,
    'float': 1.25992,
    'null': None,
    'list': [],
}

CONFIG = {
    'foo_bar': 'value',
    'integer': 123456,
    'float': 1.25992,
    'neg_int': -123,
    'neg_float': -1.23e254,
    'zero_int': 0,
    'zero_float': -0.0,
    'inf_float': inf,
    'null': None,
    'not_null': 'None',
    'not_null2': 'null',
    'not_int': '123456',
    'not_float': '1.2592',
    'not_bool': 'true',
    'not_list': '[]',
    'not_object': '{}',
    'empty_object': {},
    'object': OBJECT,
    'list': ['value', 123456, 1.25992, None, OBJECT],
}

EXPECTED_ENV = {
    'APP_empty_object': '@json {}',
    'APP_float': '1.25992',
    'APP_foo_bar': 'value',
    'APP_integer': '123456',
    'APP_neg_int': '@int -123',
    'APP_neg_float': '-1.23e+254',
    'APP_inf_float': 'inf',
    'APP_zero_float': '-0.0',
    'APP_zero_int': '0',
    'APP_list': (
        '@json ["value",123456,1.25992,null,{"foo_bar":"value",'
        '"integer":123456,"float":1.25992,"null":null,"list":[]}]'
    ),
    'APP_not_float': '"1.2592"',
    'APP_not_int': '"123456"',
    'APP_not_list': '"[]"',
    'APP_not_null': 'None',
    'APP_not_null2': 'null',
    'APP_not_bool': '"true"',
    'APP_not_object': '"{}"',
    'APP_null': '@json null',
    'APP_object__float': '1.25992',
    'APP_object__foo_bar': 'value',
    'APP_object__integer': '123456',
    'APP_object__list': '@json []',
    'APP_object__null': '@json null',
}
