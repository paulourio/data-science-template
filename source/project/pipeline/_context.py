from uuid import uuid1

import project


def make_context(**kwargs) -> project.core.context.Context:
    """Return a new context initialized for pipeline operations."""
    return project.core.context.Context(
        correlation_id=uuid1(),
        **kwargs,
    )
