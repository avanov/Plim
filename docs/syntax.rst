=======================
 Syntax
=======================


Some relevant parts of this section were copied from 
the `official Slim documentation <https://github.com/slim-template/slim>`_.

Line Indicators
==================

``|``
  The pipe tells Plim to just copy the line. It essentially escapes any processing.

``,``
  The comma tells Plim to copy the line (similar to ``|``), but makes sure that a single trailing space is appended.

  .. note:: Slim syntax instead has the single quote ( ``'`` ) line indicator.

``-``
  The dash denotes control code. Examples of control code are loops, conditionals,
  mako tags, and extensions.

``=``
  The equal sign tells Plim it's a Python call that produces output to add to the buffer.

``=,``
  Same as the single equal sign ( ``=`` ), except that it adds an explicit single trailing
  whitespace after the python expression.

``==``
  Same as the single equal sign ( ``=`` ), but adds `the "n" filter <http://docs.makotemplates.org/en/latest/filtering.html>`_
  to mako expression.

  .. code-block:: plim

     == python_expression                       =>      ${python_expression|n}

     == python_expression | custom_filter       =>      ${python_expression |n,custom_filter}


``==,``
  Same as the double equal sign ( ``==`` ), except that it adds an explicit single trailing
  whitespace after the python expression.

``/``
  Use the forward slash for code comments - anything after it won't get displayed in the final mako markup.


  .. note:: **There is no an equivalent syntax for Slim's "/!" html comment**.
      This line indicator has been considered redundant since Plim supports raw HTML tags:

      .. code-block:: plim
    
          / You can use raw HTML comment tags, as well as all other tags
          <!-- HTML comment -->
          <div>
    
            / You can use Plim markup inside the raw HTML
            a href="#" = link.title
    
          / If you use raw HTML, you have to close all tags manually
          </div>


Indentation
==================

Plim indentation rules are the same as of Slim: indentation matters, but it's not as strict as 
`Haml <http://haml.info/about.html>`_.
If you want to first indent 2 spaces, then 5 spaces, it's your choice. To nest markup you only need to
indent by one space, the rest is gravy.

Tag Attributes
===================

Static Attrbutes
----------------

Static tag attributes can be specified in the same form as any valid
python string declaration.

For example

.. code-block:: plim

    input type='text' name="username" value='''Max Power''' maxlength="""32"""

will be rendered as

.. code-block:: html
    
    <input type="text" name="username" value="Max Power" maxlength="32"/>

As in Python string declarations, you must take care of correct quote escaping

.. code-block:: plim

    input value='It\'s simple'
    input value="It's simple"
    input value='''It's simple'''
    input value="""It's simple"""
    
    input value="He said \"All right!\""
    input value='He said "All right!"'
    input value='''He said "All right!"'''
    input value="""He said "All right!\""""


You can omit quotes from numeric attribute values:

.. code-block:: plim

    input type='text' name="measure" value=+.97 maxlength=32

produces

.. code-block:: html

    <input type="text" name="measure" value="+.97" maxlength="32"/>


Dynamic Attributes
------------------

Dynamic values can be specified in forms of:

- Mako expression

  .. code-block:: plim
  
      input type="text" name="username" value="${user.name}" maxlength=32
      a href="${request.route_url('user_profile', tagname=user.login, _scheme='https')}"
  
  or
  
  .. code-block:: plim
  
      input type="text" name="username" value=${user.name} maxlength=32
      a href=${request.route_url('user_profile', tagname=user.login, _scheme='https')}


- Python expression

  .. code-block:: plim
  
      input type="text" name="username" value=user.name maxlength=32
      a href=request.route_url('user_profile', tagname=user.login, _scheme='https')
  
  or with parentheses
  
  .. code-block:: plim
  
      input type="text" name="username" value=(user.name) maxlength=32
      a href=(request.route_url('user_profile', tagname=user.login, _scheme='https'))

All these examples produce the same mako markup:

.. code-block:: mako
  
    <input type="text" name="username" value="${user.name}" maxlength="32"/>
    <a href="${request.route_url('user_profile', tagname=user.login, _scheme='https')}"></a>


Boolean Attributes
-------------------

Boolean attributes can be specified either by static or dynamic method:

Static attribute example:

.. code-block::  plim

    / Static boolean attribute "disabled"
    input type="text" name="username" disabled="disabled"
    
    / If you wrap your attributes with parentheses, you can use
      shortcut form
    input (type="text" name="username" disabled)

Dynamic attribute example (note the trailing question mark):

.. code-block::  plim

    / Dynamic boolean attribute "disabled"
      will be evaluated to 'disabled="disabled"' if `is_disabled`
      evaluates to True
      
    input type="text" name="username" disabled=${is_disabled}?
    
    / or you can write it that way
    input type="text" name="username" disabled=is_disabled?
    
    / or even that way
    input type="text" name="username" disabled=(is_disabled or 
                                                is_really_disabled)?


Dynamic unpacking
--------------------

This feature is an equivalent to
`Slim's splat attributes <https://github.com/slim-template/slim#splat-attributes->`_, but the syntax
was changed in order to correspond to Python's ``**kwargs`` semantics.

Consider the following python dictionary:

.. code-block:: python

    attrs = {
        'id': 'navbar-1',
        'class': 'navbar',
        'href': '#',
        'data-context': 'same-frame',
    }

Now we can unpack the dictionary in order to populate tags with attributes. The following line::

    a**attrs Link

will be translated to mako template which will output an equivalent to the following HTML markup

.. code-block:: html

    <a id="navbar-1" class="navbar" href="#" data-context="same-frame">Link</a>

Here are some other examples

.. code-block:: plim

    a **attrs|Link

    a **attrs **more_attrs Link

    a(**attrs disabled) Disabled Link

    a **function_returning_dict(
      *args, **kwargs
    ) Link



Attribute Wrapping
===================

You can wrap tag attributes with parentheses ``()``. Unlike Slim, Plim doesn't support square ``[]`` or
curly ``{}`` braces for attributes wrapping.

.. code-block:: plim

    body
      h1(id="logo" class="small tagline") = page_logo
      h2 id=(id_from_variable + '-idx') = page_tagline


If you wrap the attributes, you can spread them across multiple lines:

.. code-block:: plim

    body

      h1 (id="logo"
        class="small tagline") = page_logo

      h2 id=(
        id_from_variable +
        '-idx'
      ) = page_tagline


Inline Tag Content
==================

You can put content on the same line with the tag:

.. code-block:: plim

    body
      h1 id="headline" Welcome to my site.


Or nest it. Note: use either a pipe or :ref:`Implicit literal indicators <implicit-literals>`

.. code-block:: plim

    body
      h1 id="headline"

        / Explicit literal with pipe character
        | Welcome to my site.

        / Implicit literal (uppercase letter at the beginning of the line)
        Yes, Welcome to my site


Dynamic Tag Content
====================================

You can make the call on the same line

.. code-block:: plim

    body
      h1 id="headline" = page_headline


Or nest it.

.. code-block:: plim

    body
      h1 id="headline"
        = page_headline


``id`` and ``class`` Shortcuts
====================================

You can specify the id and class attributes in the following shortcut form.

.. code-block:: plim

    body

      / Static shortcuts
      h1#headline
        = page_headline
      h2#tagline.small.tagline
        = page_tagline
      .content
        = show_content


This is the same as:

.. code-block:: plim

    body
      h1 id="headline"
        = page_headline
      h2 id="tagline" class="small tagline"
        = page_tagline
      div class="content"
        = show_content



`In contrast to Slim <https://github.com/slim-template/slim#id-shortcut--and-class-shortcut->`_,
Plim allows you to insert dynamic expressions right into the shortcuts:

.. code-block:: plim

      / Dynamic shortcuts
      h1#headline-${'dynamic'} = page_headline
      h2#${tagline.id}.small-${tagline.cls}.${tagline.other_cls}
        = page_tagline
      .${'content'}
        = show_content


This is the same as:

.. code-block:: plim

      h1 id="headline-${'dynamic'}" = page_headline
      h2 id="${tagline.id}" class="small-${tagline.cls} ${tagline.other_cls}"
        = page_tagline
      div class="${'content'}"
        = show_content


Inline Tags
====================================

Sometimes you may want to be a little more compact and inline the tags.

.. code-block:: plim

    ul
      li.first: a href="/a" A link
      li: a href="/b" B link


For readability, don't forget you can wrap the attributes.

.. code-block:: plim

    ul
      li.first: a(href="/a") A link
      li: a(href="/b") B link

Inline Statements
====================================

You can inline python loops and conditional expressions in the same manner as tags.

.. code-block:: plim

    ul: -for link in ['About', 'Blog', 'Sitemap']: li: a href=route_to(link) = link

will be rendered as

.. code-block:: mako

    <ul>
    %for link in ['About', 'Blog', 'Sitemap']:
    <li><a href="${route_to(link)}">${link}</a></li>
    %endfor
    </ul>

Evaluate Python Code in Text
====================================

Use standard `mako expression syntax <http://docs.makotemplates.org/en/latest/syntax.html#expression-substitution>`_.
The text escaping depends on `mako's default filters settings <http://docs.makotemplates.org/en/latest/filtering.html?highlight=default%20filters#the-default-filters-argument>`_.

.. code-block:: plim

    body
      h1 Welcome ${current_user.name} to the show.
      Explicit non-escaped ${content|n} is also possible.


Currently, Mako doesn't provide a simple way to escape the interpolation of expressions
(i.e. render as is). You can use either the `<%text> <http://docs.makotemplates.org/en/latest/syntax.html#text>`_
tag (or Plim's ``-text`` equivalent for blocks of mako syntax examples), or this trick

.. code-block:: plim

    body
      h1 Welcome ${'${current_user.name}'} to the show.

Embedded Markup
====================================

You can embed plim markup right into literal blocks:

.. code-block:: plim

    a href="#" Embedded `strong string` everywhere

is rendered as

.. code-block:: html

    <a href="#">Embedded <strong>string</strong> everywhere</a>

If you want to put two embedded strings next to each other, add a trailing underscore
character after the first embedded string:

.. code-block:: plim

    a href="#" Embedded `strong string`_`i s` everywhere

is rendered as

.. code-block:: html

    <a href="#">Embedded <strong>string</strong><i>s</i> everywhere</a>

The embedding mechanism is recursive so you can embed plim markup into embedded plim markup:

.. code-block:: plim

    Another `a href="#" very ``strong funny ````i recursive``````` test

is rendered as

.. code-block:: html

    Another <a href="#">very <strong>funny <i>recursive</i></strong></a> test


Skip HTML Escaping
====================================

Use either a double equal sign

.. code-block:: plim

    body
      h1 id="headline"
        == page_headline


or the explicit ``| n`` filter at the end of the expression

.. code-block:: plim

    body
      h1 id="headline"
        = page_headline | n


Code Comments
===================

Use forward slash ``/`` for code comments

.. code-block:: plim

    body
      p
        / This is a comment.
          Indentation is the natural way to get block comments


.. _raw-html:

Raw HTML Tags
====================================

Plim allows you to use raw HTML tag lines, and also to mix them with any 
available control logic. It is particularly useful in situations like this one:

.. code-block:: plim

    - if edit_profile
      / Wrap interface with editable block
      <div id="edit-profile">

    - include new_or_edit_interface.html

    - if edit_profile
      / close wrapper tag
      </div>


Doctype Declarations
====================================

There is no default option for doctype declaration tag. Therefore, you should
explicitly specify the desired doctype:

.. code-block:: plim

    doctype 5


Here is the full list of available doctypes:

**doctype html**

    ``<!DOCTYPE html>``

**doctype 5**

    ``<!DOCTYPE html>``
  
**doctype 1.1**

    ``<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">``
  
**doctype strict**

    ``<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">``

**doctype xml**

    ``<?xml version="1.0" encoding="utf-8" ?>``

**doctype transitional**

    ``<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">``

**doctype frameset**

    ``<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">``
    
**doctype basic**

    ``<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN" "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">``
    
**doctype mobile**

    ``<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">``



Control Logic
==============


**if/elif/else** statements
----------------------------

.. code-block:: plim

      -if items
        table
          -for item in items
            tr
              td = item.name
              td = item.price
      -elif show_empty
        p No items found
      -else
        a href=request.route_url('items.add') =, _('Add items')


**unless** statement
----------------------

This is the shortcut form of the ``- if not (<EXPR>)`` statement.

.. code-block:: plim

   -unless user.authenticated
     p Please, sign in.
   -else
     p Welcome, ${user.name}!


**for** statement
-------------------

.. code-block:: plim

    table
      -for item in items
        tr
          td = item.name
          td = item.price


You can use the ``-continue`` and ``-break`` commands inside the ``-for`` block.
See the section :ref:`Returning Early from a Template <return-early>`.


**while** statement
---------------------

.. code-block:: plim

   -python
     i = 0
     limit = 5
   
   ul
     -while i < limit
       li#idx-${i}.up: a href='#' title="Title" == i
       -py i += 1


You can use the ``-continue`` and ``-break`` commands inside the ``-while`` block.
See the section :ref:`Returning Early from a Template <return-early>`.


**until** statement
-----------------------

This is the shortcut form of the ``- while not (<EXPR>)`` statement.

.. code-block:: plim

   -until i < 0
     li#idx-${i}.down-${i}: a href='''#''' title="""Title""" ==, i
     -py i -= 1


You can use the ``-continue`` and ``-break`` commands inside the ``-until`` block.
See the section :ref:`Returning Early from a Template <return-early>`.


**with** statement
---------------------

The ``% with`` statement was introduced in 
`Mako 0.7.0 <http://www.makotemplates.org/CHANGES>`_.

.. code-block:: plim

    -with <EXPR> as <VAR>
      / Do some stuff
    

**try/except** statements
---------------------------

.. code-block:: plim

    - try
      div = item[0]
      div = price['usd']
      
    - except IndexError
      div IndexError
      
    - except KeyError as e
      div = e


.. _return-early:

Returning Early from a Template
--------------------------------

Plim provides a shortcut to Mako's 
`<% return %> <http://docs.makotemplates.org/en/latest/syntax.html#returning-early-from-a-template>`_
template directive.

.. code-block:: plim

    - if not len(records)
      No records found.
      -return

This is the same as

.. code-block:: plim

    - if not len(records)
      No records found.
      -py return

You can use it at any position of the template, not only inside control structures.

There are also the ``-break`` and ``-continue`` shortcuts, that can be used inside the
``-for``, ``-while``, and ``-until`` loops.



.. _implicit-literals:

Literals
=================

You can specify either explicit or implicit literal blocks. The difference is,
whether you prepend a block with the explicit pipe char ``|`` or start it by one
of the implicit indicators.


Explicit Literals
--------------------

Use a pipe ( ``|`` ) or comma ( ``,`` ) literal indicators to start the escape.
Each following line that is indented greater than the first one is copied over.

.. code-block:: plim

    body
      p
        / Explicit literal
        | This is a test of the text block.


.. code-block:: plim

    body
      p
        |
          This is a test of the text block.


The parsed result of both the above examples:

.. code-block:: html

    <body><p>This is a test of the text block.</p></body>


The left margin is set to the zero. Any additional spaces will be copied over.

.. code-block:: plim

    body
      p
        |  This line is on the zero left margin.
            This line will have one space in front of it.
              This line will have two spaces in front of it.
                And so on...


Implicit Literals
-----------------------

Literal blocks can be implicitly specified by the following starting sequences:

- an uppercase ASCII letter;
- any non-ASCII letter;
- a digit without prefixed positive/negative signs;
- HTML-escaped character, for example ``&nbsp;``;
- Mako open brace sequence ``${``;
- an open square brace ``[``;
- an open parenthesis ``(``;
- any unicode character outside the range of U0021 - U007E (ASCII 33 - 126).

.. code-block:: plim

    p
      | pipe is the explicit literal indicator. It is required if your line starts with
        the non-literal character.
    
    p
      I'm the implicit literal, because my first letter is in uppercase.
    
    p
      1. Digits
      2. are
      3. the
      4. implicit
      5. literals
      6. too.
    
    p
      ${raw_mako_expression} indicates the implicit literal line.
    
    p
      If subsequent lines do not start with implicit literal indicator,
        you must indent them
      | or you can use the "explicit" pipe.


.. only:: html

    .. code-block:: plim
    
        p
          если ваш блок текста написан на русском, или любом другом языке, не
          использующим символы из ASCII-диапазона, то вам даже не обязательно
          использовать заглавную букву в начале блока.
        
          / if your literal blocks are written in Russian, or any other
            language which uses non-ASCII letters, you can put even the
            lowercase letter at the beginning of the block


.. only:: latex

    .. code-block:: plim
    
        p
          / if your literal blocks are written in Russian, or any other 
            language which uses non-ASCII letters, you can put even the 
            lowercase letter at the beginning of the block
            
            Unfortunately, we cannot provide an example of this feature here,
            because current version of Sphinx Documenting tool cannot automatically
            build PDF documentation with unicode characters.
            See an explanation on 
            https://groups.google.com/forum/#!topic/sphinx-dev/kUeROyCyX9w/discussion

      


Python Blocks
========================

Classic Blocks
--------------
Use ``-py`` or ``-python`` to insert the 
`<% %> mako tag <http://docs.makotemplates.org/en/latest/syntax.html#python-blocks>`_.

For example

.. code-block:: plim

   - python x = 1


or

.. code-block:: plim

   -py
       x = 1


or even

.. code-block:: plim

   - python x = 1
       y = x + 1
       if True:
           y += 1
       else:
           y -= 1


In latter case, the first line ``x = 1`` will be aligned with the second line ``y = x + 1``.

New-style blocks
----------------

.. versionadded:: 0.9.1
   New-style blocks were introduced for better readability of embedded python code.

Use a sequence of at least three dashes to start a new-style python block.

Here are the overwritten examples of the classic ones. The results are the same:

.. code-block:: plim

   --- x = 1

.. code-block:: plim

   -------------
       x = 1

.. code-block:: plim

   --- x = 1
       y = x + 1
       if True:
           y += 1
       else:
           y -= 1

And here's an example of how we can use an inline statement for providing a block description

.. code-block:: plim

   ul#userlist
       ---------- # prepare a list of users ---------------
           users = UsersService.get_many(max=100, offset=0)
           friends = UsersService.get_friends_for(users)
       ----------------------------------------------------
       -for user in users: li
           h4: a#user-${user.id} href='#' = user.name
           ul: -for friend in friends[user.id]: li
               a#friend-${friend.id} href='#' = friend.name

the result (indentation will be stripped out):

.. code-block:: mako

    <ul id="userlist">
        <%
            # prepare a list of users
            users = UsersService.get_many(max=100, offset=0)
            friends = UsersService.get_friends_for(users)
        %>

        %for user in users:
            <li>
                <h4>
                    <a href="#" id="user-${user.id}">${user.name}</a>
                </h4>
                <ul>
                    %for friend in friends[user.id]:
                        <li>
                            <a href="#" id="friend-${friend.id}">${friend.name}</a>
                        </li>
                    %endfor
                </ul>
            </li>
        %endfor
    </ul>


Module-level Blocks
========================

Use ``-py!`` or ``-python!`` block to insert the 
`<%! %> mako tag <http://docs.makotemplates.org/en/latest/syntax.html#module-level-blocks>`_.

.. code-block:: plim

    -py!
        import mylib
        import re

        def filter(text):
            return re.sub(r'^@', '', text)

.. versionadded:: 0.9.1
   The same example with a new-style syntax:

.. code-block:: plim

    ---! import mylib
         import re

         def filter(text):
             return re.sub(r'^@', '', text)


Mako Tags
===========================

Plim supports a complete set of 
`Mako Tags <http://docs.makotemplates.org/en/latest/syntax.html#tags>`_,
except the ``<%doc>``. The latter has been considered deprecated, since
Plim itself has built-in support of multi-line comments.

.. note:: As all mako tags start with the ``<`` char, which 
    indicates a :ref:`raw HTML line <raw-html>`, they all can be written
    "as is". The only thing you must remember is to manually close the pair tags.


**-page** tag
----------------

.. code-block:: plim

    -page args="x, y, z='default'"

produces

.. code-block:: mako

    <%page args="x, y, z='default'"/>

See the details of what ``<%page>`` is used for in 
`The body() Method <http://docs.makotemplates.org/en/latest/namespaces.html#namespaces-body>`_
and `Caching <http://docs.makotemplates.org/en/latest/caching.html>`_
sections of Mako Documentation.



**-include** tag
-------------------

.. code-block:: plim
    
    -include footer.html

or

.. code-block:: plim

    -include file="footer.html"

produce the same output

.. code-block:: mako
    
    <%include file="footer.html"/>


See the `<%include> section <http://docs.makotemplates.org/en/latest/syntax.html#include>`_
of Mako Documentation to get more information about this tag.

**-inherit** tag
-------------------

.. code-block:: plim
    
    -inherit base.html

or

.. code-block:: plim
    
    -inherit file="base.html"

will generate the same

.. code-block:: mako

    <%inherit file="base.html"/>
    
See Mako's `inheritance documentation <http://docs.makotemplates.org/en/latest/inheritance.html>`_ 
to get more information about template inheritance.

**-namespace** tag
---------------------

.. code-block:: plim

    -namespace name="helper" helpers.html

or

.. code-block:: plim

    -namespace file="helpers.html" name="helper"

produce

.. code-block:: mako

    <%namespace file="helpers.html" name="helper"/>

See Mako's `namespace documentation <http://docs.makotemplates.org/en/latest/namespaces.html>`_ 
to get more information about template namespaces.


**-def** tag
----------------

.. code-block:: plim

    -def account(accountname, type='regular')
    
or

.. code-block:: plim

    -def name="account(accountname, type='regular')"

produce

.. code-block:: mako

    <%def name="account(accountname, type='regular')">
    </%def>

See Mako's `defs and blocks documentation <http://docs.makotemplates.org/en/latest/defs.html>`_ 
to get more information about functions and blocks.


**-block** tag
-----------------

Unlike ``-def`` statements, blocks can be anonymous

.. code-block:: plim

    -block
      This is an anonymous block.

Or they can be named as functions

.. code-block:: plim

    -block name="post_prose"
      = pageargs['post'].content

or

.. code-block:: plim

    -block post_prose
      = pageargs['post'].content

As in ``-def``, both above examples produce the same result

.. code-block:: mako

    <%block name="post_prose">
    ${pageargs['post'].content}</%block>

You can also specify other block arguments as well

.. code-block:: plim

    - block filter="h"
      html this is some escaped html.


See Mako's `defs and blocks documentation <http://docs.makotemplates.org/en/latest/defs.html>`_ 
to get more information about functions and blocks.


**-call** tag
------------------------------------

This statement allows you to define custom tags.

The following examples

.. code-block:: plim

    -call expression="${4==4}" self:conditional
      |i'm the result
    
    - call expression=${4==4} self:conditional
      | i'm the result
    
    - call self:conditional
      | i'm the result
    
    - call self:conditional

will produce

.. code-block:: mako

    <%self:conditional expression="${4==4}">
    i'm the result
    </%self:conditional>
    
    <%self:conditional expression="${4==4}">
    i'm the result
    </%self:conditional>
    
    <%self:conditional>
    i'm the result
    </%self:conditional>
    
    <%self:conditional>
    </%self:conditional>


Please consult the sections
`<%nsname:defname> <http://docs.makotemplates.org/en/latest/syntax.html#nsname-defname>`_
and 
`Calling a Def with Embedded Content and/or Other Defs <http://docs.makotemplates.org/en/latest/defs.html#defs-with-content>`_
of Mako Documentation to get more information about custom tags.



**-text** tag
----------------

As it is mentioned in 
`Mako documentation <http://docs.makotemplates.org/en/latest/syntax.html#text>`_, 
this tag suspends the Mako lexer’s normal parsing of Mako template directives, 
and returns its entire body contents as plain text. It is used pretty much to write 
documentation about Mako:

.. code-block:: plim

    -text filter="h"
      here's some fake mako ${syntax}
      <%def name="x()">${x}</%def>
    
    - text filter="h" here's some fake mako ${syntax}
      <%def name="x()">${x}</%def>
    
    - text filter="h" = syntax
      <%def name="x()">${x}</%def>
    
    -text
      here's some fake mako ${syntax}
      <%def name="x()">${x}</%def>
    
    -text , here's some fake mako ${syntax}
      <%def name="x()">${x}</%def>
