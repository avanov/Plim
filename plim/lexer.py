# -*- coding: utf-8 -*-
import re

import markdown2

from . import errors
from .util import StringIO, PY3K, joined, space_separated, as_unicode
from .extensions import rst_to_html
from .extensions import coffee_to_js
from .extensions import scss_to_css
from .extensions import stylus_to_css



# Preface
# ============================================================================================

WHITESPACE = ' '
NEWLINE = '\n'
OPEN_BRACE = '('
CLOSE_BRACE = ')'

CSS_ID_SHORTCUT_DELIMITER = '#'
CSS_CLASS_SHORTCUT_DELIMITER = '.'
# used to separate tag attributes from its inline content and as a prefix of literal blocks
LITERAL_CONTENT_PREFIX = '|'
# Same as above but with the trailing whitespace
LITERAL_CONTENT_SPACE_PREFIX = ','
DYNAMIC_CONTENT_PREFIX = '='
DYNAMIC_CONTENT_SPACE_PREFIX = "=,"
# used to separate inline tags
INLINE_TAG_SEPARATOR = ':'
# used to separate attribute-value pairs from one another
ATTRIBUTES_DELIMITER = WHITESPACE
# used to separate attribute name from its value
# This is not the same as DYNAMIC_CONTENT_PREFIX
ATTRIBUTE_VALUE_DELIMITER = '='
# port of ruby's boolean methods:
# Ruby's Slim: selected=option_selected?("Slim")
# Python's Plim: selected=option_selected("Plim")?
BOOLEAN_ATTRIBUTE_MARKER = '?'
LINE_BREAK = '\\'

# Please note that in Plim all tag names are intentionally lower-cased
TAG_RULE = '(?P<html_tag>[a-z][a-z0-9]*)'
TAG_RE = re.compile(TAG_RULE)
LINE_PARTS_RE = re.compile('(?P<indent>\s*)(?P<line>.*)\s*')
MAKO_FILTERS_TAIL_RE = re.compile('\|\s*(?P<filters>[a-zA-Z][_.a-zA-Z0-9]*(?:,\s*[a-zA-Z][_.a-zA-Z0-9]*)*)\s*$')
NUMERIC_VALUE_RE = re.compile(
    # Order matters
    # Can parse -NUM, +NUM, NUM, .NUM, NUM% and all its combinations
    '(?P<value>(?:[-+]?[0-9]*\.[0-9]+|[-+]?[0-9]+%?))'
)

PARSE_PLIM_TREE_RE = re.compile('(?:#|\.|{tag}).*'.format(tag=TAG_RULE))
PARSE_STATEMENTS_RE = re.compile('-\s*(?P<stmnt>if|for|while|with|try)(?P<expr>.*)')
PARSE_FOREIGN_STATEMENTS_RE = re.compile('-\s*(?P<stmnt>unless|until)(?P<expr>.*)')
STATEMENT_CONVERT = {
    'unless': 'if not (',
    'until': 'while not ('
}

PARSE_ELIF_ELSE_RE = re.compile('-\s*(?P<control>elif|else)(?P<expr>.*)')
PARSE_EXCEPT_ELSE_FINALLY_RE = re.compile('-\s*(?P<control>except|else|finally)(?P<expr>.*)')

PARSE_PYTHON_RE = re.compile('-\s*(?P<python>py(?:thon)?(?P<excl>\!?))(?P<expr>\s+.*)?')
PARSE_DEF_BLOCK_RE = re.compile('-\s*(?P<line>(?:def|block)(?:\s+.*)?)')
PARSE_MAKO_ONE_LINERS_RE = re.compile('-\s*(?P<line>(?:include|inherit|page|namespace)(?:\s+.*)?)')

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

PARSE_RAW_HTML_RE = re.compile('\<.*')
PARSE_MAKO_TEXT_RE = re.compile('-\s*(?P<line>text(?:\s+.*)?)')
PARSE_CALL_RE = re.compile('-\s*(?P<line>call(?:\s+.*)?)')
PARSE_EARLY_RETURN_RE = re.compile('-\s*(?P<keyword>return|continue|break)\s*')

# This constant uses LITERAL_CONTENT_PREFIX and LITERAL_CONTENT_SPACE_PREFIX
PARSE_EXPLICIT_LITERAL_RE = re.compile("(?:\||,).*", re.IGNORECASE)

PARSE_VARIABLE_RE = re.compile("=(?P<prevent_escape>=)?(?P<explicit_space>,)?\s*(?P<line>.*)", re.IGNORECASE)
PARSE_COMMENT_RE = re.compile('/.*')
PARSE_DOCTYPE_RE = re.compile('doctype\s+(?P<type>[0-9a-z\.]+)', re.IGNORECASE)
PARSE_STYLE_SCRIPT_RE = re.compile('(?:style|script).*', re.IGNORECASE)
PARSE_EXTENSION_LANGUAGES_RE = re.compile('-\s*(?P<lang>md|markdown|rst|rest|coffee|scss|sass|stylus)\s*')

