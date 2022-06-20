import project


def test_core_context():
    context = project.core.context.Context(foo='bar', fuz='fuz')
    new_context = context.with_values(foo='bbb')

    assert context != new_context
    assert context['foo'] == 'bar'
    assert new_context['foo'] == 'bbb'
