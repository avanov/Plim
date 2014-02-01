import functools

from .lexer import compile_plim_source, STANDARD_PARSERS


def preprocessor_factory(custom_parsers=None):
    """

    :param custom_parsers: a list of 2-tuples of (parser_regex, parser_callable) or None
    :type custom_parsers: list or None
    :return: preprocessor instance
    """
    if custom_parsers is None:
        custom_parsers = []
    custom_parsers.extend(STANDARD_PARSERS)
    return functools.partial(compile_plim_source, parsers=tuple(custom_parsers))


# ``preprocessor`` is a public object that always follows Mako's preprocessor API.
# Do not use ``compile_plim_source`` in your projects, because its signature
# may be changed in the future.
preprocessor = preprocessor_factory()
