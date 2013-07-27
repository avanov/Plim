from .lexer import compile_plim_source

from mako.template import Template

import sys
import os.path
import argparse
import codecs


def main():
    """This is the `plimc` command line utility"""
    args = _parse_arguments()

    encoding = args.encoding
    content = _compile_to_mako(args.source, encoding=encoding)

    if args.html:
        _add_source_folder_path_for_import(args.source)
        content = _render_mako_to_html(content)

    _write_output(content, args.output, encoding)


def _parse_arguments():
    cli_parser = argparse.ArgumentParser(
        description='Compile plim source files into mako files.'
    )
    cli_parser.add_argument('source',
                            help="path to source plim template")
    cli_parser.add_argument('-o', '--output',
                            help="write result to FILE.")
    cli_parser.add_argument('-e', '--encoding', default='utf-8',
                            help="content encoding")
    cli_parser.add_argument('-H', '--html', action='store_true',
                            help="Render HTML output instead of Mako template")
    #cli_parser.add_argument('-v', '--version',
                            #action='version',
                            #version='Plim {}'.format('0.8.1'))
    args = cli_parser.parse_args()
    return args


def _write_output(content, target=None, encoding='utf-8'):
    if target:
        with codecs.open(target, 'wb', encoding) as fd:
            fd.write(content)
    else:
        print(content)


def _compile_to_mako(source, encoding='utf-8'):
    with codecs.open(source, 'rb', encoding) as fd:
        mako_markup = compile_plim_source(fd.read())
    return mako_markup


def _add_source_folder_path_for_import(source):
    sys.path.append(os.path.dirname(os.path.realpath(source)))


def _render_mako_to_html(mako_markup):
    return Template(mako_markup).render()
