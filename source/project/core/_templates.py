from multiprocessing.sharedctypes import Value
from typing import Any, Callable, Dict, Final, Optional
import importlib
import logging

import jinja2


def render(content: str, params: Dict[str, Any] = None,
           filters: Optional[Dict[str, Callable]] = None,
           globals: Optional[Dict[str, Callable]] = None) -> str:
    """Return materialized content with additional params.

    Parameters
    ----------
    content : str
        The template content to be materialized.
    params : dict
        Parameters to be passed to the template.
    filters : dict, optional
        Map of additional filters to use when rendering.
    globals : dict, optional
        Map of additional globals to use when rendering.

    Returns
    -------
    str
        The materialized content.

    Raises
    ------
    jinja2.exceptions.UndefinedError
        When trying to render content with missing parameter.

    """
    if params is None:
        params = dict()

    if not filters and not globals:
        return _render(content, ENVIRONMENT, params)

    env = _make_environment(filters=filters, globals=globals)
    return _render(content, env, params)


def _render(content: str, env: jinja2.Environment, params: Dict) -> str:
    try:
        template = env.from_string(content)
        result = template.render(**params)
    except KeyboardInterrupt:
        raise
    except Exception as err:
        # We may have any Jinja2 exception plus anything raised from a
        # filter/global callable, or even some unknown imported module.
        LOGGER.error(
            ('Failed to render content: %s\n'
             'Content: %r\n'
             'Environment loader: %r\n'
             'Params: %r'),
            str(err), content, env.loader, params,
        )
        raise ValueError('failed to render content') from err
    else:
        return result


def _make_environment(filters=None, globals=None):
    env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
    )

    env.filters['id'] = _apply_id
    env.filters['quote'] = _apply_quote
    env.globals['import'] = _run_import

    if filters:
        for name, callable in filters.items():
            env.filters[name] = callable

    if globals:
        for name, callable in globals.items():
            env.globals[name] = callable

    return env


def _apply_id(data: str) -> str:
    if '`' in data:
        raise ValueError('id cannot have backticks')
    return '`' + data + '`'


def _apply_quote(data: str) -> str:
    return repr(str(data))


def _run_import(module: str) -> object:
    return importlib.import_module(module)


ENVIRONMENT: Final[jinja2.Environment] = _make_environment()

LOGGER = logging.getLogger(__name__)
