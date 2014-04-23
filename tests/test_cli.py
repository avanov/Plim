from plim import syntax
from plim.console import plimc
from plim.util import PY3K
from . import TestCaseBase


class TestCLI(TestCaseBase):

    def setUp(self):
        super(TestCLI, self).setUp()
        self.mako_syntax = syntax.Mako()
        if PY3K:
            from io import BytesIO
            self.stdout = BytesIO()
        else:
            from StringIO import StringIO
            self.stdout = StringIO()

    def test_cli_mako_output(self):
        plimc(['tests/fixtures/unicode_attributes_test.plim'], stdout=self.stdout)

    def test_cli_html_output(self):

        plimc(['--html', 'tests/fixtures/unicode_attributes_test.plim'], stdout=self.stdout)