CSS_ID_SHORTCUT_TERMINATORS = (
    CSS_CLASS_SHORTCUT_DELIMITER,
    WHITESPACE,
    OPEN_BRACE,
    INLINE_TAG_SEPARATOR
)

CSS_CLASS_SHORTCUT_TERMINATORS = (
    CSS_CLASS_SHORTCUT_DELIMITER,
    WHITESPACE,
    OPEN_BRACE,
    INLINE_TAG_SEPARATOR
)

ATTRIBUTE_TERMINATORS = (
    ATTRIBUTE_VALUE_DELIMITER,
    ATTRIBUTES_DELIMITER,
    INLINE_TAG_SEPARATOR,
    LITERAL_CONTENT_PREFIX,
    LITERAL_CONTENT_SPACE_PREFIX
)

ATTRIBUTE_TERMINATORS_WITH_PARENTHESES = (
    ATTRIBUTE_VALUE_DELIMITER,
    ATTRIBUTES_DELIMITER,
    CLOSE_BRACE
)

ATTRIBUTE_VALUE_TERMINATORS = (
    ATTRIBUTES_DELIMITER,
    INLINE_TAG_SEPARATOR,
    LITERAL_CONTENT_PREFIX,
    LITERAL_CONTENT_SPACE_PREFIX,
    DYNAMIC_CONTENT_PREFIX,
    BOOLEAN_ATTRIBUTE_MARKER
)

ATTRIBUTE_VALUE_TERMINATORS_WITH_PARENTHESES = (
    ATTRIBUTES_DELIMITER,
    INLINE_TAG_SEPARATOR,
    LITERAL_CONTENT_PREFIX,
    LITERAL_CONTENT_SPACE_PREFIX,
    DYNAMIC_CONTENT_PREFIX,
    BOOLEAN_ATTRIBUTE_MARKER,
    CLOSE_BRACE,
    NEWLINE
)

PYTHON_EXPR_OPEN_BRACES_RE = re.compile('(?P<start_brace>\(|\{|\[).*')
PYTHON_EXPR_CLOSING_BRACES_RE = re.compile('\)|\}|\].*')
MAKO_EXPR_START_BRACE_RE = re.compile('(?P<start_brace>\$\{).*')
MAKO_EXPR_COUNT_OPEN_BRACES_RE = re.compile('\{')
MAKO_EXPR_COUNT_CLOSING_BRACES_RE = re.compile('\}')
QUOTES_RE = re.compile('(?P<quote_type>\'\'\'|"""|\'|").*') # order matters!


# ============================================================================================
# Okay, let's get started.
# There are three different types of functions below: searchers, parsers, and extractors.
# They are grouped together by API and task similarity.
#
# -- SEARCHERS are helper functions that tries to figure out the next step of parsing process
#    based on the current chunk of parsing data.
#    Each searcher MUST accept one required first positional argument *line*.
# ------------------------------
#
# -- PARSERS are the building blocks of Plim. They follow the strict API rules for both
#    input and return values.
#
#    Every parser MUST accept four input arguments:
#    1) ``indent_level`` - an indentation level of current line. When the parser reaches a line
#       which indentation is lower or equal to `indent_level``, it returns control to a top-level function.
#    2) ``current_line`` - currently parsing line. This is the line that has been matched by
#       ``matched`` object at previous parsing step.
#    3) ``matched`` - an instance of re.MatchObject of the regex associated with the current parser.
#    4) ``source`` - an instance of enumerated object returned by :func:`enumerate_source`.
#
#    Every parser MUST return a 4-tuple of:
#    1) parsed_data - a string of successfully parsed data
#    2) tail_indent - an indentation level of the ``tail line``
#    3) tail_line - a line which indentation level (``tail_indent``) is lower or equal to
#       the input `indent_level``.
#    4) ``source`` - an instance of enumerated object returned by :func:`enumerate_source`
#       which represents the remaining (untouched) plim markup.
# ------------------------------
#
# -- EXTRACTORS are the "light" versions of parsers. It means that their input arguments
#    and return values are task-specific. However, they still have several common features:
#      - Each extractor has its own starting and termination sequences.
#      - Each extractor tries to find the starting sequence of characters at the beginning
#        of the input line. If that attempt fails, the extractor returns None (in most of cases).
#        If the attempt has been succeeded, the extractor will capture all the input characters up to
#        the termination sequence.
#      - The return value of the succeeded extractor MUST contain not only the extracted value, but
#        also an instance of enumerated object returned by :func:`enumerate_source`.
# ------------------------------
#
# P.S. Yes, I'm well informed about a symbiotic relationship between "for" statements and iterators.
# But I wanted to make all parsers pure functional. Therefore, You can find a number of
# "while True: try/except StopIteration" constructs below.

