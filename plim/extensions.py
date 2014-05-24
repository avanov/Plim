from docutils.core import publish_parts
import coffeescript
from scss import Scss
from stylus import Stylus

from .util import u



def rst_to_html(source):
    # This code was taken from http://wiki.python.org/moin/ReStructuredText
    # You may also be interested in http://www.tele3.cz/jbar/rest/about.html
    html = publish_parts(source=source, writer_name='html')
    return html['html_body']


def coffee_to_js(source):
    return u('<script>{js}</script>').format(js=coffeescript.compile(source))


def scss_to_css(source):
    css = Scss().compile(source).strip()
    return u('<style>{css}</style>').format(css=css)


def stylus_to_css(source):
    compiler = Stylus()
    return u('<style>{css}</style>').format(css=compiler.compile(source).strip())
