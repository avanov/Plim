"""
This module contains entry points for command-line utilities provided by Plim package.
"""
import sys
import os
import argparse
import codecs
from pkg_resources import get_distribution
from pkg_resources import EntryPoint

from mako.template import Template
from mako.lookup import TemplateLookup

from .util import PY3K


def plimc():
    """This is the `plimc` command line utility"""
    # Parse arguments
    # ------------------------------------
    cli_parser = argparse.ArgumentParser(description='Compile plim source files into mako files.')
    cli_parser.add_argument('source', help="path to source plim template")
    cli_parser.add_argument('-o', '--output', help="write result to FILE.")
    cli_parser.add_argument('-e', '--encoding', default='utf-8', help="content encoding")
    cli_parser.add_argument('-p', '--preprocessor', default='plim:preprocessor',
                            help="Preprocessor instance that will be used for parsing the template")
    cli_parser.add_argument('-H', '--html', action='store_true', help="Render HTML output instead of Mako template")
    cli_parser.add_argument('-V', '--version', action='version',
                            version='Plim {}'.format(get_distribution("Plim").version))
    args = cli_parser.parse_args()

    # Get custom preprocessor, if specified
    # -------------------------------------
    preprocessor_path = args.preprocessor
    preprocessor = EntryPoint.parse('x={}'.format(preprocessor_path)).load(False)

    # Render to html, if requested
    # ----------------------------
    if args.html:
        root_dir = os.path.dirname(os.path.abspath(args.source))
        lookup = TemplateLookup(directories=[root_dir], preprocessor=preprocessor)
        content = lookup.get_template(args.source).render_unicode()
    else:
        with codecs.open(args.source, 'rb', args.encoding) as fd:
            content = preprocessor(fd.read())

    # Output
    # ------------------------------------
    if args.output is None:
        fd = PY3K and sys.stdout.buffer or sys.stdout
        content = codecs.encode(content, 'utf-8')
    else:
        fd = codecs.open(args.output, 'wb', args.encoding)
    try:
        fd.write(content)
    finally:
        fd.close()