# Searchers
# ==================================================================================
def search_quotes(line, escape_char='\\'):
    """``line`` may be empty"""
    match = QUOTES_RE.match(line)
    if not match: return None

    find_seq = match.group('quote_type')
    find_seq_len = len(find_seq)
    pos = find_seq_len
    line_len = len(line)

    while pos < line_len:
        if line[pos] == escape_char:
            pos += 2
            continue
        if line[pos:].startswith(find_seq):
            return pos + find_seq_len
        pos += 1
    return None


def search_parser(lineno, line):
    """Finds a proper parser function for a given line or raises an error"""
    for template, parser in PARSERS:
        matched = template.match(line)
        if matched:
            return matched, parser
    raise errors.ParserNotFound(lineno, line)


# Extractors
# ==================================================================================
def _extract_braces_api(line, source, starting_braces_re, open_braces_re, closing_braces_re):
    """``line`` may be empty"""
    match = starting_braces_re.match(line)
    if not match:
        return None

    open_brace = match.group('start_brace')
    buf = [open_brace]
    tail = line[len(open_brace):]
    braces_counter = 1
     
    while True:
        if not tail:
            _, tail = next(source)
            tail = tail.lstrip()
        
        while tail:
            current_char = tail[0]
            if closing_braces_re.match(current_char):
                braces_counter -= 1
                buf.append(current_char)
                if braces_counter:
                    tail = tail[1:]
                    continue
                return joined(buf), tail[1:], source
    
            if current_char == NEWLINE:
                _, tail = next(source)
                tail = tail.lstrip()
                continue
    
            if open_braces_re.match(current_char):
                braces_counter += 1
                buf.append(current_char)
                tail = tail[1:]
                continue
    
            result = search_quotes(tail)
            if result is not None:
                buf.append(tail[:result])
                tail = tail[result:]
                continue
    
            buf.append(current_char)
            tail = tail[1:]


extract_braces = lambda line, source: _extract_braces_api(line, source,
    PYTHON_EXPR_OPEN_BRACES_RE,
    PYTHON_EXPR_OPEN_BRACES_RE,
    PYTHON_EXPR_CLOSING_BRACES_RE
)

extract_mako_expression = lambda line, source: _extract_braces_api(line, source,
    MAKO_EXPR_START_BRACE_RE,
    MAKO_EXPR_COUNT_OPEN_BRACES_RE,
    MAKO_EXPR_COUNT_CLOSING_BRACES_RE
)


def extract_identifier(line, source, identifier_start='#', terminators=('.', ' ', CLOSE_BRACE, INLINE_TAG_SEPARATOR)):
    """``line`` may be empty"""
    if not line or not line.startswith(identifier_start):
        return None

    pos = len(identifier_start)
    buf = [identifier_start]
    tail = line[pos:]
    while tail:
        current_char = tail[0]
        if current_char in terminators:
            return joined(buf).rstrip(), tail, source

        # Let's try to find "mako variable" part of possible css-identifier
        result = extract_mako_expression(tail, source)
        if result:
            expr, tail, source = result
            buf.append(expr)
            continue
        # Try to search braces of function calls etc
        result = extract_braces(tail, source)
        if result:
            result, tail, source = result
            buf.append(result)
            continue
        buf.append(current_char)
        tail = tail[1:]
    return joined(buf).rstrip(), tail, source


def extract_digital_attr_value(line):
    result = NUMERIC_VALUE_RE.match(line)
    if result:
        return result.group('value'), line[result.end():]
    return None


def extract_quoted_attr_value(line):
    result = search_quotes(line)
    if result:
        if line.startswith('"""') or line.startswith("'''"):
            skip = 3
        else:
            skip = 1
        # remove quotes from value
        value = line[skip:result - skip]
        return value.decode('string_escape'), line[result:]
    return None


def extract_dynamic_attr_value(line, source, terminators):
    result = extract_identifier(line, source, '', terminators)
    if result is None:
        return None
    result, tail, source = result
    if line.startswith('${'):
        # remove "${" and "}" from variable
        value = result[2:-1]
    elif line.startswith(OPEN_BRACE):
        # remove "(" and ")" from variable
        value = result[1:-1]
    else:
        value = result
    return value, tail, source


