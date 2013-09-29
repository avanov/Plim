import sys


PY3K = sys.version_info >= (3, 0)

if PY3K:
    from io import StringIO

    joined = lambda buf: ''.join(buf)
    space_separated = lambda buf: ' '.join(buf)
    as_unicode = str
    MAXSIZE = sys.maxsize

else:
    from StringIO import StringIO

    joined = lambda buf: as_unicode('').join(buf)
    space_separated = lambda buf: as_unicode(' ').join(buf)
    as_unicode = unicode
    MAXSIZE = sys.maxint
