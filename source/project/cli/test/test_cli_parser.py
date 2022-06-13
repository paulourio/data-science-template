from cmath import exp
from pytest import warns

from project.cli.parser import parse_keyword_args


def test_cli_parse_args():
    with warns(UserWarning, match=r'Missing value in command-line'):
        assert parse_keyword_args(['--c']) == []
    with warns(None) as record:
        assert parse_keyword_args([]) == []
        assert parse_keyword_args(['--c', 'v']) == [('c', 'v')]
        assert parse_keyword_args(['-c', 'v']) == []
        assert parse_keyword_args(['-c', 'v'], prefix='-') == [('c', 'v')]
        # A keyword that is equal to the prefix is ignored.
        assert parse_keyword_args(['-c', 'v'], prefix='-c') == []
        argv = ['--foo', '1', '-c', '--bar', '2', '-d']
        assert parse_keyword_args(argv) == [('foo', '1'), ('bar', '2')]
        if record:
            for item in record.list:
                print('Unexpected warning:', item.message)
        assert not record

    # This is an expected behavior when using an improper prefix that
    # is ambiguous to other non-keyword arguments.  But because the last
    # element in argv matches, we expect at least a warning regarding
    # missing value.
    expected = [('-foo', '1'), ('c', '--bar')]
    with warns(UserWarning, match=r'Missing value in command-line'):
        assert parse_keyword_args(argv, prefix='-') == expected

    assert parse_keyword_args(argv, prefix='-c') == []

    # In case the prefix matches the whole word, but it is at the end
    # of the command-line, no warning should be emitted.
    with warns(None) as record:
        assert parse_keyword_args(argv, prefix='-d') == []
        assert not record

    expected = [('--foo', '1'), ('-c', '--bar'), ('2', '-d')]
    assert parse_keyword_args(argv, prefix='') == expected

    argv = ['--local', '--workspace', 'ignore', '--app_workspace', 'dev',
            '--app_logging', 'local']
    expected = [('workspace', 'dev'), ('logging', 'local')]
    assert parse_keyword_args(argv, prefix='--app_') == expected