def extract_tag_attribute(line, source, parentheses=False):
    if parentheses:
        result = extract_identifier(line, source, '', ATTRIBUTE_TERMINATORS_WITH_PARENTHESES)
    else:
        result = extract_identifier(line, source, '', ATTRIBUTE_TERMINATORS)
    if result and result[0]:
        result, tail, source = result
        attr_name = result
        if tail.startswith(ATTRIBUTE_VALUE_DELIMITER):
            # value is presented in a form of
            # =${dynamic_value} or =dynamic_value or ="value with spaces"
            # ------------------------------------------------------------------
            # remove ATTRIBUTE_VALUE_DELIMITER
            tail = tail[1:]
            # 1. Try to parse quoted literal value
            # -------------------------------------
            result = extract_quoted_attr_value(tail)
            if result:
                value, tail = result
                # remove possible newline character
                value = value.rstrip()
                return '{attr_name}="{value}"'.format(attr_name=attr_name, value=value), tail, source

            # 2. Try to parse digital value
            # -------------------------------------
            result = extract_digital_attr_value(tail)
            if result:
                value, tail = result
                return '{attr_name}="{value}"'.format(attr_name=attr_name, value=value), tail, source

            # 3. Try to parse dynamic value
            # -------------------------------------
            if parentheses:
                result = extract_dynamic_attr_value(tail, source, ATTRIBUTE_VALUE_TERMINATORS_WITH_PARENTHESES)
            else:
                result = extract_dynamic_attr_value(tail, source, ATTRIBUTE_VALUE_TERMINATORS)

            if result:
                value, tail, source = result
                # remove possible newline character
                value = value.rstrip()
                if tail.startswith(BOOLEAN_ATTRIBUTE_MARKER):
                    # selected=dynamic_variable?
                    value = """${{({value}) and '{attr_name}="{attr_name}"' or ''|n}}""".format(
                        value=value, attr_name=attr_name
                    )
                    attribute = value
                    tail = tail[1:]
                else:
                    attribute = '{attr_name}="${{{value}}}"'.format(attr_name=attr_name, value=value)
                return attribute, tail, source
            return None

        elif parentheses and tail.startswith(ATTRIBUTES_DELIMITER) or tail.startswith(CLOSE_BRACE):
            # attribute is presented in a form of boolean attribute
            # which should be converted to attr="attr"
            return '{attr_name}="{attr_name}"'.format(attr_name=attr_name), tail, source
        else:
            return None
    return None


def extract_line_break(tail, source):
    found = False
    while True:
        if tail.startswith(LINE_BREAK):
            found = True
            try:
                _, tail = next(source)
            except StopIteration:
                return found, '', source
            tail = tail.lstrip()
            continue
        break
    return found, tail, source


def extract_statement_expression(tail, source):
    buf = []
    # Ensure that tail ends with a newline character
    # (required by extract_braces() to properly handle multi-line expressions)
    tail = tail.strip() + '\n'
    while tail:
        # Try to search braces of function calls etc
        found, tail, source = extract_line_break(tail, source)
        if found:
            buf.append(' ')
        result = extract_braces(tail, source)
        if result:
            head, tail, source = result
            buf.append(head)
            continue
        buf.append(tail[0])
        tail = tail[1:]
    return joined(buf).strip(), source


