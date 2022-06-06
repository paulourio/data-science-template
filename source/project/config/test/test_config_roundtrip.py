from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits, printable
import os

from dynaconf.base import Settings
from hypothesis import given
from hypothesis.strategies import (
    booleans,
    characters,
    composite,
    composite,
    datetimes,
    dictionaries,
    emails,
    floats,
    integers,
    lists,
    none,
    recursive,
    text,
)
from numpy import isin

from project.config import ConfigFormat, load_config, export_config, as_dict

from environment import cleanup_environment


@composite
def keys(draw):
    """Return a valid key name."""
    char1 = draw(
        text(
            alphabet=list(ascii_lowercase),
            min_size=1,
            max_size=1,
        ),
    )
    middle = draw(
        text(
            alphabet=list(ascii_lowercase + digits + '_-'),
            min_size=4,
            max_size=61
        ).filter(
            lambda x: '__' not in x and '_-' not in x
        )
    )
    endchar = draw(
        text(
            alphabet=list(ascii_lowercase + digits),
            min_size=1,
            max_size=1,
        )
    )
    return '{}{}{}'.format(char1, middle, endchar)


@composite
def string_timestamps(draw):
    """Return a timestamp formatted as string."""
    tstamp = draw(
        datetimes(
            min_value=datetime(year=2020, month=1, day=1),
            max_value=datetime(year=2100, month=12, day=31),
        ),
    )
    return str(tstamp)


@composite
def random_lists(draw):
    """Return a random list."""
    values = draw(
        recursive(
            (
                none()
                | booleans()
                | floats(allow_nan=False, allow_infinity=False)
                | text(printable)
            ),
            lists,
        )
    )
    return values


@composite
def nested_dictionaries(draw):
    """Return a random nested dictionary structure."""
    random_dict = draw(
        dictionaries(
            keys(),
            (
                none()
                | booleans()
                | integers()
                | floats(allow_nan=False, allow_infinity=False)
                | STRING_VALUES
                | random_lists()
                | emails()
                | dictionaries(
                    keys(),
                    (
                        none()
                        | booleans()
                        | integers()
                        | floats(allow_nan=False, allow_infinity=False)
                        | STRING_VALUES
                    ),
                    min_size=3,
                    max_size=10,
                )
            )
        )
    )
    return random_dict


@given(nested_dictionaries())
def test_export_round_trip(data):
    print(data)
    cleanup_environment()

    cfg = Settings(
        settings_files=[],
        CORE_LOADERS_FOR_DYNACONF=[],
        ENVIRONMENTS_FOR_DYNACONF=False,
        MAIN_ENV_FOR_DYNACONF='',
        LOADERS_FOR_DYNACONF=[],
        SILENT_ERRORS_FOR_DYNACONF=False,
    )
    cfg.update(data)

    exported = export_config(cfg, format=ConfigFormat.ENVIRONMENT_VARIABLES)

    # Reading it back should give the original input.
    os.environ.update(exported)

    config = load_config(format=ConfigFormat.ENVIRONMENT_VARIABLES)

    # Dynaconf changes the case of settings, forcing upper case at
    # root level and lower case at other levels.  We compare it all
    # as lower case keys.
    assert as_dict(config) == _lower_keys(data)


def _lower_keys(data):
    if isinstance(data, dict):
        return {k.lower(): _lower_keys(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_lower_keys(v) for v in data]
    return data


VALID_CHARS = ascii_lowercase + ascii_uppercase + digits + '_'

STRING_VALUES = text(characters(blacklist_categories=('C',)))
