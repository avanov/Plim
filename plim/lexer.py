# -*- coding: utf-8 -*-
"""Plim lexer"""
import functools
import re

import markdown2

from . import errors
from .util import StringIO, MAXSIZE, joined, space_separated, u
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
DYNAMIC_ATTRIBUTES_PREFIX = '**'
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

STATEMENT_CONVERT = {
    'unless': 'if not (',
    'until': 'while not ('
}

INLINE_PYTHON_TERMINATOR = '---'

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

STATEMENT_TERMINATORS = {INLINE_TAG_SEPARATOR, NEWLINE}

PYTHON_EXPR_OPEN_BRACES_RE = re.compile('(?P<start_brace>\(|\{|\[).*')
PYTHON_EXPR_CLOSING_BRACES_RE = re.compile('\)|\}|\].*')

MAKO_EXPR_START_BRACE_RE = re.compile('(?P<start_brace>\$\{).*')
MAKO_EXPR_COUNT_OPEN_BRACES_RE = re.compile('\{')
MAKO_EXPR_COUNT_CLOSING_BRACES_RE = re.compile('\}')
QUOTES_RE = re.compile('(?P<quote_type>\'\'\'|"""|\'|").*') # order matters!

EMBEDDING_QUOTE = '`'
EMBEDDING_QUOTE_ESCAPE = EMBEDDING_QUOTE * 2
EMBEDDING_QUOTE_END = '`_'
EMBEDDING_QUOTES_RE = re.compile('(?P<quote_type>{quote_symbol}).*'.format(quote_symbol=EMBEDDING_QUOTE))


# ============================================================================================
# Okay, let's get started.
# There are three different types of functions below: searchers, parsers, and extractors.
# They are grouped together by API and task similarity.
#
# -- SEARCHERS are helper functions that try to figure out the next step of parsing process
#    based on the current chunk of data.
#    Each searcher MUST accept one required first positional argument *line*.
# ------------------------------
#
# -- PARSERS are the building blocks of Plim. They follow the strict API rules for both
#    input and return values.
#
#    Every parser MUST accept five input arguments:
#    1) ``indent_level`` - an indentation level of the current line. When the parser reaches a line
#       which indentation is lower or equal to ``indent_level``, it returns control to a top-level function.
#    2) ``current_line`` - a line which is being parsed. This is the line that has been matched by
#       ``matched`` object at the previous parsing step.
#    3) ``matched`` - an instance of ``re.MatchObject`` of the regex associated with the current parser.
#    4) ``source`` - an instance of an enumerated object returned by :func:`enumerate_source`.
#    5) ``parsers`` - a tuple of 2-tuples of (parser_regex, parser_callable). Plim uses ``STANDARD_PARSERS``
#                     as a default collection of parsers that can be extended by third-party packages.
#
#    Every parser MUST return a 4-tuple of:
#    1) parsed_data - a string of successfully parsed data
#    2) tail_indent - an indentation level of the ``tail line``
#    3) tail_line - a line which indentation level (``tail_indent``) is lower or equal to
#       the input ``indent_level``.
#    4) ``source`` - an instance of enumerated object returned by :func:`enumerate_source`
#       which represents the remaining (untouched) plim markup.
# ------------------------------
#
# -- EXTRACTORS are "light" versions of parsers. Their input arguments
#    and return values are task-specific. However, they still have several common features:
#      - Each extractor has its own starting and termination sequences.
#      - Each extractor tries to find the starting sequence of characters at the beginning
#        of the input line. If that attempt fails, the extractor returns None (in most cases).
#        If the attempt is successful, the extractor captures all the input characters up to
#        the termination sequence.
#      - The return value of the succeeded extractor MUST contain not only the extracted value,
#        but also an instance of enumerated object returned by :func:`enumerate_source`.
# ------------------------------
#
# P.S. I intentionally did not use "for" statements in conjunction with iterators.
# I wanted to make all parsers free from implicit side-effects.
# Therefore, you can find a number of "while True" and "try/except StopIteration" constructs below.

# Searchers
# ==================================================================================
def search_quotes(line, escape_char='\\', quotes_re=QUOTES_RE):
    """

    :param line: may be empty
    :type line: str
    :param escape_char:
    """
    match = quotes_re.match(line)
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


def search_parser(lineno, line, syntax):
    """Finds a proper parser function for a given line or raises an error

    :param lineno:
    :param line:
    :type syntax: :class:`plim.syntax.BaseSyntax`
    """
    for template, parser in syntax.parsers:
        matched = template.match(line)
        if matched:
            return matched, parser
    raise errors.ParserNotFound(lineno, line)