def extract_plim_line(line, source):
    """Returns a 3-tuple of inline tags sequence, closing tags sequence, and a dictionary of
    last tag components (name, attributes, content)"""
    buf = []
    close_buf = []
    components = {}
    tail = line

    while tail:
        tag_composer = ['<']
        # Get tag name
        match = TAG_RE.match(tail)
        if match:
            html_tag = match.group('html_tag').lower()
            tail = tail[match.end():]
        else:
            html_tag = 'div'
        tag_composer.append(html_tag)
        components['name'] = html_tag

        # 1. Parse css id
        # --------------------------------------------
        result = extract_identifier(tail, source, CSS_ID_SHORTCUT_DELIMITER, CSS_ID_SHORTCUT_TERMINATORS)
        if result is None:
            css_id = ''
        else:
            result, tail, source = result
            # remove preceding '#' character
            css_id = result[1:].rstrip()

        # 2. Parse css class shortcut
        # --------------------------------------------
        class_identifiers = []
        while True:
            result = extract_identifier(tail, source, CSS_CLASS_SHORTCUT_DELIMITER, CSS_CLASS_SHORTCUT_TERMINATORS)
            if result:
                result, tail, source = result
                # remove preceding '.' character
                class_identifiers.append(result[1:].rstrip())
                continue
            break

        # 3. Parse tag attributes
        # -----------------------------------
        _, tail, source = extract_line_break(tail.lstrip(), source)
        parentheses = tail.startswith(OPEN_BRACE)
        if parentheses:
            tail = tail[1:].lstrip()

        attributes = []
        # 3.1. get attribute-value pairs until the end of section (indicated by terminators)
        while True:
            _, tail, source = extract_line_break(tail.lstrip(), source)
            result = extract_tag_attribute(tail, source, parentheses)
            if result:
                attribute_pair, tail, source = result
                if attribute_pair.startswith('id="') and css_id:
                    raise errors.PlimSyntaxError('Your template has two "id" attribute definitions', line)
                if attribute_pair.startswith('class="'):
                    # len('class="') == 7
                    class_identifiers.append(attribute_pair[7:-1])
                    continue

                attributes.append(attribute_pair)
                continue
            else:
                if parentheses and not tail:
                    # We have reached the end of the line
                    # Try to parse multiline attributes list
                    lineno, tail = next(source)
                    continue
                if css_id:
                    attributes.append('id="{ids}"'.format(ids=css_id))
                if class_identifiers:
                    class_identifiers = space_separated(class_identifiers)
                    attributes.append('class="{classes}"'.format(classes=class_identifiers))
            break
        attributes = space_separated(attributes).strip()
        components['attributes'] = attributes
        if attributes:
            tag_composer.extend([' ', attributes])

        # 3.2 syntax check
        if parentheses:
            if tail.startswith(CLOSE_BRACE):
                # We have reached the end of attributes definition
                tail = tail[1:].lstrip()
            else:
                raise errors.PlimSyntaxError("Unexpected end of line", line)
        else:
            if tail.startswith(' '):
                tail = tail.lstrip()

        if html_tag in EMPTY_TAGS:
            tag_composer.append('/>')
        else:
            tag_composer.append('>')
            close_buf.append('</{tag}>'.format(tag=html_tag))
        buf.append(joined(tag_composer))

        if tail.startswith(INLINE_TAG_SEPARATOR):
            tail = tail[1:].lstrip()
            # continue to parse inline tags
            continue

        # 3.3 The remainder of the line will be treated as content
        # ------------------------------------------------------------------
        components['content'] = ''
        if tail:
            if tail.startswith(DYNAMIC_CONTENT_PREFIX):
                tail = tail[1:]
                if tail.startswith(DYNAMIC_CONTENT_PREFIX):
                    tail = _inject_n_filter(tail)
                    if tail.startswith(DYNAMIC_CONTENT_SPACE_PREFIX):
                        # ensure that a single whitespace is appended
                        tail, source = extract_statement_expression(tail[2:], source)
                        buf.append("${{{content}}} ".format(content=tail))
                    else:
                        tail, source = extract_statement_expression(tail[1:], source)
                        buf.append("${{{content}}}".format(content=tail))
                else:
                    if tail.startswith(LITERAL_CONTENT_SPACE_PREFIX):
                        # ensure that a single whitespace is appended
                        tail, source = extract_statement_expression(tail[1:], source)
                        buf.append("${{{content}}} ".format(content=tail))
                    else:
                        tail, source = extract_statement_expression(tail, source)
                        buf.append("${{{content}}}".format(content=tail))

            elif tail.startswith(LITERAL_CONTENT_PREFIX):
                buf.append(tail[1:].strip())

            elif tail.startswith(LITERAL_CONTENT_SPACE_PREFIX):
                tail = tail[1:].strip()
                buf.append("{content} ".format(content=tail))

            else:
                buf.append(tail.strip())
            components['content'] = buf[-1]
        break
    return joined(buf), joined(reversed(close_buf)), components, source


# Parsers
# ==================================================================================
def parse_style_script(indent_level, current_line, matched, source):
    extracted_html_line, close_buf, _, source = extract_plim_line(current_line, source)
    buf = [extracted_html_line, '\n']
    parsed_data, tail_indent, tail_line, source = parse_explicit_literal(indent_level, LITERAL_CONTENT_PREFIX, matched, source)
    buf.extend([parsed_data, close_buf])
    return joined(buf), tail_indent, tail_line, source


def parse_doctype(indent_level, current_line, ___, source):
    match = PARSE_DOCTYPE_RE.match(current_line.strip())
    doctype = match.group('type')
    return DOCTYPES.get(doctype, DOCTYPES['5']), indent_level, '', source


def parse_plim_tree(indent_level, current_line, ___, source):
    buf = []
    current_line = current_line.strip()
    extracted_html_line, close_buf, _, source = extract_plim_line(current_line, source)
    buf.append(extracted_html_line)

    while True:
        try:
            lineno, current_line = next(source)
        except StopIteration:
            break

        tail_indent, tail_line = scan_line(current_line)
        if not tail_line:
            continue
        if tail_indent <= indent_level:
            buf.append(close_buf)
            return joined(buf), tail_indent, tail_line, source

        # ----------------------------------------------------------
        while tail_line:
            matched_obj, parse = search_parser(lineno, tail_line)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
            buf.append(parsed_data)
            if tail_indent <= indent_level:
                buf.append(close_buf)
                return joined(buf), tail_indent, tail_line, source

    buf.append(close_buf)
    return joined(buf), 0, '', source


