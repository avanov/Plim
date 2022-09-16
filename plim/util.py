import sys

PY3K = sys.version_info >= (3, 0)

from io import StringIO

joined = lambda buf: ''.join(buf)
space_separated = lambda buf: ' '.join(buf)
u = str
MAXSIZE = sys.maxsize
