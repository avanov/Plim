Command-line Interface
======================

.. versionadded:: 0.7.12

The package provides the command-line tool ``plimc`` to compile plim
source files into Mako templates.

.. code-block:: shell

    $ plimc -h
    usage: plimc [-h] [-o OUTPUT] [-e ENCODING] [-p PREPROCESSOR] [-H] [-V] source

    Compile plim source files into mako files.

    positional arguments:
      source               path to source plim template

    optional arguments:
      -h, --help           show this help message and exit
      -o OUTPUT, --output OUTPUT
                           write result to FILE.
      -e ENCODING, --encoding ENCODING
                           content encoding
      -p PREPROCESSOR, --preprocessor PREPROCESSOR
                           Preprocessor instance that will be used for parsing
                           the template
      -H, --html           Render HTML output instead of Mako template
      -V, --version        show program's version number and exit