def parse_markup_languages(indent_level, __, matched, source):
    markup_parser = MARKUP_LANGUAGES[matched.group('lang')]
    parsed_data, tail_indent, tail_line, source = parse_explicit_literal(indent_level, LITERAL_CONTENT_PREFIX, matched, source)
    # This is slow, but correct.
    # Trying to remove preceding indentation from
    parsed_data = markup_parser(parsed_data)
    return parsed_data.strip(), tail_indent, tail_line, source


def parse_python(indent_level, __, matched, source):
    # TODO: merge with parse_mako_text()
    if matched.group('python').endswith('!'):
        buf = ['<%!\n']
    else:
        buf = ['<%\n']
    inlined = matched.group('expr')
    if inlined:
        buf.extend([inlined.strip(), '\n'])

    parsed_data, tail_indent, tail_line, source = parse_explicit_literal(indent_level, LITERAL_CONTENT_PREFIX, matched, source)
    if parsed_data:
        buf.append(as_unicode('{literal}\n').format(literal=parsed_data.rstrip()))
    buf.append('%>\n')
    return joined(buf), tail_indent, tail_line, source


def parse_mako_text(indent, __, matched, source):
    _, __, components, source = extract_plim_line(matched.group('line').strip(), source)
    buf = ['\n<%text']
    if components['attributes']:
        buf.extend([' ', components['attributes']])
    buf.append('>\n')
    if components['content']:
        buf.extend([components['content'], '\n'])

    parsed_data, tail_indent, tail_line, source = parse_explicit_literal(indent, LITERAL_CONTENT_PREFIX, matched, source)
    if parsed_data:
        buf.append(as_unicode('{literal}\n').format(literal=parsed_data.rstrip()))
    buf.append('</%text>\n')
    return joined(buf), tail_indent, tail_line, source


def parse_call(indent_level, current_line, matched, source):
    _, __, components, source = extract_plim_line(matched.group('line').strip(), source)
    tag = components['content'].strip()
    if not tag:
        raise errors.PlimSyntaxError("-call must contain namespace:defname declaration", current_line)
    buf = ['\n<%{tag}'.format(tag=tag)]
    if components['attributes']:
        buf.extend([' ', components['attributes']])
    buf.append('>\n')

    while True:
        try:
            lineno, tail_line = next(source)
        except StopIteration:
            break

        tail_indent, tail_line = scan_line(tail_line)
        if not tail_line:
            continue
        # Parse tree
        # --------------------------------------------------------
        while tail_line:
            if tail_indent <= indent_level:
                buf.append('</%{tag}>\n'.format(tag=tag))
                return joined(buf), tail_indent, tail_line, source

            # tail_indent > indent_level
            matched_obj, parse = search_parser(lineno, tail_line)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
            buf.append(parsed_data)
    buf.append('</%{tag}>\n'.format(tag=tag))
    return joined(buf), 0, '', source


def parse_comment(indent_level, __, ___, source):
    while True:
        try:
            lineno, tail_line = next(source)
        except StopIteration:
            break
        tail_indent, tail_line = scan_line(tail_line)
        if not tail_line:
            continue
        if tail_indent <= indent_level:
            return '', tail_indent, tail_line, source
    return '', 0, '', source


def parse_statements(indent_level, __, matched, source):
    stmnt = matched.group('stmnt')
    expr = matched.group('expr')
    buf = ['\n%{statement}'.format(statement=stmnt)]
    if expr:
        expr, source = extract_statement_expression(expr, source)
        buf.append(joined([' ', expr]))

    buf.append(':\n')

    while True:
        try:
            lineno, tail_line = next(source)
        except StopIteration:
            break

        tail_indent, tail_line = scan_line(tail_line)
        if not tail_line:
            continue
        # Parse tree
        # --------------------------------------------------------
        while tail_line:
            if stmnt == 'if':
                if tail_indent == indent_level:
                    # Check for elif/else
                    match = PARSE_ELIF_ELSE_RE.match(tail_line)
                    if match:
                        if match.group('control') == 'elif':
                            expr, source = extract_statement_expression(match.group('expr'), source)
                            buf.append('\n%elif {expr}:\n'.format(expr=expr))
                            break
                        else:
                            # "-else" is found
                            buf.append('\n%else:\n')
                            break
                    else:
                        # elif/else is not found, finalize and return buffer
                        buf.append('\n%end{statement}\n'.format(statement=stmnt))
                        return joined(buf), tail_indent, tail_line, source

                elif tail_indent < indent_level:
                    buf.append('\n%end{statement}\n'.format(statement=stmnt))
                    return joined(buf), tail_indent, tail_line, source

                # tail_indent > indent_level
                matched_obj, parse = search_parser(lineno, tail_line)
                parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
                buf.append(parsed_data)

            elif stmnt == 'try':
                if tail_indent == indent_level:
                    # Check for except/else/finally
                    match = PARSE_EXCEPT_ELSE_FINALLY_RE.match(tail_line)
                    if match:
                        if match.group('control') == 'except':
                            expr, source = extract_statement_expression(match.group('expr'), source)
                            buf.append('\n%except {expr}:\n'.format(expr=expr))
                            break
                        elif match.group('control') == 'else':
                            buf.append('\n%else:\n')
                            break
                        else:
                            # "-finally" is found
                            buf.append('\n%finally:\n')
                            break
                    else:
                        # elif/else is not found, finalize and return buffer
                        buf.append('\n%end{statement}\n'.format(statement=stmnt))
                        return joined(buf), tail_indent, tail_line, source

                elif tail_indent < indent_level:
                    buf.append('\n%end{statement}\n'.format(statement=stmnt))
                    return joined(buf), tail_indent, tail_line, source

                # tail_indent > indent_level
                matched_obj, parse = search_parser(lineno, tail_line)
                parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
                buf.append(parsed_data)

            else: # stmnt == for/while
                if tail_indent <= indent_level:
                    buf.append('\n%end{statement}\n'.format(statement=stmnt))
                    return joined(buf), tail_indent, tail_line, source

                # tail_indent > indent_level
                matched_obj, parse = search_parser(lineno, tail_line)
                parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
                buf.append(parsed_data)

    buf.append('\n%end{statement}\n'.format(statement=stmnt))
    return joined(buf), 0, '', source


