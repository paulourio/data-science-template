"""Additional testing utilities."""
from contextlib import contextmanager
from typing import Iterator, Type, TypeVar
import re


ErrorType = TypeVar('ErrorType', bound=Exception)


@contextmanager
def raises_with_cause(expected_exception: Type[ErrorType],
                      expected_cause: Type[ErrorType],
                      exception_match: str = '',
                      cause_match: str = '') -> Iterator[None]:
    """Assert code block raises exception with an exception cause.

    We assert the code block/function call raises expected_exception
    with the expected_cause exception or raise a failure exception
    otherwise.

    Parameters
    ----------
    expected_exception : error type
        The outermost error type expected to be raised.
    expected_cause : error type
        The immediate cause error type expected to be raised together.
    exception_match : str
        If specified, a string containing a regular expression, or a
        regular expression object, that is tested against the string
        representation of the exception using ``re.search``.
    cause_match : str
        Similar to `exception_match` but matches the cause exception
        error message.

    Raises
    ------
    AssertError
        When conditions do not meet.

    Examples
    --------
    >>> with raises_with_cause(ValueError, jinja2.UndefinedError):
    ...     raise ValueError() from jinja2.UndefinedError()

    """
    try:
        yield
    except Exception as err:
        assert isinstance(err, expected_exception)
        if exception_match and not re.search(exception_match, str(err)):
            raise AssertionError(
                'Outermost error message {} do not match {}'.format(
                    repr(str(err)), repr(exception_match)
                )
            )
        assert isinstance(err.__cause__, expected_cause)
        if cause_match and not re.search(cause_match, str(err.__cause__)):
            raise AssertionError(
                'Cause error message {} do not match {}'.format(
                    repr(str(err.__cause__)), repr(cause_match)
                )
            )
