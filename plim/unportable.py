import re



PARSE_IMPLICIT_LITERAL_RE = re.compile(
    # Order matters
    u'(?P<line>(?:'
        u'\$?\{|\(|\[|&.+;|[0-9]+|'
        u'(?:'
            u'[^\u0021-\u007E]'  # not ASCII 33 - 126
            u'|'                 # or
            u'[A-Z]'             # uppercase latin letters (ASCII 65 - 90)
        u')'                     # It is possible because TAG_RE can match only lowercase tag names
    u').*)\s*'
)