def parse_foreign_statements(indent_level, __, matched, source):
    stmnt = STATEMENT_CONVERT[matched.group('stmnt')]
    buf = ['-{statement}'.format(statement=stmnt)]
    expr = matched.group('expr')
    expr, source = extract_statement_expression(expr, source)
    buf.append(joined([expr, ')']))

    matched = PARSE_STATEMENTS_RE.match(joined(buf))
    return parse_statements(indent_level, __, matched, source)


def parse_explicit_literal(indent_level, current_line, ___, source):
    """Parses lines and blocks started with the "|" (pipe) or "," (comma) character."""
    # Get rid of the pipe character
    trailing_space_required = current_line[0] == LITERAL_CONTENT_SPACE_PREFIX
    current_line = current_line[1:]
    _, striped_line = scan_line(current_line)
    # Add line and trailing newline character
    buf = [current_line.strip(), striped_line and "\n" or ""]

    align = None
    while True:
        try:
            lineno, current_line = next(source)
        except StopIteration:
            break
        indent, line = scan_line(current_line)
        if not line:
            buf.append('\n')
            continue
        if indent <= indent_level:
            result = joined(buf).rstrip()
            if trailing_space_required:
                result = "{} ".format(result)
            return result, indent, line, source
        if align is None:
            align = len(current_line) - len(current_line.lstrip())

        # remove preceding spaces
        line = current_line[align:].rstrip()
        buf.extend([line.rstrip(), "\n"])

    result = joined(buf).rstrip()
    if trailing_space_required:
        result = "{} ".format(result)
    return result, 0, '', source


def _inject_n_filter(line):
    """This is a helper function for :func:parse_variable"""
    # try to find specified filters
    found_filters = MAKO_FILTERS_TAIL_RE.search(line)
    if found_filters:
        # inject "n" filter to specified filters chain
        line = as_unicode('{expr}n,{filters}').format(
            expr=line[:found_filters.start('filters')].rstrip(),
            filters=line[found_filters.start('filters'):]
        )
    else:
        line = as_unicode('{expr}|n').format(expr=line)
    return line


def parse_variable(indent_level, __, matched, source):
    explicit_space = matched.group('explicit_space') and ' ' or ''
    prevent_escape = matched.group('prevent_escape')
    buf = ['${', matched.group('line')]
    while True:
        try:
            lineno, current_line = next(source)
        except StopIteration:
            break
        indent, line = scan_line(current_line)
        if not line:
            continue
        if indent <= indent_level:
            buf = joined(buf)
            if prevent_escape:
                buf = _inject_n_filter(buf)
            # add closing brace to complete mako expression syntax ${}
            buf += '}' + explicit_space
            return buf, indent, line, source
        buf.append(line.strip())

    buf = joined(buf)
    if prevent_escape:
        buf = _inject_n_filter(buf)
    buf += '}' + explicit_space
    return buf, 0, '', source


def parse_early_return(indent_level, __, matched, source):
    return as_unicode('\n<% {keyword} %>\n').format(keyword=matched.group('keyword')), indent_level, '', source


def parse_implicit_literal(indent_level, __, matched, source):
    return parse_explicit_literal(
        indent_level,
        as_unicode('{}{}').format(LITERAL_CONTENT_PREFIX, matched.group('line')),
        matched, source
    )


