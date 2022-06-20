from project.core.dictionary import DictMerger, MergeMethod


class Context(dict):
    """Pipeline context."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def with_values(self, **kwargs) -> 'Context':
        """Return a copy of the context with additional keyword values."""
        merger = DictMerger(
            scalars=MergeMethod.LAST,
            dicts=MergeMethod.LAST,
            lists=MergeMethod.LAST,
        )
        return Context(merger.apply(self.__dict__, kwargs))
