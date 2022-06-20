from multiprocessing.sharedctypes import Value
import jinja2

from project.core.templates import render
from project.core.testing import raises_with_cause


def test_core_templates():
    assert render('abc') == 'abc'
    assert render('abc', filters={'dict': dict()})
    with raises_with_cause(ValueError, jinja2.TemplateSyntaxError):
        render('{{ param ')
    with raises_with_cause(ValueError, jinja2.UndefinedError):
        render('{{ param }}')
    with raises_with_cause(ValueError, jinja2.TemplateAssertionError):
        render('{{ abc|missing_filter }}')
    with raises_with_cause(ValueError, ValueError, cause_match=r'backticks'):
        render('{{ "foo`bar"|id }}')
    params = dict(table='project.dataset.table')
    assert render('{{ table|id }}', params) == '`project.dataset.table`'
    params = dict(name='abc"def')
    assert render('{{ name|quote }}', params) == r"""'abc"def'"""
    params = dict(name="abc'def")
    assert render('{{ name|quote }}', params) == r'''"abc'def"'''
    params = dict(name='abc\"\'\\def')
    assert render('{{ name|quote }}', params) == r"""'abc"\'\\def'"""
    params = dict(name='abc\ndef')
    assert render('{{ name|quote }}', params) == r"'abc\ndef'"
    with raises_with_cause(ValueError, ModuleNotFoundError):
        render('{% set module = import("_1#@1") %}')
    result = render(
        ('{% set project = import("project") %}'
         '{{ project.core.templates.render("abc")|id }}'))
    assert result == '`abc`'
