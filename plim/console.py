"""
This module contains entry points for command-line utilities provided by Plim package.
"""
import sys
import os
import argparse
import codecs
from pkg_resources import get_distribution

from mako.template import Template
from mako.lookup import TemplateLookup

from .lexer import compile_plim_source


def plimc():
    """This is the `plimc` command line utility"""
    # Parse arguments
    # ------------------------------------
    cli_parser = argparse.ArgumentParser(description='Compile plim source files into mako files.')
    cli_parser.add_argument('source', help="path to source plim template")
    cli_parser.add_argument('-o', '--output', help="write result to FILE.")
    cli_parser.add_argument('-e', '--encoding', default='utf-8', help="content encoding")
    cli_parser.add_argument('-H', '--html', action='store_true', help="Render HTML output instead of Mako template")
    cli_parser.add_argument('-V', '--version', action='version',
                            version='Plim {}'.format(get_distribution("Plim").version))
    args = cli_parser.parse_args()

    # Get mako source
    # ------------------------------------
    with codecs.open(args.source, 'rb', args.encoding) as fd:
        content = compile_plim_source(fd.read())

    # Get html source if requested
    # ------------------------------------
    if args.html:
        root_dir = os.path.dirname(os.path.abspath(args.source))
        lookup = TemplateLookup(directories=[root_dir])
        content = Template(content, lookup=lookup).render()

    # Output
    # ------------------------------------
    fd = sys.stdout if args.output is None else codecs.open(args.output, 'wb', args.encoding)
    try:
        fd.write(content)
    finally:
        fd.close()
