import os

from dynaconf.base import Settings

from project.config import ConfigFormat, export_config, load_config, as_dict

from environment import cleanup_environment


def test_export_nested_config():
    """Test exporting nested config to environment variables."""
    cleanup_environment()

    cfg = Settings(
        settings_files=[],
        CORE_LOADERS_FOR_DYNACONF=[],
        ENVIRONMENTS_FOR_DYNACONF=False,
        MAIN_ENV_FOR_DYNACONF='',
        LOADERS_FOR_DYNACONF=[],
        SILENT_ERRORS_FOR_DYNACONF=False,
    )
    cfg.update(CONFIG)

    exported = export_config(cfg, format=ConfigFormat.ENVIRONMENT_VARIABLES)
    assert exported == EXPECTED_ENV

    # Reading it back should give the original input.
    os.environ.update(exported)

    config = load_config(format=ConfigFormat.ENVIRONMENT_VARIABLES)
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
    'null': None,
    'not_null': 'None',
    'not_null2': 'null',
    'not_int': '123456',
    'not_float': '1.2592',
    'not_list': '[]',
    'not_object': '{}',
    'empty_object': {},
    'object': OBJECT,
    'list': ['value', 123456, 1.25992, None, OBJECT],
}

EXPECTED_ENV = {
    'PROJECT_empty_object': '@json {}',
    'PROJECT_float': '@float 1.25992',
    'PROJECT_foo_bar': 'value',
    'PROJECT_integer': '@int 123456',
    'PROJECT_list': (
        '@json ["value",123456,1.25992,null,{"foo_bar":"value",'
        '"integer":123456,"float":1.25992,"null":null,"list":[]}]'
    ),
    'PROJECT_not_float': "'1.2592'",
    'PROJECT_not_int': "'123456'",
    'PROJECT_not_list': "'[]'",
    'PROJECT_not_null': 'None',
    'PROJECT_not_null2': 'null',
    'PROJECT_not_object': "'{}'",
    'PROJECT_null': '@json null',
    'PROJECT_object__float': '@float 1.25992',
    'PROJECT_object__foo_bar': 'value',
    'PROJECT_object__integer': '@int 123456',
    'PROJECT_object__list': '@json []',
    'PROJECT_object__null': '@json null',
}
