# -*- coding: utf-8 -*-
import os
import codecs
import unittest
import plim



class TestCaseBase(unittest.TestCase):
    def setUp(self):
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'fixtures')

    def tearDown(self):
        pass

    def get_file_contents(self, template_name):
        return  codecs.open(os.path.join(self.templates_dir, template_name), 'r', 'utf-8').read()

    def check_relevant_chars(self, value1, value2):
        value1 = value1.strip().replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n', '\n')
        value2 = value2.strip().replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n', '\n')
        assert value1 == value2


class TestPreprocessorSyntax(TestCaseBase):

    def test_plim(self):
        cases = [
            'pipe', 'plim_line', 'if', 'unless', 'python', 'for', 'while', 'until', 'with',
            'try', 'def_block', 'style_script', 'comment', 'one_liners', 'mako_text',
            'early_return', 'call', 'multiline_variable', 'literal_one_liners', 'no_filtering',
        ]
        for test_case in cases:
            source = self.get_file_contents(test_case + '_test.html')
            result = self.get_file_contents(test_case + '_result.html')
            data = plim.preprocessor(source)
            self.check_relevant_chars(data.strip(), result.strip())
