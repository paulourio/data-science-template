from enum import Enum, auto
from multiprocessing.sharedctypes import Value
from typing import Any, Dict, Mapping, Type
import logging


def merge(*dicts: Mapping) -> Mapping:
    """Merge dictionaries."""
    merger = DictMerger(
        scalars=MergeMethod.LAST,
        dicts=MergeMethod.UNION,
        lists=MergeMethod.UNION,
    )
    return merger.apply(*dicts)


class MergeMethod(Enum):
    """Method for merging two conflicting resources."""

    FIRST = auto()
    LAST = auto()
    UNION = auto()


class DictMerger:
    """Merge dictionaries implementation.

    Parameters
    ----------
    scalars : MergeMethod,
        How to merge two scalars. Only FIRST and LAST are supported.
    dicts : MergeMethod
        How to merge two dictionaries.
    lists : MergeMethod
        How to merge two lists.

    """

    def __init__(
        self,
        scalars: MergeMethod,
        dicts: MergeMethod,
        lists: MergeMethod,
    ) -> None:
        self.scalars = scalars
        self.dicts = dicts
        self.lists = lists

    def apply(self, *items: Mapping) -> Dict:
        """Return dictionary of merged mappings."""
        result: Dict[Any, Any] = dict()
        for item in items:
            self._merge(result, item)
        return result

    def _merge(self, a: Dict, b: Mapping) -> None:
        for key, value in b.items():
            if key not in a:
                a[key] = value
                continue

            # The same key is present in both dictionaries.
            existing = a[key]
            self._check_type_mismatch(existing, value)

            if isinstance(existing, (str, int, float)) or existing is None:
                a[key] = self._merge_scalars(existing, value)
            elif isinstance(existing, list):
                a[key] = self._merge_lists(existing, value)
            elif isinstance(existing, dict):
                a[key] = self._merge_dicts(existing, value)
            else:
                LOGGER.error(
                    ('Unexpected type to merge: %s. '
                     'Trying to merge %r with %r.'),
                    type(a).__name__, a, b,
                )
                raise TypeError('unexpected type')

    def _merge_scalars(self, a, b):
        LOGGER.debug('Merging scalars %r with %r (method %s).',
                     a, b, self.scalars.name)
        if self.scalars == MergeMethod.FIRST:
            return a
        if self.scalars == MergeMethod.LAST:
            return b
        raise ValueError(
            'unsupported merge method for scalars: ' + str(self.scalars))

    def _merge_lists(self, a, b):
        LOGGER.debug('Merging lists %r with %r (method %s).',
                     a, b, self.lists.name)
        if self.lists == MergeMethod.FIRST:
            return a
        if self.lists == MergeMethod.LAST:
            return b
        if self.lists == MergeMethod.UNION:
            return a + b
        raise ValueError(
            'unsupported merge method for lists: ' + str(self.lists))

    def _merge_dicts(self, a, b):
        LOGGER.debug('Merging dicts %r with %r (method %s).',
                     a, b, self.dicts.name)
        if self.dicts == MergeMethod.FIRST:
            return a
        if self.dicts == MergeMethod.LAST:
            return b
        if self.dicts == MergeMethod.UNION:
            new_value = a.copy()
            self._merge(new_value, b)
            return new_value
        raise ValueError(
            'unsupported merge method for dicts: ' + str(self.dicts))

    def _check_type_mismatch(self, a: Any, b: Any) -> None:
        a_type, b_type = type(a), type(b)
        if a_type == b_type:
            return

        LOGGER.error(
            ('Type mismatch when merging value of type %s with type %s. '
             'Existing value: %r. Value to merge into existing: %r.'),
            a_type.__name__, b_type.__name__, a, b,
        )
        raise TypeError('type mismatch')


LOGGER = logging.getLogger(__name__)
