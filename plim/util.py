import sys
from typing import Sequence, Iterable

PY3K = sys.version_info >= (3, 0)

from io import StringIO


def joined(buf: Iterable[str], sep: str = '') -> str:
    """ note: `buf` iterable will be fully consumed, so if you are passing a stream make sure you tee it
    if you need to use the `buf` again later
    """
    return sep.join(buf)


def space_separated(buf: Sequence[str]) -> str:
    return joined(buf, ' ')


u = str
MAXSIZE = sys.maxsize