# Extractors
# ==================================================================================
def extract_embedding_quotes(content):
    """
    ``content`` may be empty

    :param content:
    :param escape_seq:
    """
    match = EMBEDDING_QUOTES_RE.match(content)
    if not match:
        return None

    original_string = [EMBEDDING_QUOTE]
    embedded_string = []
    tail = content[1:]

    while tail:
        if tail.startswith(EMBEDDING_QUOTE_ESCAPE):
            original_string.append(EMBEDDING_QUOTE_ESCAPE)
            embedded_string.append(EMBEDDING_QUOTE)
            tail = tail[len(EMBEDDING_QUOTE_ESCAPE):]
            continue

        if tail.startswith(EMBEDDING_QUOTE):
            append_seq = EMBEDDING_QUOTE_END if tail.startswith(EMBEDDING_QUOTE_END) else EMBEDDING_QUOTE
            original_string.append(append_seq)
            original_string = joined(original_string)
            content = content[len(original_string):]
            embedded_string = joined(embedded_string)
            return embedded_string, original_string, content

        current_char = tail[0]
        original_string.append(current_char)
        embedded_string.append(current_char)
        tail = tail[1:]

    original_string = joined(original_string)
    pos = len(original_string)
    raise errors.PlimSyntaxError(u('Embedding quote is not closed: "{}"').format(original_string), pos)


def _extract_braces_expression(line, source, starting_braces_re, open_braces_re, closing_braces_re):
    """

    :param line: may be empty
    :type line: str
    :param source:
    :type source: str
    :param starting_braces_re:
    :param open_braces_re:
    :param closing_braces_re:
    """
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


extract_braces = lambda line, source: _extract_braces_expression(line, source,
    PYTHON_EXPR_OPEN_BRACES_RE,
    PYTHON_EXPR_OPEN_BRACES_RE,
    PYTHON_EXPR_CLOSING_BRACES_RE
)

extract_mako_expression = lambda line, source: _extract_braces_expression(line, source,
    MAKO_EXPR_START_BRACE_RE,
    MAKO_EXPR_COUNT_OPEN_BRACES_RE,
    MAKO_EXPR_COUNT_CLOSING_BRACES_RE
)


def extract_identifier(line, source, identifier_start='#', terminators=('.', ' ', CLOSE_BRACE, INLINE_TAG_SEPARATOR)):
    """

    :param line: Current line. It may be empty.
    :type line: str or unicode
    :param source:
    :type source: str
    :param identifier_start:
    :param terminators:
    :type terminators: tuple or set
    """
    if not line or not line.startswith(identifier_start):
        return None

    pos = len(identifier_start)
    buf = [identifier_start]
    tail = line[pos:]
    while tail:
        for terminator in terminators:
            if tail.startswith(terminator):
                return joined(buf).rstrip(), tail, source

        # Let's try to find "mako variable" part of possible css-identifier
        result = extract_mako_expression(tail, source)
        if result:
            expr, tail, source = result
            buf.append(expr)
            continue

        # Check for a string object
        result = search_quotes(tail)
        if result is not None:
            buf.append(tail[:result])
            tail = tail[result:]
            continue

        # Try to search braces of function calls etc
        result = extract_braces(tail, source)
        if result:
            result, tail, source = result
            buf.append(result)
            continue
        current_char = tail[0]
        buf.append(current_char)
        tail = tail[1:]
    return joined(buf).rstrip(), tail, source


def extract_digital_attr_value(line):
    result = NUMERIC_VALUE_RE.match(line)
    if result:
        return result.group('value'), line[result.end():]
    return None


def extract_quoted_attr_value(line, search_quotes=search_quotes, remove_escape_seq=True):
    """

    :param line:
    :param search_quotes:
    :param remove_escape_seq: Sometimes escape sequences have to be removed outside of the extractor.
                              This flag prevents double-escaping of backslash sequences.
    :return:
    """
    result = search_quotes(line)
    if result:
        if line.startswith('"""') or line.startswith("'''"):
            skip = 3
        else:
            skip = 1
        # remove quotes from value
        value = line[skip:result - skip]
        # We have to remove backslash escape sequences from the value, but
        # at the same time, preserve unicode escape sequences like "\u4e2d\u6587".
        if remove_escape_seq:
            value = value.encode('raw_unicode_escape')
            value = value.decode('unicode_escape')
        return value, line[result:]
    return None


def extract_dynamic_attr_value(line, source, terminators, syntax):
    result = extract_identifier(line, source, '', terminators)
    if result is None:
        return None
    result, tail, source = result
    if MAKO_EXPR_START_BRACE_RE.match(line):
        # remove VARIABLE_PLACEHOLDER_START_SEQUENCE and VARIABLE_PLACEHOLDER_END_SEQUENCE from variable
        value = result[len(syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE):-len(syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE)]
    elif line.startswith(OPEN_BRACE):
        # remove "(" and ")" from variable
        value = result[1:-1]
    else:
        value = result
    return value, tail, source


