import re

from . import lexer as l
from .util import PY3K


if PY3K:
    PARSE_IMPLICIT_LITERAL_RE = re.compile(
        # Order matters
        '(?P<line>(?:'
            '\$?\{|\(|\[|&.+;|[0-9]+|'
            '(?:'
                '[^\u0021-\u007E]'  # not ASCII 33 - 126
                '|'                 # or
                '[A-Z]'             # uppercase latin letters (ASCII 65 - 90)
            ')'                     # It is possible because TAG_RE can match only lowercase tag names
        ').*)\s*'
    )
else:
    from .unportable import PARSE_IMPLICIT_LITERAL_RE


class BaseSyntax(object):
    VARIABLE_PLACEHOLDER_START_SEQUENCE = '${'
    VARIABLE_PLACEHOLDER_END_SEQUENCE = '}'

    STATEMENT_START_START_SEQUENCE = '%'
    STATEMENT_START_END_SEQUENCE = ':'
    STATEMENT_END_START_SEQUENCE = '%'
    STATEMENT_END_END_SEQUENCE = ''

    # Parsers
    # ----------------------------------
    PARSE_DOCTYPE_RE = re.compile('doctype\s+(?P<type>[0-9a-z\.]+)', re.IGNORECASE)
    PARSE_STYLE_SCRIPT_RE = re.compile('(?:style|script).*', re.IGNORECASE)
    PARSE_HANDLEBARS_RE = re.compile('(?:handlebars).*')
    PARSE_TAG_TREE_RE = re.compile('(?:#|\.|{tag}).*'.format(tag=l.TAG_RULE))
    # This constant uses l.LITERAL_CONTENT_PREFIX and l.LITERAL_CONTENT_SPACE_PREFIX
    PARSE_EXPLICIT_LITERAL_RE = re.compile("(?:\||,).*", re.IGNORECASE)
    PARSE_IMPLICIT_LITERAL_RE = PARSE_IMPLICIT_LITERAL_RE

    STANDARD_PARSERS = ( # Order matters
        (PARSE_STYLE_SCRIPT_RE, l.parse_style_script),
        (PARSE_DOCTYPE_RE, l.parse_doctype),
        (PARSE_HANDLEBARS_RE, l.parse_handlebars),
        (PARSE_TAG_TREE_RE, l.parse_tag_tree),
        (PARSE_EXPLICIT_LITERAL_RE, l.parse_explicit_literal_with_embedded_markup),
        (PARSE_IMPLICIT_LITERAL_RE, l.parse_implicit_literal),
        (l.PARSE_RAW_HTML_RE, l.parse_raw_html),
        (l.PARSE_VARIABLE_RE, l.parse_variable),
        (l.PARSE_COMMENT_RE, l.parse_comment),
        (l.PARSE_STATEMENTS_RE, l.parse_statements),
        (l.PARSE_FOREIGN_STATEMENTS_RE, l.parse_foreign_statements),
        (l.PARSE_PYTHON_NEW_RE, l.parse_python_new_style),
        (l.PARSE_PYTHON_CLASSIC_RE, l.parse_python),
        (l.PARSE_DEF_BLOCK_RE, l.parse_def_block),
        (l.PARSE_MAKO_ONE_LINERS_RE, l.parse_mako_one_liners),
        (l.PARSE_MAKO_TEXT_RE, l.parse_mako_text),
        (l.PARSE_CALL_RE, l.parse_call),
        (l.PARSE_EARLY_RETURN_RE, l.parse_early_return),
        (l.PARSE_EXTENSION_LANGUAGES_RE, l.parse_markup_languages)
    )

    def __init__(self, custom_parsers=None):
        """
        :param custom_parsers: a list of 2-tuples of (parser_regex, parser_callable) or None
        :type custom_parsers: list or None
        """
        if custom_parsers is None:
            custom_parsers = []
        custom_parsers.extend(self.STANDARD_PARSERS)
        self.parsers = tuple(custom_parsers)


class Mako(BaseSyntax):
    pass


class Django(BaseSyntax):
    VARIABLE_PLACEHOLDER_START_SEQUENCE = '{{'
    VARIABLE_PLACEHOLDER_END_SEQUENCE = '}}'
    STATEMENT_START_START_SEQUENCE = '{% '
    STATEMENT_START_END_SEQUENCE = ' %}'
    STATEMENT_END_START_SEQUENCE = STATEMENT_START_START_SEQUENCE
    STATEMENT_END_END_SEQUENCE = STATEMENT_START_END_SEQUENCE
