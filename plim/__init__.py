import functools

from .lexer import compile_plim_source, STANDARD_PARSERS


# ``preprocessor`` is a public object that always follows Mako's preprocessor API.
# Do not use ``compile_plim_source`` in your projects, because its signature
# may be changed in the future.
preprocessor = functools.partial(compile_plim_source, parsers=STANDARD_PARSERS)
