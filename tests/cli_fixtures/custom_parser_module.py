import re
from plim import preprocessor_factory
from plim.util import joined

PARSE_DISPLAY_COMMENT_RE = re.compile('/!.*')

def parse_can_display_comment(indent_level, current_line, matched, source, syntax):
    return joined(['<!-- ', current_line[2:], ' -->']), indent_level, '', source

CUSTOM_PARSERS = [
    (PARSE_DISPLAY_COMMENT_RE, parse_can_display_comment)
]

custom_preprocessor = preprocessor_factory(custom_parsers=CUSTOM_PARSERS, syntax='mako')
