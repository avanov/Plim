import functools
from typing import Mapping, Type, Sequence, Any, Callable

from pyrsistent import v

from .lexer import compile_plim_source
from . import syntax as available_syntax


def preprocessor_factory(custom_parsers: Sequence[Any] = v(), syntax: str = 'mako') -> Callable[[str, bool], str]:
    """

    :param custom_parsers: a list of 2-tuples of (parser_regex, parser_callable) or None
    :type custom_parsers: list or None
    :param syntax: name of the target template engine ('mako' by default)
    :return: preprocessor instance
    """
    syntax_choices: Mapping[str, Type[available_syntax.BaseSyntax]] = {
        'mako': available_syntax.Mako,
        'django': available_syntax.Django,
    }
    selected_syntax = syntax_choices[syntax](custom_parsers or v())
    return functools.partial(compile_plim_source, syntax=selected_syntax)


# ``preprocessor`` is a public object that always follows Mako's preprocessor API.
# Do not use ``compile_plim_source`` in your projects, because its signature
# may be changed in the future.
preprocessor = preprocessor_factory()
