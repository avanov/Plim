.. Plim documentation master file, created by
   sphinx-quickstart on Sun Jun 10 21:08:09 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========================
 Plim Documentation
=========================

.. image:: https://pypip.in/v/Plim/badge.png
        :target: https://crate.io/packages/Plim

.. image:: https://pypip.in/d/Plim/badge.png
        :target: https://crate.io/packages/Plim

.. image:: https://api.travis-ci.org/avanov/Plim.png
        :target: https://travis-ci.org/avanov/Plim

.. image:: https://coveralls.io/repos/avanov/Plim/badge.png?branch=develop
        :target: https://coveralls.io/r/avanov/Plim?branch=develop


Plim is a Python port of `Ruby's Slim template language <http://slim-lang.com/>`_
built on top of `Mako Templates <http://www.makotemplates.org/>`_.
It uses `Mako's preprocessor feature <http://docs.makotemplates.org/en/latest/usage.html?highlight=preprocessor#api-reference>`_
to translate its syntax into a valid HTML/Mako markup.


Installation
=============

.. code-block:: bash

   pip install Plim


Tests
=======

Plim provides an extensive test suite based on
`nosetests <http://nose.readthedocs.org/en/latest/>`_.
You can run the tests with the following command

.. code-block:: bash

    python setup.py nosetests

Coverage statistics are `available online <https://coveralls.io/r/avanov/Plim?branch=develop>`_.


Detailed example
=================

.. code-block:: plim

    / base.html
    --------------------------
    doctype html
    html = next.body()


.. code-block:: plim

    / helpers.html
    --------------------------
    -def other_headers()
        meta charset="utf-8"
        link rel="stylesheet" href="/static/css/main.css"


.. code-block:: plim

    / layout.html
    --------------------------
    -inherit base.html
    -namespace name="helper" helpers.html

    head
      title Plim Example
      meta name="keywords" content="template language"
      = helper.other_headers()

      script
        /* "script" and "style" blocks do not require explicit literal indicator "|"  */
        $(content).do_something();

      style
        body {
          background:#FFF;
          }

      -scss
        /* SCSS/SASS extension */
        @option compress: no;
        .selector {
          a {
            display: block;
          }
          strong {
            color: blue;
          }
        }

      -coffee
        # CoffeeScript extension
        square = (x) -> x * x

    body
      h1 Markup examples
      #content.example1
        p Nest by indentation
        <div>
          p Mix raw HTML and Plim markup
        </div>

        -md
          Use Markdown
          ============

          See the syntax on [this page][1].

          [1]: http://daringfireball.net/projects/markdown/basics

        -rest
          or Use reStructuredText
          =======================

          See the syntax on `this page`_.

          .. _this page: http://docutils.sourceforge.net/docs/user/rst/quickref.html


      -if items
        table: -for item in items: tr
          td = item.name
          td = item.price
      -elif show_empty
        p No items found
      -else
        a href=request.route_url('items.add') =, _('Add items')

      -unless user.authenticated
        p Please, sign in.
      -else
        p Welcome, ${user.name}!
        ul
          --- i = 0
              limit = 5

          -while i < limit
            li#idx-${i}.up: a href='#' title="Title" == i
            --- i += 1

          -until i < 0
            li#idx-${i}.down-${i}: a href='''#''' title="""Title""" ==, i
            --- i -= 1

      #footer
        Copyright &copy; 2014.
        -include footer_links.html

    = render('tracking_code')


Main Documentation
===================

.. toctree::
   :maxdepth: 3

   en/syntax.txt
   en/differences.txt
   en/extensions.txt
   en/frameworks.txt
   en/cli.txt
   en/license.txt
   en/authors.txt
   en/related.txt
   en/changes.txt


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

