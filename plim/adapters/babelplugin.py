"""gettext message extraction via Babel: http://babel.edgewall.org/"""
from mako.ext.babelplugin import extract as _extract_mako

from .. import preprocessor_factory
from ..util import StringIO, PY3K


def extractor_factory(preprocessor=None):
    if preprocessor is None:
        preprocessor = preprocessor_factory()

    def babel_extractor(fileobj, keywords, comment_tags, options):
        """ Extract messages from Plim templates.

        :param fileobj: the file-like object the messages should be extracted from
        :param keywords: a list of keywords (i.e. function names) that should be
                         recognized as translation functions
        :param comment_tags: a list of translator tags to search for and include
                             in the results
        :param options: a dictionary of additional options (optional)
        :return: an iterator over ``(lineno, funcname, message, comments)`` tuples
        :rtype: ``iterator``
        """
        raw_data = fileobj.read()
        if not PY3K:
            encoding = options.get('input_encoding', options.get('encoding', 'utf-8'))
            raw_data = raw_data.decode(encoding)
        data = preprocessor(raw_data)
        for extracted in _extract_mako(StringIO(data), keywords, comment_tags, options):
            yield extracted

    return babel_extractor

# Default Plim extractor
extract = extractor_factory()