def extract_dynamic_tag_attributes(line, source, syntax, inside_parentheses=False):
    """
    Extract one occurrence of ``**dynamic_attributes``
    :param line:
    :param source:
    :param inside_parentheses:
    """
    if not line.startswith(DYNAMIC_ATTRIBUTES_PREFIX):
        return None
    line = line[len(DYNAMIC_ATTRIBUTES_PREFIX):]

    terminators = {
        WHITESPACE,
        NEWLINE,
        LITERAL_CONTENT_PREFIX,
        LITERAL_CONTENT_SPACE_PREFIX,
        # we want to terminate extract_identifier() by DYNAMIC_ATTRIBUTES_PREFIX,
        # but it contains two characters, whereas the function checks only one character.
        # Therefore, we use a single asterisk terminator here instead of DYNAMIC_ATTRIBUTES_PREFIX.
        '*',
        INLINE_TAG_SEPARATOR,
        LINE_BREAK
    }
    if inside_parentheses:
        terminators.add(CLOSE_BRACE)

    result = extract_identifier(line, source, '', terminators)
    if result is None:
        return None

    expr, tail, source = result
    attributes = u(
        '\n%for __plim_key__, __plim_value__ in {expr}.items():\n'
        '{var_start}__plim_key__{var_end}="{var_start}__plim_value__{var_end}"\n'
        '%endfor\n'
    ).format(
        expr=expr,
        var_start=syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE,
        var_end=syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE
    )
    return attributes, tail, source



def extract_tag_attribute(line, source, syntax, inside_parentheses=False):
    """

    :param line:
    :param source:
    :param inside_parentheses:
    :return:
    """
    terminators = inside_parentheses and ATTRIBUTE_TERMINATORS_WITH_PARENTHESES or ATTRIBUTE_TERMINATORS
    result = extract_identifier(line, source, '', terminators)
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
                return u('{attr_name}="{value}"').format(attr_name=attr_name, value=value), tail, source

            # 2. Try to parse digital value
            # -------------------------------------
            result = extract_digital_attr_value(tail)
            if result:
                value, tail = result
                return u('{attr_name}="{value}"').format(attr_name=attr_name, value=value), tail, source

            # 3. Try to parse dynamic value
            # -------------------------------------
            terminators = inside_parentheses and ATTRIBUTE_VALUE_TERMINATORS_WITH_PARENTHESES or ATTRIBUTE_VALUE_TERMINATORS
            result = extract_dynamic_attr_value(tail, source, terminators, syntax)

            if result:
                value, tail, source = result
                # remove possible newline character
                value = value.rstrip()
                if tail.startswith(BOOLEAN_ATTRIBUTE_MARKER):
                    # selected=dynamic_variable?
                    value = u("""{start_var}({value}) and '{attr_name}="{attr_name}"' or ''|n{end_var}""").format(
                        value=value,
                        attr_name=attr_name,
                        start_var=syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE,
                        end_var=syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE
                    )
                    attribute = value
                    tail = tail[1:]
                else:
                    attribute = u('{attr_name}="{start_var}{value}{end_var}"').format(
                        attr_name=attr_name,
                        value=value,
                        start_var=syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE,
                        end_var=syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE
                    )
                return attribute, tail, source
            return None

        elif inside_parentheses and tail.startswith(ATTRIBUTES_DELIMITER) or tail.startswith(CLOSE_BRACE):
            # attribute is presented in a form of boolean attribute
            # which should be converted to attr="attr"
            return u('{attr_name}="{attr_name}"').format(attr_name=attr_name), tail, source
        else:
            return None
    return None


def extract_line_break(tail, source):
    """
    Checks the first character of the tail.

    :param tail:
    :param source:
    :return:
    """
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
    """

    :param tail:
    :param source:
    :return:
    """
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


