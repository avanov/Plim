import sys


PY3K = sys.version_info >= (3, 0)

if PY3K:
    from io import StringIO

    joined = lambda buf: ''.join(buf)
    space_separated = lambda buf: ' '.join(buf)
    u = str
    MAXSIZE = sys.maxsize

else:
    from StringIO import StringIO

    joined = lambda buf: u('').join(buf)
    space_separated = lambda buf: u(' ').join(buf)
    u = unicode
    MAXSIZE = sys.maxint
