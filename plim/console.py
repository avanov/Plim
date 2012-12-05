from .lexer import compile_plim_source
import argparse
import codecs



def plim_compiler():
    """This is the `plimc` command line utility"""
    cli_parser = argparse.ArgumentParser(
        description='Compile plim source files into mako files.'
    )
    cli_parser.add_argument('source', help="path to source plim template")
    cli_parser.add_argument('target',  help="path to target mako template")
    cli_parser.add_argument('--encoding',  help="source file encoding")
    args = cli_parser.parse_args()

    encoding = args.encoding or 'utf-8'
    with codecs.open(args.source, 'rb',encoding) as fd:
        mako_markup = compile_plim_source(fd.read())

    with codecs.open(args.target, 'wb', encoding) as fd:
        fd.write(mako_markup)
