import os

from dynaconf.base import Settings


def test_config_loaders_yaml(tmpdir):
    config_dir = tmpdir.mkdir('config')
    foo = config_dir.join('foo.yml')
    bar = config_dir.join('bar.yml')
    fuz = config_dir.join('fuz.yml')

    foo.write(b'a: {b: {key: foo, $ref: bar.yml}, f: x}\nother: [1]\n')
    bar.write(b'c: {d: true}\nother: [null, 0]\nx-a: 0\n')
    fuz.write((b'a: {b: {key: "@format {this.a.f}-value", '
               b'other: [{"id": {"foo": 2}}]}}\n'
               b'x-abc: null\n'))

    settings = Settings(
        settings_module=[str(foo), str(fuz)],  # bar is read indirectly.
        CORE_LOADERS_FOR_DYNACONF=[],
        ENVIRONMENTS_FOR_DYNACONF=False,
        MAIN_ENV_FOR_DYNACONF='',
        LOADERS_FOR_DYNACONF=['project.config.loaders.yaml'],
        SILENT_ERRORS_FOR_DYNACONF=False,
    )

    expected = {
        'A': {
            'b': {
                'key': 'x-value',
                'c': {'d': True},
                'other': [None, 0, {'id': {'foo': 2}}],
            },
            'f': 'x',
        },
        'OTHER': [1],
    }

    assert settings.as_dict() == expected
