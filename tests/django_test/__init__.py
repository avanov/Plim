# -*- coding: utf-8 -*-
import os

import plim
from plim import lexer as l
from plim import syntax
from plim.errors import PlimSyntaxError, ParserNotFound
from .. import TestCaseBase



class TestDjangoSyntax(TestCaseBase):

    def setUp(self):
        super(TestDjangoSyntax, self).setUp()
        self.preprocessor = plim.preprocessor_factory(syntax='django')
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'fixtures')

    def test_conditionals(self):
        test_case = 'if'
        source = self.get_file_contents(test_case + '_test.plim')
        result = self.get_file_contents(test_case + '_result.djhtml')
        data = self.preprocessor(source)
        self.check_relevant_chars(data.strip(), result.strip())
