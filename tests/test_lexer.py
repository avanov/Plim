# -*- coding: utf-8 -*-
from plim import lexer as l
from . import TestCaseBase



class TestLexerFunctions(TestCaseBase):

    def test_control_re(self):
        m = l.PARSE_STATEMENTS_RE.match("- if 1")
        assert m.group('expr') == ' 1'

        m = l.PARSE_STATEMENTS_RE.match("-for i in [1,2,3,4,5]")
        assert m.group('expr') == ' i in [1,2,3,4,5]'


    def test_parse_quotes(self):
        self.assertEqual(l.search_quotes('"test"'), 6)

        str_ = "'test'"
        result = l.search_quotes(str_)
        self.assertEqual(result, 6)
        self.assertEqual(str_, str_[:result])

        self.assertEqual(l.search_quotes(r"'test\''"), 8)
        self.assertEqual(l.search_quotes(r'"test\""'), 8)
        self.assertEqual(l.search_quotes(r"'test\\'"), 8)
        self.assertEqual(l.search_quotes(r"'''test\\'''"), 12)
        self.assertEqual(l.search_quotes("'''test'''"), 10)

        self.assertIsNone(l.search_quotes('"test'))
        self.assertIsNone(l.search_quotes("'test"))
        self.assertIsNone(l.search_quotes(r"'test\'"))
        self.assertIsNone(l.search_quotes('"""test'))
        self.assertIsNone(l.search_quotes("'''test"))


    def test_extract_mako_expression(self):
        str_ = '${x}'
        source = l.enumerate_source('')
        result, tail, _ = l.extract_mako_expression(str_, source)
        self.assertEqual(result, str_)
        self.assertEqual(str_[:len(result)], str_)

        str_ = """${{"test\\"":'test}}}'}}"""
        result, tail, _ = l.extract_mako_expression(str_, source)
        self.assertEqual(result, str_)
        self.assertEqual(str_[:len(result)], str_)

        str_ = """${{"test\\"":{'ddd': 'test}}}', 'eee':{}}}}"""
        result, tail, _ = l.extract_mako_expression(str_, source)
        self.assertEqual(result, str_)
        self.assertEqual(str_[:len(result)], str_)

        str_ = """{{"test\\"":'test}}}'}}"""
        result = l.extract_mako_expression(str_, source)
        self.assertIsNone(result)

        str_ = """{{"test\\"":'test}}}'}"""
        result = l.extract_mako_expression(str_, source)
        self.assertIsNone(result)


    def test_extract_ident(self):
        source = l.enumerate_source('')
        str_ = '#test'
        result, _, __ = l.extract_identifier(str_, source)
        self.assertEqual(result, str_)

        str_ = '#test '
        result, _, __ = l.extract_identifier(str_, source)
        self.assertNotEqual(result, str_)
        self.assertEqual(result, str_.strip())

        str_ = '#test.class'
        result, _, __ = l.extract_identifier(str_, source)
        self.assertNotEqual(result, str_)
        self.assertEqual(str_[:len(result)], '#test')
        self.assertEqual(str_[len(result)], '.')

        str_ = '.test.class'
        result, _, __ = l.extract_identifier(str_, source, '.')
        self.assertNotEqual(result, str_)
        self.assertEqual(str_[:len(result)], '.test')

        str_ = '.${test.test}.class'
        result, _, __ = l.extract_identifier(str_, source, '.')
        self.assertNotEqual(result, str_)
        self.assertEqual(str_[:len(result)], '.${test.test}')

        str_ = '.${test.test}test.class'
        result, _, __ = l.extract_identifier(str_, source, '.')
        self.assertNotEqual(result, str_)
        self.assertEqual(str_[:len(result)], '.${test.test}test')

        str_ = '.test-${test.test}test.class'
        result, _, __ = l.extract_identifier(str_, source, '.')
        self.assertNotEqual(result, str_)
        self.assertEqual(str_[:len(result)], '.test-${test.test}test')

        str_ = '.test-${test.test + "${{\'test\':1}}"}${test}test.class'
        result, _, __ = l.extract_identifier(str_, source, '.')
        self.assertNotEqual(result, str_)
        self.assertEqual(str_[:len(result)], '.test-${test.test + "${{\'test\':1}}"}${test}test')

        str_ = u'.абв.где'
        result, _, __ = l.extract_identifier(str_, source, '.')
        self.assertNotEqual(result, str_)
        self.assertEqual(str_[:len(result)], u'.абв')


    def test_parse_tag_attribute(self):
        def assert_this(str_, parentheses, attr_, tail):
            source = l.enumerate_source('')
            result = l.extract_tag_attribute(str_, source, parentheses)
            self.assertEqual(result[0], attr_)
            self.assertEqual(tail, result[1])

        source = l.enumerate_source('')
        self.assertEqual(l.extract_tag_attribute("", source), None)
        self.assertEqual(l.extract_tag_attribute(" ", source), None)
        self.assertEqual(l.extract_tag_attribute("=", source), None)
        self.assertEqual(l.extract_tag_attribute(" = ", source), None)
        self.assertEqual(l.extract_tag_attribute("|", source), None)
        self.assertEqual(l.extract_tag_attribute("'", source), None)
        self.assertEqual(l.extract_tag_attribute("()", source, True), None)
        self.assertEqual(l.extract_tag_attribute(")", source, True), None)

        assert_this('attr="value"', False, 'attr="value"', '')
        assert_this('attr=${val}', False,  'attr="${val}"', '')
        assert_this('attr=(val)', False,  'attr="${val}"', '')

        # Test digital values
        assert_this('attr=7 attr2=val', False,  'attr="7"', ' attr2=val')
        assert_this('attr=.7 attr2=val', False,  'attr=".7"', ' attr2=val')
        assert_this('attr=-7 attr2=val', False,  'attr="-7"', ' attr2=val')
        assert_this('attr=+7 attr2=val', False,  'attr="+7"', ' attr2=val')
        assert_this('attr=-.7 attr2=val', False,  'attr="-.7"', ' attr2=val')
        assert_this('attr=+.7 attr2=val', False,  'attr="+.7"', ' attr2=val')
        assert_this('attr=10.7 attr2=val', False,  'attr="10.7"', ' attr2=val')
        assert_this('attr=-10.7 attr2=val', False,  'attr="-10.7"', ' attr2=val')
        assert_this('attr=+10.7 attr2=val', False,  'attr="+10.7"', ' attr2=val')
        assert_this('attr=10.107 attr2=val', False,  'attr="10.107"', ' attr2=val')
        assert_this('attr=107 attr2=val', False,  'attr="107"', ' attr2=val')

        assert_this('style=c.selected_cover', False,  'style="${c.selected_cover}"', '')
        assert_this('href=item[\'url\']', False,  'href="${item[\'url\']}"', '')
        assert_this('value=extra_title[0]', False,  'value="${extra_title[0]}"', '')

        assert_this('attr=obj.url(request, func("test([\'") + "{test}".format(test="123"), cover[\'image\'])', False,  'attr="${obj.url(request, func("test([\'") + "{test}".format(test="123"), cover[\'image\'])}"', '')

        assert_this('attr=${val} selected', False,  'attr="${val}"', ' selected')
        assert_this('attr=(val) selected', False,  'attr="${val}"', ' selected')
        assert_this('attr=val selected', False,  'attr="${val}"', ' selected')
        assert_this('attr=_(\'i18n message\') selected', False,  'attr="${_(\'i18n message\')}"', ' selected')
        assert_this('attr=${val}? selected', False,  """${(val) and 'attr="attr"' or ''|n}""", ' selected')
        assert_this('attr=(val)? selected', False,  """${(val) and 'attr="attr"' or ''|n}""", ' selected')
        assert_this('attr=val? selected', False,  """${(val) and 'attr="attr"' or ''|n}""", ' selected')
        assert_this('attr=${val + 1}? selected', False,  """${(val + 1) and 'attr="attr"' or ''|n}""", ' selected')
        assert_this('attr=(val + 1)? selected', False,  """${(val + 1) and 'attr="attr"' or ''|n}""", ' selected')
        assert_this('attr="${val}"? selected', False,  'attr="${val}"', '? selected')
        assert_this('attr="${\\"val\\"}"? selected', False,  'attr="${"val"}"', '? selected')

        assert_this('attr="value")', True, 'attr="value"', ')')
        assert_this('attr=${val})', True, 'attr="${val}"', ')')
        assert_this('attr=(val))', True, 'attr="${val}"', ')')
        assert_this('attr=${val}?)', True, """${(val) and 'attr="attr"' or ''|n}""", ')')
        assert_this('attr=(val)?)', True, """${(val) and 'attr="attr"' or ''|n}""", ')')
        assert_this('attr=(val("test() is a function"))?)', True, """${(val("test() is a function")) and 'attr="attr"' or ''|n}""", ')')
        assert_this('attr=${val} selected)', True, 'attr="${val}"', ' selected)')
        assert_this('attr=(val) selected)', True, 'attr="${val}"', ' selected)')
        assert_this('attr=val) selected', True, 'attr="${val}"', ') selected')
        assert_this('attr="${\\"val\\"}"?) selected', True,  'attr="${"val"}"', '?) selected')

        assert_this('attr${attr}attr="${\\"val\\"}"?) selected', True,  'attr${attr}attr="${"val"}"', '?) selected')


    def test_scan_line(self):
        assert l.scan_line('body') == (0, 'body')
        assert l.scan_line("    div") == (4, 'div')
        assert l.scan_line("") == (0, '')
        assert l.scan_line(" ") == (1, '')


    def test_extract_dynamic_attr_value(self):
        for terminators in (l.ATTRIBUTE_VALUE_WITH_PARENTHESES_TERMINATORS, l.ATTRIBUTE_VALUE_TERMINATORS):
            source = l.enumerate_source('')
            value, tail, _ = l.extract_dynamic_attr_value("(value in func('test') and 'yes' or 'no')", source, terminators)
            assert value == "value in func('test') and 'yes' or 'no'"
            assert tail == ''


    def test_inline_extract_slim_line(self):
        def test_case(template, result):
            source = enumerate('')
            line, close_buf, _, __ = l.extract_slim_line(template, source)
            self.assertEqual(line + close_buf, result)

        test_case(
            'body: #layout: ul#list.cls1.cls2: li.active: a href="#" = Page Title',
            '<body><div id="layout"><ul id="list" class="cls1 cls2"><li class="active"><a href="#">${Page Title}</a></li></ul></div></body>'
        )
        test_case(
            'body: #layout: ul#list.cls1.cls2: li.active: a href="#"=Page Title',
            '<body><div id="layout"><ul id="list" class="cls1 cls2"><li class="active"><a href="#">${Page Title}</a></li></ul></div></body>'
        )
        test_case(
            'body: #layout: ul#list.cls1.cls2: li.active: a href="#" =, Page Title',
            '<body><div id="layout"><ul id="list" class="cls1 cls2"><li class="active"><a href="#"> ${Page Title}</a></li></ul></div></body>'
        )

        # Check parentheses
        test_case(
            'body(): #layout (): ul#list.cls1.cls2(   ): li.active: a ( href="#" ) = Page Title',
            '<body><div id="layout"><ul id="list" class="cls1 cls2"><li class="active"><a href="#">${Page Title}</a></li></ul></div></body>'
        )

        # test dynamic content
        result = '<body>${Test}</body>'
        test_case('body = Test', result)
        test_case('body=Test', result)

        # Test explicit whitespace
        result = '<body> Test</body>'
        test_case('body , Test', result)
        test_case('body,Test', result)

        # Test literals
        result = '<div>Test</div>'
        test_case('div | Test', result)
        test_case('div|Test', result)
        test_case('div|=Test', '<div>=Test</div>')

        # Test dynamic with whitespace
        result = '<div> ${Test}</div>'
        test_case('div=,Test', result)
        test_case('div =, Test', result)
        test_case('div = , Test', '<div>${, Test}</div>')
        test_case('div, =Test', '<div> =Test</div>')

        # Test parentheses and functions as dynamic variables
        test_case('div attr=func(test("test")) Test', '<div attr="${func(test("test"))}">Test</div>')

        result = '<div attr="${func(test())}">${Test}</div>'
        test_case('div (attr=func(test()))= Test', result)

        result = '<div attr="${func(test())}" attr2="${test()}">${Test}</div>'
        test_case('div( attr=func(test()) attr2=test() )= Test', result)

        result = '<div attr="${func(test())}" ${(test()) and \'attr2="attr2"\' or \'\'|n}>${Test}</div>'
        test_case('div( attr=func(test()) attr2=test()? )= Test', result)


    def test_multiline_extract_slim_line(self):
        def test_case(template, result):
            """Use files for multiline test cases"""
            template = l.enumerate_source(self.get_file_contents(template))
            result = l.enumerate_source(self.get_file_contents(result))
            for lineno, line in template:
                if line.strip():
                    _, result_line = result.next()
                    line, close_buf, _, __ = l.extract_slim_line(line, template)
                    self.assertEqual(line + close_buf, result_line.rstrip())

        test_case('slim_multiline_tag_test.html', 'slim_multiline_tag_result.html')


    def test_parse_markdown(self):
        source = self.get_file_contents('markdown_test.html')
        source = l.enumerate_source(source)
        _, line = source.next()
        result = self.get_file_contents('markdown_result.html')
        data, _, __, ___ = l.parse_markup_languages(0, '', l.PARSE_EXTENSION_LANGUAGES_RE.match(line), source)
        self.assertEqual(data.strip(), result.strip())


    def test_parse_rst(self):
        source = self.get_file_contents('reST_test.html')
        source = l.enumerate_source(source)
        _, line = source.next()
        result = self.get_file_contents('reST_result.html')
        data, _, __, ___ = l.parse_markup_languages(0, '', l.PARSE_EXTENSION_LANGUAGES_RE.match(line), source)
        self.assertEqual(data.strip(), result.strip())


    def test_sass(self):
        source = self.get_file_contents('scss_test.html')
        source = l.enumerate_source(source)
        _, line = source.next()
        result = self.get_file_contents('scss_result.html')
        data, _, __, ___ = l.parse_markup_languages(0, '', l.PARSE_EXTENSION_LANGUAGES_RE.match(line), source)
        self.assertEqual(data.strip(), result.strip())
