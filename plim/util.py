import sys
from typing import Sequence

PY3K = sys.version_info >= (3, 0)

from io import StringIO


def joined(buf: Sequence[str], sep: str = '') -> str:
    return sep.join(buf)


def space_separated(buf: Sequence[str]) -> str:
    return joined(buf, ' ')


u = str
MAXSIZE = sys.maxsize
