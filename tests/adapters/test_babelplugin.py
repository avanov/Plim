# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from plim.adapters.babelplugin import extract
from plim.util import StringIO
from .. import TestCaseBase



class TestBabelPlugin(TestCaseBase):

    def test_babel_extractor(self):
        fileobj = StringIO(self.get_file_contents('babelplugin_test.plim'))
        keywords = ['_', 'gettext', 'ungettext', 'pluralize']
        extracted = [(data[1], data[2]) for data in extract(fileobj, keywords, None, {})]
        
        assert ('_', 'Test') in extracted
        assert ('_', 'View more') in extracted

        assert ('pluralize', ('${num} conversation has been marked as read.',
                              '${num} conversations have been marked as read.',
                              None, None)) in extracted
        assert ('ungettext', ('{num} conversation has been marked as read.',
                              '{num} conversations have been marked as read.',
                              None)) in extracted
        
        assert ('gettext', 'N') not in extracted


