from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type
import logging

import pytest

from project.core._dictionary import MergeMethod, DictMerger, merge
import project


def test_core_dictionary_merge():
    assert merge() == {}
    for case in TEST_CASES:
        for m in case.merges:
            merger = DictMerger(
                scalars=m.scalars,
                lists=m.lists,
                dicts=m.dicts,
            )
            if m.raises:
                with pytest.raises(m.raises):
                    merger.apply(*case.dicts)
            else:
                result = merger.apply(*case.dicts)
                if result != m.value:
                    LOGGER.error('Failed merge: %r. Got %r.', m, result)
                assert result == m.value


@dataclass
class Merge:
    """Single merge trial specification."""

    scalars: MergeMethod = MergeMethod.LAST
    lists: MergeMethod = MergeMethod.UNION
    dicts: MergeMethod = MergeMethod.UNION
    value: Dict = field(default_factory=dict)
    raises: Optional[Type[TypeError]] = None


@dataclass
class MergeTestCase:
    """Test specification for merge."""

    dicts: List[Dict]
    merges: List[Merge]


LOGGER = logging.getLogger(__name__)


TEST_CASES = [
    MergeTestCase(
        dicts=[
            dict(a=1, b=2, c=3, d='4', e=[1], f=dict(e=[5])),
            dict(a=5, b=6, c=7, d='8', e=[2], f=dict(e=[6], g=2)),
            dict(a=9, b=10, c=11, d='12', e=[3], f=dict(e=[7], g=3, h=4)),
        ],
        merges=[
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.FIRST,
                dicts=MergeMethod.FIRST,
                value=dict(a=1, b=2, c=3, d='4', e=[1], f=dict(e=[5])),
            ),
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.LAST,
                dicts=MergeMethod.FIRST,
                value=dict(a=1, b=2, c=3, d='4', e=[3], f=dict(e=[5])),
            ),
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.FIRST,
                dicts=MergeMethod.LAST,
                value=dict(a=1, b=2, c=3, d='4', e=[1],
                           f=dict(e=[7], g=3, h=4)),
            ),
            Merge(
                scalars=MergeMethod.LAST,
                lists=MergeMethod.FIRST,
                dicts=MergeMethod.FIRST,
                value=dict(a=9, b=10, c=11, d='12', e=[1], f=dict(e=[5])),
            ),
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.UNION,
                dicts=MergeMethod.FIRST,
                value=dict(a=1, b=2, c=3, d='4', e=[1, 2, 3], f=dict(e=[5])),
            ),
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.UNION,
                dicts=MergeMethod.LAST,
                value=dict(a=1, b=2, c=3, d='4', e=[1, 2, 3],
                           f=dict(e=[7], g=3, h=4)),
            ),
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.UNION,
                dicts=MergeMethod.UNION,
                value=dict(a=1, b=2, c=3, d='4', e=[1, 2, 3],
                           f=dict(e=[5, 6, 7], g=2, h=4)),
            ),
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.FIRST,
                dicts=MergeMethod.UNION,
                value=dict(a=1, b=2, c=3, d='4', e=[1],
                           f=dict(e=[5], g=2, h=4)),
            ),
            Merge(
                scalars=MergeMethod.FIRST,
                lists=MergeMethod.LAST,
                dicts=MergeMethod.UNION,
                value=dict(a=1, b=2, c=3, d='4', e=[3],
                           f=dict(e=[7], g=2, h=4)),
            ),
        ]
    ),
    MergeTestCase(
        dicts=[dict(a=1.0), dict(a=0)],
        merges=[Merge(raises=TypeError)],
    ),
    MergeTestCase(
        dicts=[dict(a=1.0), dict(a='0')],
        merges=[Merge(raises=TypeError)],
    ),
    MergeTestCase(
        dicts=[dict(a=[]), dict(a={})],
        merges=[Merge(raises=TypeError)],
    ),
    MergeTestCase(
        dicts=[dict(a={}), dict(a=[])],
        merges=[Merge(raises=TypeError)],
    ),
    MergeTestCase(
        dicts=[dict(a=None), dict(a=45)],
        merges=[Merge(raises=TypeError)],
    ),
    MergeTestCase(
        dicts=[dict(a=None), dict(a=[])],
        merges=[Merge(raises=TypeError)],
    ),
]
