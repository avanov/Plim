=======================
 Framework Integration
=======================


Pyramid
=========

Add ``plim.adapters.pyramid_renderer`` into the ``pyramid.includes`` list of your .ini configuration file

.. code-block:: ini

    [app:main]
    pyramid.includes =
        # ... (other packages)
        plim.adapters.pyramid_renderer

The adapter will add the ``.plim`` renderer for use in Pyramid. This can be overridden and more may be
added via the ``config.add_plim_renderer()`` directive:

.. code-block:: python

    config.add_plim_renderer('.plm', mako_settings_prefix='mako.')

The renderer will load its configuration from a provided mako prefix in the Pyramid
settings dictionary. The default prefix is 'mako.'.

Flask
======

The following code snippet would get Flask working with plim:

.. code-block:: python

    from flask import Flask
    from flask.ext.mako import MakoTemplates, render_template
    from plim import preprocessor

    app = Flask(__name__)
    mako = MakoTemplates(app)
    app.config['MAKO_PREPROCESSOR'] = preprocessor

    @app.route('/')
    def hello():
        return render_template('hello.html', name='mako')

    if __name__ == "__main__":
        app.run(debug=True)

With hello.html in templates dir:

.. code-block:: html
    doctype html
    html
      head
        title hello ${name}
      body
        p hello ${name}



Syntax Highlighters
======================

At this moment, Plim doesn't have syntax highlighters.

But, at a starting point you can use
`Slim syntax highlighters <https://github.com/slim-template/slim#syntax-highlighters>`_,
since most of Plim syntax is the same as of Slim.

Editors support
----------------


* `vim-plim <https://github.com/keitheis/vim-plim>`_ - a Plim port of `vim-slim <https://github.com/slim-template/vim-slim>`_ plugin.


