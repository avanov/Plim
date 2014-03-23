from . import lexer as l

class Mako:
    VARIABLE_PLACEHOLDER_START_SEQUENCE = '${'
    VARIABLE_PLACEHOLDER_END_SEQUENCE = '}'
    STANDARD_PARSERS = l.STANDARD_PARSERS

    def __init__(self, custom_parsers=None):
        """
        :param custom_parsers: a list of 2-tuples of (parser_regex, parser_callable) or None
        :type custom_parsers: list or None
        """
        if custom_parsers is None:
            custom_parsers = []
        custom_parsers.extend(self.STANDARD_PARSERS)
        self.parsers = tuple(custom_parsers)