def extract_tag_line(line, source, syntax):
    """
    Returns a 3-tuple of inline tags sequence, closing tags sequence, and a dictionary of
    last tag components (name, attributes, content)

    :param line:
    :type line: str
    :param source:
    :type source: enumerate
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    """
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
            # remove the preceding '#' character
            css_id = result[1:].rstrip()

        # 2. Parse css class shortcut
        # --------------------------------------------
        class_identifiers = []
        while True:
            result = extract_identifier(tail, source, CSS_CLASS_SHORTCUT_DELIMITER, CSS_CLASS_SHORTCUT_TERMINATORS)
            if result:
                result, tail, source = result
                # remove the preceding '.' character
                class_identifiers.append(result[1:].rstrip())
                continue
            break

        # 3. Parse tag attributes
        # -----------------------------------
        _, tail, source = extract_line_break(tail.lstrip(), source)
        inside_parentheses = tail.startswith(OPEN_BRACE)
        if inside_parentheses:
            tail = tail[1:].lstrip()

        attributes = []
        while True:
            _, tail, source = extract_line_break(tail.lstrip(), source)

            # 3.1 try to get and unpack dynamic attributes
            result = extract_dynamic_tag_attributes(tail, source, syntax, inside_parentheses)
            if result:
                dynamic_attrs, tail, source = result
                attributes.append(dynamic_attrs)
                continue

            # 3.2. get attribute-value pairs until the end of the section (indicated by terminators)
            result = extract_tag_attribute(tail, source, syntax, inside_parentheses)
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
                if inside_parentheses and not tail:
                    # We have reached the end of the line.
                    # Try to parse multiline attributes list.
                    lineno, tail = next(source)
                    continue
                if css_id:
                    attributes.append(u('id="{ids}"').format(ids=css_id))
                if class_identifiers:
                    class_identifiers = space_separated(class_identifiers)
                    attributes.append(u('class="{classes}"').format(classes=class_identifiers))
            break
        attributes = space_separated(attributes)
        components['attributes'] = attributes
        if attributes:
            tag_composer.extend([' ', attributes])

        # 3.2 syntax check
        if inside_parentheses:
            if tail.startswith(CLOSE_BRACE):
                # We have reached the end of attributes definition
                tail = tail[1:].lstrip()
            else:
                raise errors.PlimSyntaxError("Unexpected end of line", tail)
        else:
            if tail.startswith(' '):
                tail = tail.lstrip()

        if html_tag in EMPTY_TAGS:
            tag_composer.append('/>')
        else:
            tag_composer.append('>')
            close_buf.append(u('</{tag}>').format(tag=html_tag))
        buf.append(joined(tag_composer))

        if tail.startswith(INLINE_TAG_SEPARATOR):
            tail = tail[1:].lstrip()
            break

        # 3.3 The remainder of the line will be treated as content
        # ------------------------------------------------------------------
        components['content'] = ''
        if tail:
            if tail.startswith(DYNAMIC_CONTENT_PREFIX):
                tail = tail[1:]
                if tail.startswith(DYNAMIC_CONTENT_PREFIX):
                    # case for the '==' prefix
                    tail = _inject_n_filter(tail)
                    if tail.startswith(DYNAMIC_CONTENT_SPACE_PREFIX):
                        # ensure that a single whitespace is appended
                        tail, source = extract_statement_expression(tail[2:], source)
                        buf.append(u("{start_var}{content}{end_var} ").format(
                            content=tail,
                            start_var=syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE,
                            end_var=syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE
                        ))
                    else:
                        tail, source = extract_statement_expression(tail[1:], source)
                        buf.append(u("{start_var}{content}{end_var}").format(
                            content=tail,
                            start_var=syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE,
                            end_var=syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE
                        ))
                else:
                    if tail.startswith(LITERAL_CONTENT_SPACE_PREFIX):
                        # ensure that a single whitespace is appended
                        tail, source = extract_statement_expression(tail[1:], source)
                        buf.append(u("{start_var}{content}{end_var} ").format(
                            content=tail,
                            start_var=syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE,
                            end_var=syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE
                        ))
                    else:
                        tail, source = extract_statement_expression(tail, source)
                        buf.append(u("{start_var}{content}{end_var}").format(
                            content=tail,
                            start_var=syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE,
                            end_var=syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE
                        ))

            elif tail.startswith(LITERAL_CONTENT_PREFIX):
                tail = _parse_embedded_markup(tail[1:].strip(), syntax)
                buf.append(tail)

            elif tail.startswith(LITERAL_CONTENT_SPACE_PREFIX):
                tail = _parse_embedded_markup(tail[1:].strip(), syntax)
                buf.append(u("{content} ").format(content=tail))

            else:
                tail = _parse_embedded_markup(tail.strip(), syntax)
                buf.append(tail)
            components['content'] = buf[-1]
        tail = ''

    return joined(buf), joined(reversed(close_buf)), components, tail, source


# Parsers
# ==================================================================================
def parse_style_script(indent_level, current_line, matched, source, syntax):
    """

    :param indent_level:
    :param current_line:
    :type current_line: str
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    extracted_html_line, close_buf, _, tail, source = extract_tag_line(current_line, source, syntax)
    buf = [extracted_html_line, '\n']
    parsed_data, tail_indent, tail_line, source = parse_explicit_literal_no_embedded(
        indent_level,
        LITERAL_CONTENT_PREFIX,
        matched,
        source,
        syntax
    )
    buf.extend([parsed_data, close_buf])
    return joined(buf), tail_indent, tail_line, source


def parse_doctype(indent_level, current_line, ___, source, syntax):
    """

    :param indent_level:
    :param current_line:
    :param ___:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    match = syntax.PARSE_DOCTYPE_RE.match(current_line.strip())
    doctype = match.group('type')
    return DOCTYPES.get(doctype, DOCTYPES['5']), indent_level, '', source


