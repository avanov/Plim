Extensions
===========

Standard extensions
-------------------

CoffeeScript
~~~~~~~~~~~~

Plim uses `Python-CoffeeScript <https://github.com/doloopwhile/Python-CoffeeScript>`_ package
as a bridge to the JS `CoffeeScript <http://coffeescript.org/>`_ compiler.
You can start CoffeeScript block with the ``-coffee`` construct.

.. code-block:: plim

    - coffee
      # Assignment:
      number   = 42
      opposite = true

      # Conditions:
      number = -42 if opposite

      # Functions:
      square = (x) -> x * x

      # Arrays:
      list = [1, 2, 3, 4, 5]

      # Objects:
      math =
        root:   Math.sqrt
        square: square
        cube:   (x) -> x * square x

      # Splats:
      race = (winner, runners...) ->
        print winner, runners

      # Existence:
      alert "I knew it!" if elvis?

      # Array comprehensions:
      cubes = (math.cube num for num in list)


SCSS/SASS
~~~~~~~~~

Plim uses `pyScss <https://github.com/Kronuz/pyScss>`_ package to translate
`SCSS/SASS <http://sass-lang.com/>`_ markup to plain CSS.
You can start SCSS/SASS block with the ``-scss`` or ``-sass`` construct. The output will be
wrapped with ``<style></style>`` tags.

For example,

.. code-block:: plim

    - scss
      @option compress: no;
      .selector {
        a {
          display: block;
        }
        strong {
          color: blue;
        }
      }

produces

.. code-block:: html

    <style>.selector a {
      display: block;
    }
    .selector strong {
      color: #00f;
    }</style>


Stylus
~~~~~~~~~

Plim uses `stylus <https://github.com/bkad/python-stylus>`_ package to translate
`stylus <http://learnboost.github.com/stylus/>`_ markup to plain CSS.
You can start Stylus block with the ``-stylus`` construct. The output will be
wrapped with ``<style></style>`` tags.

For example,

.. code-block:: plim

    - stylus
      @import 'nib'
      body
        background: linear-gradient(top, white, black)
      
      border-radius()
        -webkit-border-radius arguments
        -moz-border-radius arguments
        border-radius arguments
    
      a.button
        border-radius 5px

produces

