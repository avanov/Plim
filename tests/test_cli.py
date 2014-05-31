import os
import subprocess
import sys
import codecs
import tempfile
import shutil

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

    def test_custom_preprocessor(self):
        initial_cwd = os.getcwd()
        tmp_dir = tempfile.mkdtemp()
        os.chdir(tmp_dir)

        # copy test module into the temporary dir
        test_items = (
            ('custom_parser_module.py', 'a.py'),
            ('custom_parser_template.plim', 'a.plim')
        )
        for item_src, item_dest in test_items:
            item_src = os.path.join(initial_cwd, 'tests', 'cli_fixtures', item_src)
            item_dest = os.path.join(tmp_dir, item_dest)
            shutil.copy(item_src, item_dest)

        # Make tests
        data = subprocess.Popen(
            ['plimc', '-p', 'a:custom_preprocessor', 'a.plim'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        ).communicate()[0]
        data = codecs.decode(data, 'utf-8')

        self.assertNotEqual(initial_cwd, os.getcwd())
        self.assertIn('', sys.path)
        self.assertEqual(data, '<!-- But this comment can display in html -->')

        # Cleanup
        os.chdir(initial_cwd)
        shutil.rmtree(tmp_dir)