def parse_handlebars(indent_level, current_line, ___, source, syntax):
    """

    :param indent_level:
    :param current_line:
    :param ___:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    processed_tag, tail_indent, tail_line, source = parse_tag_tree(indent_level, current_line, ___, source, syntax)
    assert processed_tag.startswith("<handlebars") and processed_tag.endswith("</handlebars>")
    # We don't want to use str.replace() here, therefore
    # len("<handlebars") == len("handlebars>") == 11
    processed_tag = u(
        '<script type="text/x-handlebars"{content}script>'
    ).format(
        content=processed_tag[11:-11]
    )
    return processed_tag, tail_indent, tail_line, source


def parse_tag_tree(indent_level, current_line, ___, source, syntax):
    """

    :param indent_level:
    :param current_line:
    :param ___:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return: 4-tuple
    """
    buf = []
    close_buf = []
    current_line = current_line.strip()
    html_tag, close_seq, _, tail, source = extract_tag_line(current_line, source, syntax)
    buf.append(html_tag)
    close_buf.append(close_seq)
    if tail:
        parsed, tail_indent, tail_line, source = parse_plim_tail(0, indent_level, tail, source, syntax)
        # at this point we have tail_indent <= indent_level
        buf.extend(parsed)
        buf.append(joined(close_buf))
        return joined(buf), tail_indent, tail_line, source

    while True:
        try:
            lineno, current_line = next(source)
        except StopIteration:
            break

        tail_indent, tail_line = scan_line(current_line)
        if not tail_line:
            continue
        if tail_indent <= indent_level:
            buf.append(joined(close_buf))
            return joined(buf), tail_indent, tail_line, source

        # ----------------------------------------------------------
        while tail_line:
            matched_obj, parse = search_parser(lineno, tail_line, syntax)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
            buf.append(parsed_data)
            if tail_indent <= indent_level:
                buf.append(joined(close_buf))
                return joined(buf), tail_indent, tail_line, source

    buf.append(joined(close_buf))
    return joined(buf), 0, '', source


def parse_markup_languages(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    markup_parser = MARKUP_LANGUAGES[matched.group('lang')]
    parsed_data, tail_indent, tail_line, source = parse_explicit_literal_no_embedded(
        indent_level,
        LITERAL_CONTENT_PREFIX,
        matched,
        source,
        syntax
        )
    # This is slow but correct.
    # Trying to remove redundant indentation
    parsed_data = markup_parser(parsed_data)
    return parsed_data.strip(), tail_indent, tail_line, source


def parse_python(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    # TODO: merge with parse_mako_text()
    if matched.group('python').endswith('!'):
        buf = ['<%!\n']
    else:
        buf = ['<%\n']
    inline_statement = matched.group('expr')
    if inline_statement:
        buf.extend([inline_statement.strip(), '\n'])

    parsed_data, tail_indent, tail_line, source = parse_explicit_literal_no_embedded(
        indent_level,
        LITERAL_CONTENT_PREFIX,
        matched,
        source,
        syntax
        )
    # do not render a python block if it's empty
    if not inline_statement and not parsed_data:
        return u(''), tail_indent, tail_line, source

    buf.extend([u('{literal}\n').format(literal=parsed_data.rstrip()), '%>\n'])
    return joined(buf), tail_indent, tail_line, source


def parse_python_new_style(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    buf = [matched.group('excl') and '-py! ' or '-py ']
    inline_statement = matched.group('expr')
    if inline_statement:
        inline_statement, _tail_line_, source = extract_identifier(inline_statement, source, '', {INLINE_PYTHON_TERMINATOR, NEWLINE})
        buf.append(inline_statement)
    converted_line = joined(buf).strip()
    match = syntax.PARSE_PYTHON_CLASSIC_RE.match(converted_line)
    return parse_python(indent_level, __, match, source, syntax)



def parse_mako_text(indent, __, matched, source, syntax):
    """

    :param indent:
    :param __:
    :param matched:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    _, __, components, tail, source = extract_tag_line(matched.group('line').strip(), source, syntax)
    buf = ['\n<%text']
    if components['attributes']:
        buf.extend([' ', components['attributes']])
    buf.append('>\n')
    if components['content']:
        buf.extend([components['content'], '\n'])

    parsed_data, tail_indent, tail_line, source = parse_explicit_literal_no_embedded(
        indent,
        LITERAL_CONTENT_PREFIX,
        matched,
        source,
        syntax
        )
    if parsed_data:
        buf.append(u('{literal}\n').format(literal=parsed_data.rstrip()))
    buf.append('</%text>\n')
    return joined(buf), tail_indent, tail_line, source


