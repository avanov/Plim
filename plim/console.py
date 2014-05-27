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


def plimc(args=None, stdout=None):
    """This is the `plimc` command line utility

    :param args: list of command-line arguments. If None, then ``sys.argv[1:]`` will be used.
    :type args: list or None
    :param stdout: file-like object representing stdout. If None, then ``sys.stdout`` will be used.
                   Custom stdout is used for testing purposes.
    :type stdout: None or a file-like object
    """
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

    if args is None:
        args = sys.argv[1:]
    args = cli_parser.parse_args(args)

    # Get custom preprocessor, if specified
    # -------------------------------------
    preprocessor_path = args.preprocessor
    # Add an empty string path, so modules located at the current working dir
    # are reachable and considered in the first place (see issue #32).
    sys.path.insert(0, '')
    preprocessor = EntryPoint.parse('x={}'.format(preprocessor_path)).load(False)

    # Render to html, if requested
    # ----------------------------
    if args.html:
        root_dir = os.path.dirname(os.path.abspath(args.source))
        template_file = os.path.basename(args.source)
        lookup = TemplateLookup(directories=[root_dir],
                                input_encoding=args.encoding,
                                output_encoding=args.encoding,
                                preprocessor=preprocessor)
        content = lookup.get_template(template_file).render_unicode()
    else:
        with codecs.open(args.source, 'rb', args.encoding) as fd:
            content = preprocessor(fd.read())

    # Output
    # ------------------------------------
    if args.output is None:
        if stdout is None:
            stdout = PY3K and sys.stdout.buffer or sys.stdout
        fd = stdout
        content = codecs.encode(content, 'utf-8')
    else:
        fd = codecs.open(args.output, 'wb', args.encoding)
    try:
        fd.write(content)
    finally:
        fd.close()
