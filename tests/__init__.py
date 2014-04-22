# -*- coding: utf-8 -*-
import os
import codecs
import unittest
import plim
from plim import syntax



class TestCaseBase(unittest.TestCase):
    def setUp(self):
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'fixtures')
        self.maxDiff = None
        self.syntax = plim.syntax.Mako()

    def tearDown(self):
        pass

    def get_file_contents(self, template_name):
        return  codecs.open(os.path.join(self.templates_dir, template_name), 'r', 'utf-8').read()

    def check_relevant_chars(self, value1, value2):
        value1 = value1.strip().replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n', '\n')
        value2 = value2.strip().replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n', '\n')
        self.assertEqual(value1, value2)


class TestPreprocessorSyntax(TestCaseBase):

    def test_plim(self):
        cases = [
            'pipe',
            'plim_line',
            'if',
            'unless',
            'python',
            'for',
            'while',
            'until',
            'with',
            'try',
            'def_block',
            'style_script',
            'comment',
            'one_liners',
            'mako_text',
            'early_return',
            'call',
            'multiline_variable',
            'literal_one_liners',
            'no_filtering',
            'linebreak',
            'explicit_space',
            'unicode_attributes',
            'inline_conditions',
            'handlebars',
        ]
        for test_case in cases:
            source = self.get_file_contents(test_case + '_test.plim')
            result = self.get_file_contents(test_case + '_result.mako')
            data = plim.preprocessor(source)
            self.check_relevant_chars(data.strip(), result.strip())


    def test_dynamic_attributes(self):
        test_case = 'dynamic_attributes'
        source = self.get_file_contents(test_case + '_test.plim')
        result = self.get_file_contents(test_case + '_result.mako')
        data = plim.preprocessor(source)
        # normalize data
        data = data.replace("<a \n", "<a\n")
        # normalize for Test4
        data = data.replace("\n \n", "\n\n")
        self.assertEqual(data.strip(), result.strip())

    def test_inline_loops(self):
        test_case = 'inline_loop'
        source = self.get_file_contents(test_case + '_test.plim')
        result = self.get_file_contents(test_case + '_result.mako')
        data = plim.preprocessor(source)
        self.assertEqual(data.strip(), result.strip())

    def test_embedded_markup(self):
        test_case = 'embedded'
        source = self.get_file_contents(test_case + '_test.plim')
        result = self.get_file_contents(test_case + '_result.mako')
        data = plim.preprocessor(source)
        # normalize result
        result = result.strip().replace('\n---\n', '')
        self.assertEqual(data.strip(), result)