def parse_call(indent_level, current_line, matched, source, syntax):
    """

    :param indent_level:
    :param current_line:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return: :raise:
    """
    _, __, components, tail, source = extract_tag_line(matched.group('line').strip(), source, syntax)
    tag = components['content'].strip()
    if not tag:
        raise errors.PlimSyntaxError("-call must contain namespace:defname declaration", current_line)
    buf = [u('\n<%{tag}').format(tag=tag)]
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
                buf.append(u('</%{tag}>\n').format(tag=tag))
                return joined(buf), tail_indent, tail_line, source

            # tail_indent > indent_level
            matched_obj, parse = search_parser(lineno, tail_line, syntax)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
            buf.append(parsed_data)
    buf.append(u('</%{tag}>\n').format(tag=tag))
    return joined(buf), 0, '', source


def parse_comment(indent_level, __, ___, source, syntax):
    """

    :param indent_level:
    :param __:
    :param ___:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
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


def parse_statements(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    stmnt = matched.group('stmnt')
    expr = matched.group('expr')
    buf = [u('\n{statement_start}{statement}').format(
        statement_start=syntax.STATEMENT_START_START_SEQUENCE,
        statement=stmnt
    )]
    if expr:
        expr, source = extract_statement_expression(expr, source)
        expr, tail_line, source = extract_identifier(expr, source, '', STATEMENT_TERMINATORS)
        expr = expr.lstrip()
        tail_line = tail_line[1:].lstrip()
        parsed, tail_indent, tail_line, source = parse_plim_tail(0, indent_level, tail_line, source, syntax)
        buf.append(joined([' ', expr, syntax.STATEMENT_START_END_SEQUENCE, '\n', joined(parsed)]))
    else:
        # So far only the "-try" statement has empty ``expr`` part
        buf.extend([syntax.STATEMENT_START_END_SEQUENCE, '\n'])
        try:
            lineno, tail_line = next(source)
        except StopIteration:
            tail_indent = 0
            tail_line = ''
        else:
            tail_indent, tail_line = scan_line(tail_line)

    def complete_statement(buf, tail_indent, tail_line, source, statement, syntax):
        buf.extend([
            '\n',
            syntax.STATEMENT_END_START_SEQUENCE,
            u('end{statement}').format(statement=statement),
            syntax.STATEMENT_END_END_SEQUENCE,
            '\n'
        ])
        return joined(buf), tail_indent, tail_line, source

    while True:
        # Parse tree
        # --------------------------------------------------------
        while tail_line:
            if stmnt == 'if':
                if tail_indent == indent_level:
                    # Check for elif/else
                    match = syntax.PARSE_ELIF_ELSE_RE.match(tail_line)
                    if match:
                        if match.group('control') == 'elif':
                            expr, source = extract_statement_expression(match.group('expr'), source)
                            expr, tail_line, source = extract_identifier(expr, source, '', STATEMENT_TERMINATORS)
                            expr = expr.lstrip()
                            tail_line = tail_line[1:].lstrip()
                            parsed, tail_indent, tail_line, source = parse_plim_tail(0, indent_level, tail_line, source, syntax)
                            buf.append(joined([
                                '\n',
                                syntax.STATEMENT_START_START_SEQUENCE,
                                u('elif {expr}').format(expr=expr),
                                syntax.STATEMENT_START_END_SEQUENCE,
                                '\n',
                                joined(parsed)
                            ]))
                            if tail_line:
                                continue
                            break
                        else:
                            # "-else" is found
                            expr = match.group('expr')
                            result = extract_identifier(expr, source, '', STATEMENT_TERMINATORS)
                            if result:
                                expr, tail_line, source = extract_identifier(expr, source, '', STATEMENT_TERMINATORS)
                                tail_line = tail_line[1:].lstrip()
                                parsed, tail_indent, tail_line, source = parse_plim_tail(0, indent_level, tail_line, source, syntax)
                                buf.append(joined([
                                    '\n',
                                    syntax.STATEMENT_START_START_SEQUENCE,
                                    'else',
                                    syntax.STATEMENT_START_END_SEQUENCE,
                                    '\n',
                                    joined(parsed)
                                ]))
                                if tail_line:
                                    continue
                            buf.append(joined([
                                '\n',
                                syntax.STATEMENT_START_START_SEQUENCE,
                                'else',
                                syntax.STATEMENT_START_END_SEQUENCE,
                                '\n'
                            ]))
                            break
                    else:
                        # elif/else is not found, finalize and return buffer
                        return complete_statement(buf, tail_indent, tail_line, source, stmnt, syntax)

                elif tail_indent < indent_level:
                    return complete_statement(buf, tail_indent, tail_line, source, stmnt, syntax)

                # tail_indent > indent_level
                matched_obj, parse = search_parser(lineno, tail_line, syntax)
                parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
                buf.append(parsed_data)

            elif stmnt == 'try':
                if tail_indent == indent_level:
                    # Check for except/else/finally
                    match = syntax.PARSE_EXCEPT_ELSE_FINALLY_RE.match(tail_line)
                    if match:
                        if match.group('control') == 'except':
                            expr, source = extract_statement_expression(match.group('expr'), source)
                            buf.append(u('\n%except {expr}:\n').format(expr=expr))
                            break
                        elif match.group('control') == 'else':
                            buf.append('\n%else:\n')
                            break
                        else:
                            # "-finally" is found
                            buf.append('\n%finally:\n')
                            break
                    else:
                        # elif/else is not found, finalize and return the buffer
                        return complete_statement(buf, tail_indent, tail_line, source, stmnt, syntax)

                elif tail_indent < indent_level:
                    return complete_statement(buf, tail_indent, tail_line, source, stmnt, syntax)

                # tail_indent > indent_level
                matched_obj, parse = search_parser(lineno, tail_line, syntax)
                parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
                buf.append(parsed_data)

            else: # stmnt == for/while
                if tail_indent <= indent_level:
                    return complete_statement(buf, tail_indent, tail_line, source, stmnt, syntax)

                # tail_indent > indent_level
                matched_obj, parse = search_parser(lineno, tail_line, syntax)
                parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
                buf.append(parsed_data)

        try:
            lineno, tail_line = next(source)
        except StopIteration:
            break
        tail_indent, tail_line = scan_line(tail_line)

    return complete_statement(buf, 0, '', source, stmnt, syntax)



def parse_foreign_statements(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    stmnt = STATEMENT_CONVERT[matched.group('stmnt')]
    buf = [u('-{statement}').format(statement=stmnt)]
    expr = matched.group('expr')
    expr, source = extract_statement_expression(expr, source)
    buf.append(joined([expr, ')']))

    matched = syntax.PARSE_STATEMENTS_RE.match(joined(buf))
    return parse_statements(indent_level, __, matched, source, syntax)


def parse_explicit_literal(indent_level, current_line, ___, source, syntax, parse_embedded):
    """
    Parses lines and blocks started with the "|" (pipe) or "," (comma) character.

    :param indent_level:
    :param current_line:
    :param ___:
    :param source:
    :param parsers:
    :type parsers: tuple
    :param parse_embedded: whether to parse possible embedded Plim markup
    :type parse_embedded: bool
    """
    # Get rid of the pipe character
    trailing_space_required = current_line[0] == LITERAL_CONTENT_SPACE_PREFIX

    # ---------------------------------
    def prepare_result(buf):
        result = joined(buf).rstrip()
        if trailing_space_required:
            result = u("{} ").format(result)
        if parse_embedded:
            result = _parse_embedded_markup(result, syntax)
        return result

    # --------------------------------
    current_line = current_line[1:]
    _, striped_line = scan_line(current_line)
    # Add line and trailing newline character
    buf = [current_line.strip(), striped_line and "\n" or ""]

    align = MAXSIZE
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
            result = prepare_result(buf)
            return result, indent, line, source

        new_align = len(current_line) - len(current_line.lstrip())
        if align > new_align:
            align = new_align
        # remove preceding spaces
        line = current_line[align:].rstrip()
        buf.extend([line.rstrip(), "\n"])

    result = prepare_result(buf)
    return result, 0, '', source

parse_explicit_literal_with_embedded_markup = functools.partial(parse_explicit_literal, parse_embedded=True)
parse_explicit_literal_no_embedded = functools.partial(parse_explicit_literal, parse_embedded=False)


def _parse_embedded_markup(content, syntax):
    """

    :param content:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    :rtype: str
    """
    buf = []
    tail = content
    while tail:
        if tail.startswith(EMBEDDING_QUOTE_ESCAPE):
            tail = tail[len(EMBEDDING_QUOTE_ESCAPE):]
            buf.append(EMBEDDING_QUOTE)
            continue
        result = extract_embedding_quotes(tail)
        if result:
            embedded, original, tail = result
            embedded = embedded.strip()
            if embedded:
                try:
                    embedded = compile_plim_source(embedded, syntax, False)
                except errors.ParserNotFound:
                    # invalid plim markup, leave things as is
                    buf.append(original)
                else:
                    buf.append(embedded)
            continue

        buf.append(tail[0])
        tail = tail[1:]

    return joined(buf)


def _inject_n_filter(line):
    """
    This is a helper function for :func:parse_variable

    :param line:
    """
    # try to find specified filters
    found_filters = MAKO_FILTERS_TAIL_RE.search(line)
    if found_filters:
        # inject "n" filter to specified filters chain
        line = u('{expr}n,{filters}').format(
            expr=line[:found_filters.start('filters')].rstrip(),
            filters=line[found_filters.start('filters'):]
        )
    else:
        line = u('{expr}|n').format(expr=line)
    return line


def parse_variable(indent_level, __, matched, source, syntax):
    """ = variable or == variable

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    explicit_space = matched.group('explicit_space') and ' ' or ''
    prevent_escape = matched.group('prevent_escape')
    buf = [syntax.VARIABLE_PLACEHOLDER_START_SEQUENCE, matched.group('line')]
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
            # add a closing brace to complete variable expression syntax ("${}" in case of mako).
            buf += syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE + explicit_space
            return buf, indent, line, source
        buf.append(line.strip())

    buf = joined(buf)
    if prevent_escape:
        buf = _inject_n_filter(buf)
    buf += syntax.VARIABLE_PLACEHOLDER_END_SEQUENCE + explicit_space
    return buf, 0, '', source


