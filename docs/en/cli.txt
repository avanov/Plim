Command-line Interface
======================

.. versionadded:: 0.7.12

The package provides the command-line tool ``plimc`` to compile plim
source files into Mako templates.

.. code-block:: shell

    $ plimc -h
    usage: plimc [-h] [--encoding ENCODING] source target

    Compile plim source files into mako files.

    positional arguments:
      source               path to source plim template
      target               path to target mako template

    optional arguments:
      -h, --help           show this help message and exit
      --encoding ENCODING  source file encoding

