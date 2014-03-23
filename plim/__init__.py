import functools

from .lexer import compile_plim_source, STANDARD_PARSERS
from . import syntax


def preprocessor_factory(custom_parsers=None):
    """

    :param custom_parsers: a list of 2-tuples of (parser_regex, parser_callable) or None
    :type custom_parsers: list or None
    :return: preprocessor instance
    """
    mako_syntax = syntax.Mako(custom_parsers)
    return functools.partial(compile_plim_source, parsers=mako_syntax.parsers, syntax=mako_syntax)


# ``preprocessor`` is a public object that always follows Mako's preprocessor API.
# Do not use ``compile_plim_source`` in your projects, because its signature
# may be changed in the future.
preprocessor = preprocessor_factory()
