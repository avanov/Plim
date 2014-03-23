# -*- coding: utf-8 -*-
import os
from plim import lexer as l
from plim import syntax
from plim.errors import PlimSyntaxError, ParserNotFound
from .. import TestCaseBase



class TestDjangoSyntax(TestCaseBase):

    def setUp(self):
        super(TestDjangoSyntax, self).setUp()
        self.syntax = syntax.Django()