def parse_early_return(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    return u('\n<% {keyword} %>\n').format(keyword=matched.group('keyword')), indent_level, '', source


def parse_implicit_literal(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    return parse_explicit_literal_with_embedded_markup(
        indent_level,
        u('{}{}').format(LITERAL_CONTENT_PREFIX, matched.group('line')),
        matched,
        source,
        syntax
    )


def parse_raw_html(indent_level, current_line, ___, source, syntax):
    """

    :param indent_level:
    :param current_line:
    :param ___:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    buf = [current_line.strip(), '\n']
    while True:
        try:
            lineno, tail_line = next(source)
        except StopIteration:
            break
        tail_indent, tail_line = scan_line(tail_line)
        if not tail_line:
            continue
        # Parse a tree
        # --------------------------------------------------------
        while tail_line:
            if tail_indent <= indent_level:
                return joined(buf), tail_indent, tail_line, source

            # tail_indent > indent_level
            matched_obj, parse = search_parser(lineno, tail_line, syntax)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
            buf.append(parsed_data)

    return joined(buf), 0, '', source


def parse_mako_one_liners(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    _, __, components, tail, source = extract_tag_line(matched.group('line').strip(), source, syntax)
    buf = [u('<%{tag}').format(tag=components['name'])]
    if components['content']:
        buf.append(u(' file="{name}"').format(name=components['content']))
    if components['attributes']:
        buf.extend([' ', components['attributes']])
    buf.append('/>')
    return joined(buf), indent_level, '', source


def parse_def_block(indent_level, __, matched, source, syntax):
    """

    :param indent_level:
    :param __:
    :param matched:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    _, __, components, tail, source = extract_tag_line(matched.group('line'), source, syntax)
    tag = components['name']
    buf = [u('<%{def_or_block}').format(def_or_block=tag)]
    if components['content']:
        buf.append(u(' name="{name}"').format(name=components['content'].strip()))
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
        # Parse a tree
        # --------------------------------------------------------
        while tail_line:
            if tail_indent <= indent_level:
                buf.append(u('</%{def_or_block}>\n').format(def_or_block=tag))
                return joined(buf), tail_indent, tail_line, source

            # tail_indent > indent_level
            matched_obj, parse = search_parser(lineno, tail_line, syntax)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
            buf.append(parsed_data)

    buf.append(u('</%{def_or_block}>\n').format(def_or_block=tag))
    return joined(buf), 0, '', source


def parse_plim_tail(lineno, indent_level, tail_line, source, syntax):
    """

    :param lineno:
    :param indent_level:
    :param tail_line:
    :param source:
    :param parsers: 2-tuple of (parser_regex, parser_callable)
    :type parsers: tuple
    :return:
    """
    buf = []
    tail_indent = indent_level
    while tail_line:
        matched_obj, parse = search_parser(lineno, tail_line, syntax)
        parsed_data, tail_indent, tail_line, source = parse(indent_level, tail_line, matched_obj, source, syntax)
        buf.append(parsed_data)
        if tail_indent <= indent_level:
            break
    return buf, tail_indent, tail_line, source


# Miscellaneous utilities
# ==================================================================================
def enumerate_source(source):
    """

    :param source:
    :return:
    """
    return enumerate(StringIO(source), start=1)


def scan_line(line):
    """ Returns a 2-tuple of (length_of_the_indentation, line_without_preceding_indentation)

    :param line:
    :type line: str
    """
    match = LINE_PARTS_RE.match(line)
    return len(match.group('indent')), match.group('line')


def compile_plim_source(source, syntax, strip=True):
    """

    :param source:
    :param syntax: a syntax instance
    :type syntax: :class:`plim.syntax.BaseSyntax`
    :param strip: for embedded markup we don't want to strip whitespaces from result
    :type strip: bool
    :return:
    """
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
            matched_obj, parse = search_parser(lineno, tail_line, syntax)
            parsed_data, tail_indent, tail_line, source = parse(tail_indent, tail_line, matched_obj, source, syntax)
            result.append(parsed_data)

    result = joined(result)
    if strip:
        result = result.strip()
    return result


# Acknowledgements
# ============================================================================================

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