.. code-block:: html

    <style>body {
      background: -webkit-gradient(linear, left top, left bottom, color-stop(0, #fff), color-stop(1, #000));
      background: -webkit-linear-gradient(top, #fff 0%, #000 100%);
      background: -moz-linear-gradient(top, #fff 0%, #000 100%);
      background: -o-linear-gradient(top, #fff 0%, #000 100%);
      background: -ms-linear-gradient(top, #fff 0%, #000 100%);
      background: linear-gradient(top, #fff 0%, #000 100%);
    }
    a.button {
      -webkit-border-radius: 5px;
      -moz-border-radius: 5px;
      border-radius: 5px;
    }</style>


Markdown
~~~~~~~~

Plim uses `python-markdown2 <https://github.com/trentm/python-markdown2>`_ package
for the ``-markdown`` (or ``-md``) extension.

For example,

.. code-block:: plim

    - markdown
      A First Level Header
      ====================

      A Second Level Header
      ---------------------

      Now is the time for all good men to come to
      the aid of their country. This is just a
      regular paragraph.

      The quick brown fox jumped over the lazy
      dog's back.

      ### Header 3

      > This is a blockquote.
      >
      > This is the second paragraph in the blockquote.
      >
      > ## This is an H2 in a blockquote


produces

.. code-block:: html

    <h1>A First Level Header</h1>

    <h2>A Second Level Header</h2>

    <p>Now is the time for all good men to come to
    the aid of their country. This is just a
    regular paragraph.</p>

    <p>The quick brown fox jumped over the lazy
    dog's back.</p>

    <h3>Header 3</h3>

    <blockquote>
        <p>This is a blockquote.</p>

        <p>This is the second paragraph in the blockquote.</p>

        <h2>This is an H2 in a blockquote</h2>
    </blockquote>


reStructuredText
~~~~~~~~~~~~~~~~

Plim uses `Docutils <http://docutils.sourceforge.net/>`_ package for both supporting
the ``-rest`` (or ``-rst``) extension and project documenting.

For example,

.. code-block:: plim

    - rest
      Grid table:

      +------------+------------+-----------+
      | Header 1   | Header 2   | Header 3  |
      +============+============+===========+
      | body row 1 | column 2   | column 3  |
      +------------+------------+-----------+
      | body row 2 | Cells may span columns.|
      +------------+------------+-----------+
      | body row 3 | Cells may  | - Cells   |
      +------------+ span rows. | - contain |
      | body row 4 |            | - blocks. |
      +------------+------------+-----------+


produces

.. code-block:: html

    <p>Grid table:</p>
    <table border="1">
      <thead valign="bottom">
        <tr>
          <th>Header 1
          </th><th>Header 2
          </th><th>Header 3
        </th></tr>
      </thead>
      <tbody valign="top">
        <tr>
          <td>body row 1
          </td><td>column 2
          </td><td>column 3
        </td></tr>
        <tr>
          <td>body row 2
          </td><td colspan="2">Cells may span columns.
        </td></tr>
        <tr>
          <td>body row 3
          </td><td rowspan="2">Cells may<br>span rows.
          </td><td rowspan="2">
            <ul>
              <li>Cells
              </li><li>contain
              </li><li>blocks.
            </li></ul>
        </td></tr>
        <tr>
          <td>body row 4
        </td></tr>
    </tbody></table>


Handlebars
~~~~~~~~~~

Plim supports a special tag ``handlebars`` that is translated to a handlebars section declaration:

.. code-block:: html

    <script type="text/x-handlebars"></script>


This is particularly useful to developers using `Ember.js <http://emberjs.com/guides/templates/handlebars-basics/>`_.

Here is an example. The following plim document

.. code-block:: plim

    html
        body
            handlebars#testapp
                .container {{outlet}}

            handlebars#about: .container {{outlet}}


will be rendered as

.. code-block:: html

    <html>
        <body>
            <script type="text/x-handlebars" id="testapp">
                <div class="container">{{outlet}}</div>
            </script>
            <script type="text/x-handlebars" id="about">
                <div class="container">{{outlet}}</div>
            </script>
        </body>
    </html>


Extending Plim with custom parsers
----------------------------------

.. versionadded:: 0.9.2

It is possible to extend standard Plim markup with your own directives. This feature allows you
to build your own DSL on top of Plim. For instance, the following example adds a new directive
for parsing HTTP links present in a form of ``http_url > title``.

.. code-block:: python
    :linenos:

    # my_module.py
    import re
    from plim import preprocessor_factory


    PARSE_HTTP_LINKS_RE = re.compile('(?P<url>https?://[^>]+)+\s+>\s+(?P<title>.*)')


    def parse_http_link(indent_level, current_line, matched, source, syntax):
        url = matched.group('url')
        url_title = matched.group('title')
        rt = '<a href="{}">{}</a>'.format(url, url_title)
        return rt, indent_level, '', source


    CUSTOM_PARSERS = [
        (PARSE_HTTP_LINKS_RE, parse_http_link)
    ]


    custom_preprocessor = preprocessor_factory(custom_parsers=CUSTOM_PARSERS, syntax='mako')


The ``parse_http_link()`` function is defined according to the strict API.

Every parser accepts five input arguments:

1) ``indent_level`` - an indentation level of the current line. When the parser reaches a line
   which indentation is lower or equal to ``indent_level``, it returns control to a top-level function.
2) ``current_line`` - a line which is being parsed. This is the line that has been matched by
   ``matched`` object at the previous parsing step.
3) ``matched`` - an instance of :class:`re.MatchObject` of the regex associated with the current parser.
4) ``source`` - an instance of an enumerated object returned by :func:`plim.lexer.enumerate_source`.
5) ``syntax`` - an instance of one of :class:`plim.syntax.BaseSyntax` children.

Every parser returns a 4-tuple of:

1) parsed_data - a string of successfully parsed data
2) tail_indent - an indentation level of the ``tail line``
3) tail_line - a line which indentation level (``tail_indent``) is lower or equal to
   the input ``indent_level``.
4) ``source`` - an instance of enumerated object returned by :func:`plim.lexer.enumerate_source`
   which represents the remaining (untouched) plim markup.


From now on, we can use ``custom_preprocessor`` in exactly the same manner as the standard
``plim.preprocessor``.

Let's create a plim document with extended syntax:

.. code-block:: plim
    :linenos:

    / hamilton.plim
    ---------------
    html
        head:title Alexander Hamilton
        body
            h1 Alexander Hamilton
            ul
                li: http://en.wikipedia.org/wiki/Alexander_Hamilton > Wikipedia Article
                li: http://www.amazon.com/Alexander-Hamilton-Ron-Chernow/dp/0143034758 > Full-length Biography

Here is how we can compile this document into a valid HTML (note the ``-p`` argument):

.. code-block:: bash

    $ plimc -H -p my_module:custom_preprocessor hamilton.plim

The result:

.. code-block:: html
    :linenos:

    <html>
        <head>
            <title>Alexander Hamilton</title>
        </head>
        <body>
            <h1>Alexander Hamilton</h1>
            <ul>
                <li><a href="http://en.wikipedia.org/wiki/Alexander_Hamilton">Wikipedia Article</a></li>
                <li><a href="http://www.amazon.com/Alexander-Hamilton-Ron-Chernow/dp/0143034758">Full-length Biography</a></li>
            </ul>
        </body>
    </html>
