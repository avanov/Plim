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
    PARSE_RAW_HTML_RE = re.compile('\<.*')
    PARSE_VARIABLE_RE = re.compile("=(?P<prevent_escape>=)?(?P<explicit_space>,)?\s*(?P<line>.*)", re.IGNORECASE)
    PARSE_COMMENT_RE = re.compile('/.*')

    PARSE_STATEMENTS_RE = re.compile('-\s*(?P<stmnt>if|for|while|with|try)(?P<expr>.*)')
    PARSE_FOREIGN_STATEMENTS_RE = re.compile('-\s*(?P<stmnt>unless|until)(?P<expr>.*)')
    PARSE_PYTHON_NEW_RE = re.compile('---[-]*(?P<excl>\!)?\s*(?P<expr>[^-].*)?')
    PARSE_PYTHON_CLASSIC_RE = re.compile('-\s*(?P<python>py(?:thon)?(?P<excl>\!?))(?P<expr>\s+.*)?')
    PARSE_DEF_BLOCK_RE = re.compile('-\s*(?P<line>(?:def|block)(?:\s+.*)?)')
    PARSE_MAKO_ONE_LINERS_RE = re.compile('-\s*(?P<line>(?:include|inherit|page|namespace)(?:\s+.*)?)')
    PARSE_MAKO_TEXT_RE = re.compile('-\s*(?P<line>text(?:\s+.*)?)')
    PARSE_CALL_RE = re.compile('-\s*(?P<line>call(?:\s+.*)?)')
    PARSE_EARLY_RETURN_RE = re.compile('-\s*(?P<keyword>return|continue|break)\s*')
    PARSE_EXTENSION_LANGUAGES_RE = re.compile('-\s*(?P<lang>md|markdown|rst|rest|coffee|scss|sass|stylus)\s*')

    PARSE_ELIF_ELSE_RE = re.compile('-\s*(?P<control>elif|else)(?P<expr>.*)')
    PARSE_EXCEPT_ELSE_FINALLY_RE = re.compile('-\s*(?P<control>except|else|finally)(?P<expr>.*)')

    def __init__(self, custom_parsers=None):
        """
        :param custom_parsers: a list of 2-tuples of (parser_regex, parser_callable) or None
        :type custom_parsers: list or None
        """
        if custom_parsers is None:
            custom_parsers = []

        # We initialize standard parsers here rather than in a class' scope, because
        # we would like to be able to discard parsers in some syntax implementations by
        # replacing them with None (see Django syntax vs. Mako syntax definitions below).
        standard_parsers = ( # Order matters
            (self.PARSE_STYLE_SCRIPT_RE, l.parse_style_script),
            (self.PARSE_DOCTYPE_RE, l.parse_doctype),
            (self.PARSE_HANDLEBARS_RE, l.parse_handlebars),
            (self.PARSE_TAG_TREE_RE, l.parse_tag_tree),
            (self.PARSE_EXPLICIT_LITERAL_RE, l.parse_explicit_literal_with_embedded_markup),
            (self.PARSE_IMPLICIT_LITERAL_RE, l.parse_implicit_literal),
            (self.PARSE_RAW_HTML_RE, l.parse_raw_html),
            (self.PARSE_VARIABLE_RE, l.parse_variable),
            (self.PARSE_COMMENT_RE, l.parse_comment),
            (self.PARSE_STATEMENTS_RE, l.parse_statements),
            (self.PARSE_FOREIGN_STATEMENTS_RE, l.parse_foreign_statements),
            (self.PARSE_PYTHON_NEW_RE, l.parse_python_new_style),
            (self.PARSE_PYTHON_CLASSIC_RE, l.parse_python),
            (self.PARSE_DEF_BLOCK_RE, l.parse_def_block),
            (self.PARSE_MAKO_ONE_LINERS_RE, l.parse_mako_one_liners),
            (self.PARSE_MAKO_TEXT_RE, l.parse_mako_text),
            (self.PARSE_CALL_RE, l.parse_call),
            (self.PARSE_EARLY_RETURN_RE, l.parse_early_return),
            (self.PARSE_EXTENSION_LANGUAGES_RE, l.parse_markup_languages)
        )
        custom_parsers.extend(standard_parsers)
        # discard parsers with None pattern
        self.parsers = tuple([p for p in custom_parsers if p[0]])

    def __str__(self):
        return 'Base Syntax'


class Mako(BaseSyntax):
    def __str__(self):
        return 'Mako Syntax'


class Django(BaseSyntax):
    VARIABLE_PLACEHOLDER_START_SEQUENCE = '{{'
    VARIABLE_PLACEHOLDER_END_SEQUENCE = '}}'
    STATEMENT_START_START_SEQUENCE = '{% '
    STATEMENT_START_END_SEQUENCE = ' %}'
    STATEMENT_END_START_SEQUENCE = STATEMENT_START_START_SEQUENCE
    STATEMENT_END_END_SEQUENCE = STATEMENT_START_END_SEQUENCE

    PARSE_MAKO_ONE_LINERS_RE = None
    PARSE_MAKO_TEXT_RE = None

    def __str__(self):
        return 'Django Syntax'