def parse_raw_html(indent_level, current_line, ___, source):
    buf = [current_line.strip(), '\n']
    while True:
        try:
            lineno, tail_line = next(source)
        except StopIteration:
            break
        tail_indent, tail_line = scan_line(tail_line)
        if not tail_line:
            continue
        # Parse tree
        # --------------------------------------------------------
        while tail_line:
            if tail_indent <= indent_level:
                return joined(buf), tail_indent, tail_line, source

            # tail_indent > indent_level
            matched_obj, parse = search_parser(lineno, tail_line)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
            buf.append(parsed_data)

    return joined(buf), 0, '', source


def parse_mako_one_liners(indent_level, __, matched, source):
    _, __, components, source = extract_plim_line(matched.group('line').strip(), source)
    buf = ['\n<%{tag}'.format(tag=components['name'])]
    if components['content']:
        buf.append(' file="{name}"'.format(name=components['content']))
    if components['attributes']:
        buf.extend([' ', components['attributes']])
    buf.append('/>\n')
    return joined(buf), indent_level, '', source


def parse_def_block(indent_level, __, matched, source):
    _, __, components, source = extract_plim_line(matched.group('line'), source)
    tag = components['name']
    buf = ['<%{def_or_block}'.format(def_or_block=tag)]
    if components['content']:
        buf.append(' name="{name}"'.format(name=components['content'].strip()))
    if components['attributes']:
        buf.extend([' ', components['attributes']])
    buf.append('>\n')

    while True:
        try:
            lineno, tail_line = next(source)
        except StopIteration:
            break
        tail_indent, tail_line = scan_line(tail_line)
        if not tail_line:
            continue
        # Parse tree
        # --------------------------------------------------------
        while tail_line:
            if tail_indent <= indent_level:
                buf.append('</%{def_or_block}>\n'.format(def_or_block=tag))
                return joined(buf), tail_indent, tail_line, source

            # tail_indent > indent_level
            matched_obj, parse = search_parser(lineno, tail_line)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
            buf.append(parsed_data)

    buf.append('</%{def_or_block}>\n'.format(def_or_block=tag))
    return joined(buf), 0, '', source


# Miscellaneous utilities
# ==================================================================================
def enumerate_source(source):
    return enumerate(StringIO(source), start=1)


def scan_line(line):
    """Returns a 2-tuple of (length_of_the_indentation, line_without_preceding_indentation)"""
    match = LINE_PARTS_RE.match(line)
    return len(match.group('indent')), match.group('line')


def compile_plim_source(source):
    source = enumerate_source(source)
    result = []
    while True:
        try:
            lineno, line = next(source)
        except StopIteration:
            break

        tail_indent, tail_line = scan_line(line)
        if not line:
            continue
        while tail_line:
            matched_obj, parse = search_parser(lineno, tail_line)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source)
            result.append(parsed_data)

    return joined(result).strip()


# Acknowledgements
# ============================================================================================
PARSERS = ( # Order matters
    (PARSE_STYLE_SCRIPT_RE, parse_style_script),
    (PARSE_DOCTYPE_RE, parse_doctype),
    (PARSE_PLIM_TREE_RE, parse_plim_tree),
    (PARSE_EXPLICIT_LITERAL_RE, parse_explicit_literal),
    (PARSE_IMPLICIT_LITERAL_RE, parse_implicit_literal),
    (PARSE_RAW_HTML_RE, parse_raw_html),
    (PARSE_VARIABLE_RE, parse_variable),
    (PARSE_COMMENT_RE, parse_comment),
    (PARSE_STATEMENTS_RE, parse_statements),
    (PARSE_FOREIGN_STATEMENTS_RE, parse_foreign_statements),
    (PARSE_PYTHON_RE, parse_python),
    (PARSE_DEF_BLOCK_RE, parse_def_block),
    (PARSE_MAKO_ONE_LINERS_RE, parse_mako_one_liners),
    (PARSE_MAKO_TEXT_RE, parse_mako_text),
    (PARSE_CALL_RE, parse_call),
    (PARSE_EARLY_RETURN_RE, parse_early_return),
    (PARSE_EXTENSION_LANGUAGES_RE, parse_markup_languages)
)

EMPTY_TAGS = {'meta', 'img', 'link', 'input', 'area', 'base', 'col', 'br', 'hr'}

MARKUP_LANGUAGES = {
    'md': markdown2.markdown,
    'markdown': markdown2.markdown,
    'rst': rst_to_html,
    'rest': rst_to_html,
    'coffee': coffee_to_js,
    'scss': scss_to_css,
    'sass': scss_to_css,
    'stylus': stylus_to_css
}

DOCTYPES = {
    'html':'<!DOCTYPE html>',
    '5': '<!DOCTYPE html>',
    '1.1': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
    'strict': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',
    'xml': '<?xml version="1.0" encoding="utf-8" ?>',
    'transitional': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
    'frameset': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">',
    'basic': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN" "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">',
    'mobile': '<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">',
}
